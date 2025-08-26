from __future__ import annotations

from typing import Any

from django.contrib.admin.views.autocomplete import AutocompleteJsonView as Base


class AutocompleteJsonView(Base):
    """Overriding django admin's AutocompleteJsonView"""

    model_admin: Any = None
    source_field: Any = None

    @staticmethod
    def display_text(obj: Any) -> str:
        """
        Hook to specify means for converting object to string for endpoint.
        """
        return str(obj)

    def serialize_result(self, obj: Any, to_field_name: str) -> dict[str, str]:
        return {'id': str(getattr(obj, to_field_name)), 'text': self.display_text(obj)}

    def get_queryset(self) -> Any:
        """Return queryset based on ModelAdmin.get_search_results()."""
        qs = self.model_admin.get_queryset(self.request)
        if hasattr(self.source_field, 'get_limit_choices_to'):
            qs = qs.complex_filter(self.source_field.get_limit_choices_to())
        qs, search_use_distinct = self.model_admin.get_search_results(self.request, qs, self.term)
        if search_use_distinct:
            qs = qs.distinct()
        return qs
