# ICHEC Django Core #

This is a set of Django application building blocks and utilities for use at ICHEC. They can be used to build and test other Django apps.

Useful elements include:

* A common collection of Django Settings for use in consuming projects, intended to provide secure defaults:

``` python
from ichec_django_core import settings

MY_DJANGO_SETTING = settings.MY_DJANGO_SETTING
```

* Core functionality for authentication, including:
  * models of portal members and organizations 
  * OpenID Connect integration

* Functionality for handling user provided media and subsequent access in a secure and performant way

* Tested, re-usable components

# Usage #

This guide assumes you are comfortable building a basic Django app - if not you should create one first following the [Getting Started with Django guide](https://www.djangoproject.com/start/).

You can include this project `ichec-django-core` as a Python package in your `requirements.txt` or `pyproject.toml`.

## Example project ##

The [app](./app) directory is an example use of the module to build a minimal portal. Note that there's not much code involved, `ichec-django-core` has enough defaults to get somethings basic running.

You are encoouraged to try it our before proceeding with the rest of the guide. You can do:

``` shell
git clone https://git.ichec.ie/platform-engineering/ichec-django-core.git
python -m venv .venv
source .venv/bin/activate
pip install .
source infra/set_dev_environment.sh
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py runserver
```

and open http:://localhost:8000 in your browser to check it out.


## Including default settings ##

The module will define some sensible default Django settings, leaving you to only define a few for a basic portal. See the sample settings in the [app](./app) directory:

``` python
from pathlib import Path

from ichec_django_core import settings
from ichec_django_core.settings import *

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"

TEMPLATES = settings.get_templates(BASE_DIR)
DATABASES = settings.get_databases(BASE_DIR)

STATIC_ROOT = settings.get_static_root(BASE_DIR)
MEDIA_ROOT = settings.get_media_root(BASE_DIR)
```

Of course - if you need something different from the default `ichec-django-core` values you can override them in your own settings file.

The settings values in `ichec-django-core` come from evironment variables. It is most convenient to keep a development version of these variables in a text file and then load them into your shell environment when working with the server. The [infra](./infra) directory shows an example of how to do this. We keep variables in a `dev.txt` file and use the shell script `set_dev_environment.sh` to load them using:

``` shell
source infra/set_dev_environment.sh
```

. In production, these values may be passed into a container using a `.env` file or via the container orchestration environment (e.g. compose files).

## Including Urls ##

The module comes with some useful default Django and Django Rest Framework (DRF) default views, such as for admin and user and organisation management.

To include them, using the [app](./app) directory as an example, you can do:

``` python
from django.urls import include, path
from django.views.generic.base import RedirectView
from rest_framework import routers

from ichec_django_core.urls import register_drf_views

router = routers.DefaultRouter()
register_drf_views(router)

urlpatterns = [
    path("api/", include(router.urls)),
    path("", include("ichec_django_core.urls")),
    path("", RedirectView.as_view(url='/api', permanent=True), name='index'),
]
```

This is a slightly non-standard approach for Django apps. Here we are creating a top-level DRF router and registering the `ichec_django_core` DRF API views with it. This approach allows for easier composition of DRF views from different modules.

We are using the standard Django approach to include the Django Views, namely ` path("", include("ichec_django_core.urls")),`.

The remaining view is a boilerplate redirect since the example doesn't come with an 'index.html' template and directs straight to the DRF landing instead.

## Using OpenID Connect ##

The module has basic user managment and authentication built-in, however you likely want this to be handled in a more suitable application or want to include the portal in a Single-Sign-On framework. This can be handled using OAuth 2.0 and OpenID Connect.

To set this up we first need to register our app as a client in an OIDC provider. ICHEC uses Keycloak so will focus on it in the guide, but the module itself is agnostic of the particulars of the provider.

Once the client has been registered you can set the following environment variables:

``` shell
WITH_OIDC=1
OIDC_RP_CLIENT_ID=xxx
OIDC_RP_CLIENT_SECRET=xxx
OIDC_OP_AUTHORIZATION_ENDPOINT=xxx
OIDC_OP_TOKEN_ENDPOINT=xxx
OIDC_OP_USER_ENDPOINT=xxx
OIDC_OP_JWKS_ENDPOINT=xxx
```

using [this guide](https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html) as a reference. You can look at [infra/dev.txt](./infra/dev.txt) as an example if running a local Keycloak provider, just the client ID and secret need to be changed.


# Licensing #

This software is copyright of the Irish Centre for High End Computing (ICHEC). It may be used under the terms of the GNU AGPL version 3 or later, with license details in the included `LICENSE` file. Exemptions are available for Marinerg project partners and possibly others on request.
