# Cartoview
[![GitHub stars](https://img.shields.io/github/stars/cartologic/cartoview.svg)](https://github.com/cartologic/cartoview/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/cartologic/cartoview.svg)](https://github.com/cartologic/cartoview/network)
[![Coverage Status](https://coveralls.io/repos/github/cartologic/cartoview/badge.svg?branch=master&service=github)](https://coveralls.io/github/cartologic/cartoview?branch=master&service=github)
[![Build Status](https://travis-ci.org/cartologic/cartoview.svg?branch=master)](https://travis-ci.org/cartologic/cartoview)
[![GitHub license](https://img.shields.io/github/license/cartologic/cartoview.svg)](https://github.com/cartologic/cartoview/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/cartologic/cartoview.svg)](https://github.com/cartologic/cartoview/issues)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/cartologic/cartoview.svg?style=social)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fcartologic%2Fcartoview)
## Quick Start
```
git clone -b cartoview2 --single-branch https://github.com/cartologic/cartoview.git
cd cartoview
virtualenv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
> You must adjust the Database settings in settings > base.py - or create a local settings file
```python
python manage.py createcachetable
python manage.py migrate
python manage.py loaddata initial_groups.json
python manage.py loaddata initial_users.json

```
> run server
```python
python manage.py runserver
```

---
## Additonal Info
![Contrib](https://img.shields.io/github/contributors/cartologic/cartoview_2.svg)
![Languages](https://img.shields.io/github/languages/top/cartologic/cartoview_2.svg)
![License](https://img.shields.io/github/license/cartologic/cartoview_2.svg)