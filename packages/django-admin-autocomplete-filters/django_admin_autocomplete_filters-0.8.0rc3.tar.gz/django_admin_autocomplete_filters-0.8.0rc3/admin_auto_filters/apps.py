from collections.abc import Sequence
from typing import TYPE_CHECKING

from django.apps import AppConfig

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver  # noqa: F401


class AdminAutoFiltersConfig(AppConfig):
    name = 'admin_auto_filters'

    def ready(self) -> None:  # Django 4.2+ lifecycle hook
        # Defer imports to avoid app registry and import-order issues
        from django.contrib import admin
        from django.urls import path

        from . import ADMIN_AUTOCOMPLETE_VIEW_SLUG
        from .views import AutocompleteJsonView

        site = admin.site

        # Prevent multiple patches during autoreload or multiple app loads
        if getattr(site, '_admin_auto_filters_urls_patched', False):
            return

        original_get_urls = site.get_urls

        def get_urls() -> Sequence['URLResolver | URLResolver | URLPattern | URLPattern']:
            urls = original_get_urls()
            extra = [
                path(
                    f'{ADMIN_AUTOCOMPLETE_VIEW_SLUG}/',
                    site.admin_view(AutocompleteJsonView.as_view(admin_site=site)),
                    name=ADMIN_AUTOCOMPLETE_VIEW_SLUG,
                ),
            ]
            # Prepend so our route takes precedence if names collide (they shouldn't)
            return extra + urls

        site.get_urls = get_urls  # type: ignore[assignment]
        site._admin_auto_filters_urls_patched = True  # type: ignore[attr-defined]
