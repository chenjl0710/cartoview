# Generated by Django 2.2 on 2019-07-24 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='geonode_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
