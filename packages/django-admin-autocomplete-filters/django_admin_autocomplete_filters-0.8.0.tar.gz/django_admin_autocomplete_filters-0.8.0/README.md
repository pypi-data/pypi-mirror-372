[![PyPI version](https://badge.fury.io/py/django-admin-autocomplete-filters.svg?icon=si%3Apython)](https://badge.fury.io/py/django-admin-autocomplete-filters)
[![Tests](https://github.com/Barsoomx/django-admin-autocomplete-filters/actions/workflows/tests.yml/badge.svg)](https://github.com/Barsoomx/django-admin-autocomplete-filters/actions/workflows/tests.yml)
[![Ruff](https://img.shields.io/badge/lint-ruff-46a2f1.svg)](https://github.com/astral-sh/ruff)


Django Admin Autocomplete Filters
=================================
Maintained continuation of the [original project by Farhan Khan](https://github.com/farhan0581/django-admin-autocomplete-filter)

This fork modernizes packaging (PEP 621), adds CI, and supports Django 4.2–5.2 and Python 3.10+.

A simple Django app to render list filters in django admin using an autocomplete widget. This app is heavily inspired by [dal-admin-filters.](https://github.com/shamanu4/dal_admin_filters)


Overview:
---------

Django comes preshipped with an admin panel which is a great utility to create quick CRUD's.

Version 2.0 came with a much needed [`autocomplete_fields`](https://docs.djangoproject.com/en/2.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.autocomplete_fields "autocomplete_fields") property which uses a select2 widget to load the options asynchronously.  We leverage this in `django-admin-list-filter`.



Requirements:
-------------

- Django >= 4.2
- Python >= 3.10

Supported Versions
------------------
- Python: 3.10, 3.11, 3.12
- Django: 4.2, 5.0, 5.1, 5.2

See the CI badge for the full matrix.


Features:
-------------

* Custom search view/endpoint ([more details](#functionality-to-provide-custom-view-for-search))
* `list_filter` Filter Factory support ([more details](#shortcut-for-creating-filters))
* Custom widget text ([more details](#customizing-widget-text))
* Support for [Grappelli](https://grappelliproject.com/)


Installation:
-------------

You can install it via pip or poetry.  To get the latest version clone this repo.

```shell
pip install django-admin-autocomplete-filters
```
or
```shell
poetry add django-admin-autocomplete-filters@latest
```

Add `admin_auto_filters` to your `INSTALLED_APPS` inside settings.py of your project.

Breaking Changes compared to original project:
----------------

- CustomSearchView registration (Django 4.2+): pass the admin site instead of a model admin instance. See examples below.
  - Before: `CustomSearchView.as_view(model_admin=self)`
  - Now: `CustomSearchView.as_view(admin_site=self.admin_site)`
  - Rationale: the view uses Django’s `process_request()` to infer the target model admin from query params and performs core permission/validation checks. The admin site wrapper (`self.admin_site.admin_view(...)`) continues to enforce staff/CSRF safeguards.


Usage:
------

Let's say we have following models:
```python
from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=128)

class Album(models.Model):
    name = models.CharField(max_length=64)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    cover = models.CharField(max_length=256, null=True, default=None)
```

And you would like to filter results in `AlbumAdmin` on the basis of `artist`.  You need to define `search fields` in `Artist` and then define filter like this:

```python
from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilter


class ArtistFilter(AutocompleteFilter):
    title = 'Artist' # display title
    field_name = 'artist' # name of the foreign key field


class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['name'] # this is required for django's autocomplete functionality
    # ...


class AlbumAdmin(admin.ModelAdmin):
    list_filter = [ArtistFilter]
    # ...
```

After following these steps you may see the filter as:

![](admin_auto_filters/media/screenshot1.png)

![](admin_auto_filters/media/screenshot2.png)

Release Process
---------------
- Bump `admin_auto_filters.__version__` and update `CHANGELOG.md`.
- Ensure CI is green on `main`.
- Create a tag `vX.Y.Z` and push; the GitHub Actions workflow will build and publish to PyPI via trusted publishing.

Contributing
------------
See `CONTRIBUTING.md` for local setup, linting, typing, tests, and pre-commit hooks.


Functionality to provide a custom view for search:
--------------------------------------------------

You can also register your custom view instead of using Django admin's `search_results` to control the results in the autocomplete.
For this you will need to create your custom view and register the URL in your admin class as shown below:
In your `views.py`/`admin.py`/'filters.py':

```python
from admin_auto_filters.views import AutocompleteJsonView
from django.contrib import admin
from django.urls import path

from django.shortcuts import reverse
from admin_auto_filters.filters import AutocompleteFilter


class ArtistFilter(AutocompleteFilter):
    title = 'Artist'
    field_name = 'artist'

    def get_autocomplete_url(self, request, model_admin):
        return reverse('admin:custom_search')


class CustomSearchView(AutocompleteJsonView):
    def get_queryset(self):
        """
           your custom logic goes here.
        """
        queryset = super().get_queryset()
        queryset = queryset.order_by('name')
        return queryset


class AlbumAdmin(admin.ModelAdmin):
    list_filter = [
        ArtistFilter,
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
            'custom_search/', self.admin_site.admin_view(CustomSearchView.as_view(admin_site=self.admin_site)), name='custom_search'
            ),
        ]
        return custom_urls + urls
```


Shortcut for creating filters:
------------------------------

It's also possible to use the `AutocompleteFilterFactory` shortcut to create
filters on the fly, as shown below. Nested relations are supported too, with
no need to specify the model.

```python
from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory


class AlbumAdmin(admin.ModelAdmin):
    list_filter = [
        AutocompleteFilterFactory('Artist', 'artist', 'admin:custom_search', True)
    ]

    def get_urls(self):
        """As above..."""
```


More Examples
-------------

Nested relations and reverse lookups are supported out of the box.

1) Filter a log model by users related through a device

Models:

```python
from django.db import models

class Member(models.Model):
    name = models.CharField(max_length=100)

class Device(models.Model):
    slug = models.CharField(max_length=100)
    members = models.ManyToManyField(Member, related_name='devices', blank=True)

class PingLog(models.Model):
    device = models.ForeignKey(Device, related_name='pings', on_delete=models.CASCADE)
    ip = models.CharField(max_length=64, blank=True, default='')
```

Admin:

```python
from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory
from tests.testapp.models import Member, PingLog

@admin.register(PingLog)
class PingLogAdmin(admin.ModelAdmin):
    list_filter = [
        # Drill-down M2M: filter PingLog by Device.members
        AutocompleteFilterFactory('Member', 'device__members'),
    ]

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    search_fields = ['name']  # required for admin autocomplete
```

2) Filter coupons by redeemers and by bug reports that rewarded them

Models:

```python
from django.db import models

class Coupon(models.Model):
    code = models.CharField('Code', max_length=64, unique=True, blank=True, db_index=True)

class CouponUser(models.Model):
    coupon = models.ForeignKey(Coupon, related_name='users', on_delete=models.DO_NOTHING)
    user = models.ForeignKey('auth.User', related_name='coupons', null=True, on_delete=models.SET_NULL)
    redeemed_at = models.DateTimeField('Used', auto_now_add=True)

class BugReport(models.Model):
    title = models.CharField(max_length=1024)
    reward_coupon = models.ForeignKey(Coupon, on_delete=models.DO_NOTHING, null=True, blank=True)
```

Admin:

```python
from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory
from tests.testapp.models import BugReport, Coupon

@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    search_fields = ['title']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_filter = [
        # Through model to auth.User
        AutocompleteFilterFactory('User', 'users__user'),
        # Reverse FK using default related_query_name 'bugreport'
        AutocompleteFilterFactory('Bug Report', 'bugreport'),
    ]
```

Notes:
- For each remote model you filter by (e.g., `Member`, `BugReport`), its `ModelAdmin` must define `search_fields` so the admin autocomplete endpoint works (Django 4.2+ requirement).
- By default, `AutocompleteFilterFactory` points to the package’s auto-registered admin view, available at `admin:admin-autocomplete`. (otherwise it fails due to `get_limit_choices_to` being required on non-fk Fields). You can override this by specifying a custom view, as shown above.


Customizing widget text
-----------------------

You can customize the text displayed in the filter widget, to use something
other than `str(obj)`. This needs to be configured for both the dropdown
endpoint and the widget itself.

In your `views.py`, override `display_text`:

```python
from admin_auto_filters.views import AutocompleteJsonView


class CustomSearchView(AutocompleteJsonView):

    @staticmethod
    def display_text(obj):
        return obj.my_str_method()

    def get_queryset(self):
        """As above..."""
        ...
```

Then use either of two options to customize the text.

Option one is to specify the form_field in an AutocompleteFilter in your
`admin.py`:

```python
from django import forms
from django.contrib import admin
from django.shortcuts import reverse
from admin_auto_filters.filters import AutocompleteFilter


class FoodChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.my_str_method()


class ArtistFilter(AutocompleteFilter):
    title = 'Artist'
    field_name = 'artist'
    form_field = FoodChoiceField

    def get_autocomplete_url(self, request, model_admin):
        return reverse('admin:custom_search')


class AlbumAdmin(admin.ModelAdmin):
    list_filter = [ArtistFilter]

    def get_urls(self):
        """As above..."""
```

Option two is to use an AutocompleteFilterFactory in your `admin.py`
add a `label_by` argument:

```python
from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory


class AlbumAdmin(admin.ModelAdmin):
    list_filter = [
        AutocompleteFilterFactory('Artist', 'artist', 'admin:custom_search', True, label_by='my_str_method')
    ]

    def get_urls(self):
        """As above..."""
```


Contributing:
------------

This project is a combined effort of a lot of selfless developers who try to make things easier. Your contribution is most welcome.

Please make a pull-request to the branch `master`, make sure your branch does not have any conflicts, and clearly mention the problems or improvements your PR is addressing.

Verify that tests and linting pass in the Pull Request checks.

License:
--------

Django Admin Autocomplete Filter is an Open Source project licensed under the terms of the GNU GENERAL PUBLIC LICENSE.
