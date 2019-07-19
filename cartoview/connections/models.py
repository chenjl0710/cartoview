import jsonfield
from cartoview.log_handler import get_logger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from fernet_fields import EncryptedTextField
from guardian.shortcuts import assign_perm

from . import SUPPORTED_SERVERS
from .utils import HandlerManager

logger = get_logger(__name__)
CONNECTION_PERMISSIONS = (
    ("use_for_read", _("Allow to use for read operations")),
    ("use_for_write", _("Allow to use for write operations")),
)


class BaseConnectionModel(models.Model):
    title = models.CharField(max_length=150, null=False,
                             blank=False, help_text=_("Title"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def to_dict(self):
        return model_to_dict(self)


class Server(BaseConnectionModel):
    SERVER_TYPES = [(s.value, s.title) for s in SUPPORTED_SERVERS]
    server_type = models.CharField(
        max_length=15, choices=SERVER_TYPES, help_text=_("Server Type"))
    url = models.TextField(blank=False, null=False,
                           help_text=_("Base Server URL"), validators=[URLValidator(
                               schemes=['http', 'https', 'ftp', 'ftps', 'postgis'])])
    operations = jsonfield.JSONField(default=dict, blank=True)

    @cached_property
    def server_handler_key(self):
        key = None
        for server in SUPPORTED_SERVERS:
            if server.value == self.server_type:
                key = server.name
        return key

    def handler(self, user_id=None):
        handler_obj = None
        handler_manager = HandlerManager(self.server_type, server=True)
        Handler = handler_manager.get_handler_class_handler()
        if Handler:
            handler_obj = Handler(self.url, self.id, user_id)
        return handler_obj

    def get_user_connections(self, user_id):
        user_connections = self.connections.filter(owner__id=user_id)
        return user_connections

    @property
    def is_alive(self):
        alive = False
        handler = self.handler()
        if handler:
            alive = handler.is_alive
        return alive

    def __str__(self):
        return self.url

    class Meta(BaseConnectionModel.Meta):
        unique_together = ('server_type', 'url',)


class Connection(BaseConnectionModel):
    connection_class_names = (
        'SimpleAuthConnection',
        'TokenAuthConnection',
    )
    BASIC_HANDLER_KEY = "BASIC"
    DIGEST_HANDLER_KEY = "DIGEST"
    TOKEN_HANDLER_KEY = "TOKEN"
    AUTH_TYPES = (
        (BASIC_HANDLER_KEY, _("Basic Authentication")),
        (DIGEST_HANDLER_KEY, _("Digest Authentication")),
        (TOKEN_HANDLER_KEY, _("Token Authentication"))

    )
    auth_type = models.CharField(
        max_length=6, choices=AUTH_TYPES, help_text=_("Authentication Type"))
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="connections")

    class Meta:
        ordering = ('-created_at', '-updated_at')
        unique_together = ('server', 'owner',)

    @cached_property
    def credentials(self):
        for conn_class_name in self.connection_class_names:
            try:
                return self.__getattribute__(conn_class_name.lower())
            except eval(conn_class_name).DoesNotExist:
                pass
        return self

    def __str__(self):
        return self.server.url


class SimpleAuthConnection(Connection):
    BASIC_HANDLER_KEY = "BASIC"
    DIGEST_HANDLER_KEY = "DIGEST"
    AUTH_TYPES = (
        (BASIC_HANDLER_KEY, _("Basic Authentication")),
        (DIGEST_HANDLER_KEY, _("Digest Authentication"))
    )
    username = models.CharField(
        max_length=200, null=False, blank=False, help_text=_("Server Type"))
    password = EncryptedTextField(
        null=False, blank=False, help_text=_("User Password"))

    @cached_property
    def session(self):
        handler_manager = HandlerManager(self.auth_type)
        handler = handler_manager.get_handler_class_handler()
        if handler:
            return handler.get_session(self)
        else:
            logger.error("anonymous session")
            return handler_manager.anonymous_session

    def __str__(self):
        return self.username

    class Meta:
        permissions = CONNECTION_PERMISSIONS


class TokenAuthConnection(Connection):
    token = models.TextField(null=False, blank=False,
                             help_text=_("Access Token"))
    prefix = models.CharField(
        max_length=60, null=False, blank=True, default="Bearer",
        help_text=_("Authentication Header Value Prefix"))

    def __str__(self):
        return "<{}:{}>".format(self.prefix, self.token)

    @cached_property
    def session(self):
        handler_manager = HandlerManager(TokenAuthConnection.TOKEN_HANDLER_KEY)
        handler = handler_manager.get_handler_class_handler()
        if handler:
            return handler.get_session(self)
        else:
            logger.error("anonymous session")
            return handler_manager.anonymous_session

    class Meta:
        permissions = CONNECTION_PERMISSIONS


@receiver(post_save, sender=TokenAuthConnection)
@receiver(post_save, sender=SimpleAuthConnection)
def connection_post_save(sender, instance, created, **kwargs):
    if created and instance.owner and \
            instance.owner.username != settings.ANONYMOUS_USER_NAME:
        users = get_user_model().objects.filter(is_superuser=True,)
        if instance.owner:
            users = users.union(get_user_model().objects.filter(
                username=instance.owner.username))
        for user in users:
            for perm in CONNECTION_PERMISSIONS:
                assign_perm(perm[0], user, instance)
