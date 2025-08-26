from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from django import VERSION as DJANGO_VERSION
from django import forms
from django.contrib import admin
from django.contrib.admin import utils as admin_utils
from django.contrib.admin.widgets import (
    AutocompleteSelect as AutocompleteSelectBase,
)
from django.contrib.admin.widgets import (
    AutocompleteSelectMultiple as AutocompleteSelectMultipleBase,
)
from django.db.models.constants import LOOKUP_SEP  # this is '__'
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.fields.related_descriptors import (
    ManyToManyDescriptor,
    ReverseManyToOneDescriptor,
)
from django.forms import widgets as forms_widgets
from django.forms.widgets import Media
from django.urls import reverse

from . import ADMIN_AUTOCOMPLETE_VIEW_NAME

# Django does not expose precise typing for these in stubs
MEDIA_TYPES: tuple[str, ...] = ('css', 'js')
media_property = forms_widgets.media_property  # type: ignore[attr-defined]


class AutocompleteSelectMixin:
    def __init__(
        self,
        rel: Any,
        admin_site: Any,
        attrs: dict[str, Any] | None = None,
        choices: Sequence[Any] = (),
        using: str | None = None,
        custom_url: str | None = None,
    ) -> None:
        self.custom_url: str | None = custom_url
        super().__init__(rel, admin_site, attrs, choices, using)  # type: ignore[call-arg]

    def get_url(self) -> str:
        return self.custom_url if self.custom_url else super().get_url()  # type: ignore[misc]


class AutocompleteSelect(AutocompleteSelectMixin, AutocompleteSelectBase):
    pass


class AutocompleteSelectMultiple(
    AutocompleteSelectMixin,
    AutocompleteSelectMultipleBase,
):
    pass


class AutocompleteFilterBase(admin.SimpleListFilter):
    template = 'django-admin-autocomplete-filter/autocomplete-filter.html'
    title = ''
    field_name = ''
    field_pk = 'pk'
    use_pk_exact = True
    is_placeholder_title = False
    widget_attrs: dict[str, Any] = {}
    rel_model = None
    parameter_name = None
    form_field: type[forms.Field] | None = None
    widget_cls: type[Any] | None = None

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'django-admin-autocomplete-filter/js/autocomplete_filter_qs.js',
        )
        css = {
            'screen': ('django-admin-autocomplete-filter/css/autocomplete-fix.css',),
        }

    def __init__(self, request: Any, params: dict[str, Any], model: Any, model_admin: Any) -> None:
        if self.parameter_name is None:
            self.parameter_name = self.generate_parameter_name()
        super().__init__(request, params, model, model_admin)

        if self.rel_model:
            model = self.rel_model

        if DJANGO_VERSION >= (3, 2):
            remote_field = model._meta.get_field(self.field_name)
        else:
            remote_field = model._meta.get_field(self.field_name).remote_field

        assert self.widget_cls is not None, 'widget_cls must be defined'
        widget = self.widget_cls(
            remote_field,
            model_admin.admin_site,
            custom_url=self.get_autocomplete_url(request, model_admin),
        )
        form_field = self.get_form_field()
        assert form_field is not None, 'form_field or get_form_field() must be defined'
        field = form_field(
            queryset=self.get_queryset_for_field(model, self.field_name),
            widget=widget,
            required=False,
        )

        # Django 4.2+ exposes this in django.contrib.admin.utils
        self.may_have_duplicates: bool = admin_utils.lookup_spawns_duplicates(
            model_admin.model._meta,
            self.parameter_name,
        )
        self._add_media(model_admin, widget)

        attrs = self.widget_attrs.copy()
        attrs['id'] = f'id-{self.parameter_name}-dal-filter'
        if self.is_placeholder_title:
            # Upper case letter P as dirty hack for bypass django2 widget force placeholder value as empty string ("")
            attrs['data-Placeholder'] = self.title
        value = self.used_parameters.get(self.parameter_name, '')
        if value:
            value = self.normalize_value(str(value))
        self.rendered_widget = field.widget.render(
            name=self.parameter_name,
            value=value,
            attrs=attrs,
        )

    @staticmethod
    def get_queryset_for_field(model: Any, name: str) -> Any:
        try:
            field_desc = getattr(model, name)
        except AttributeError:
            field_desc = model._meta.get_field(name)
        if isinstance(field_desc, ManyToManyDescriptor):
            related_model = field_desc.rel.related_model if field_desc.reverse else field_desc.rel.model
        elif isinstance(field_desc, ReverseManyToOneDescriptor):
            related_model = field_desc.rel.related_model  # look at field_desc.related_manager_cls()?
        elif isinstance(field_desc, ForeignObjectRel):
            # includes ManyToOneRel, ManyToManyRel
            # also includes OneToOneRel - not sure how this would be used
            related_model = field_desc.related_model
        elif hasattr(field_desc, 'descriptor'):
            return field_desc.descriptor.get_queryset()
        else:
            # primarily for ForeignKey/ForeignKeyDeferredAttribute
            # also includes ForwardManyToOneDescriptor, ForwardOneToOneDescriptor, ReverseOneToOneDescriptor
            return field_desc.get_queryset()
        # Handle self-referential relations reported as string
        if isinstance(related_model, str) and related_model == 'self':
            return model._default_manager.get_queryset()
        return related_model._default_manager.get_queryset()

    def get_form_field(self) -> Any:
        """Return the type of form field to be used."""
        return self.form_field

    def _add_media(self, model_admin: Any, widget: Any) -> None:
        if not hasattr(model_admin, 'Media'):
            model_admin.__class__.Media = type('Media', (object,), {})
            model_admin.__class__.media = media_property(model_admin.__class__)

        def _get_media(obj: Any) -> Media:
            return Media(media=getattr(obj, 'Media', None))

        media = _get_media(model_admin) + widget.media + _get_media(AutocompleteFilterBase) + _get_media(self)

        for name in MEDIA_TYPES:
            setattr(model_admin.Media, name, getattr(media, '_' + name))

    def has_output(self) -> bool:
        return True

    def lookups(self, request: Any, model_admin: Any) -> tuple:
        return ()

    def generate_parameter_name(self) -> str:
        return self.field_name

    @classmethod
    def normalize_value(cls, value: str) -> Any:
        return value

    def queryset(self, request: Any, queryset: Any) -> Any:
        value = self.value()
        if not value:
            return queryset

        if self.may_have_duplicates:
            queryset = queryset.distinct()

        return queryset.filter(**{self.parameter_name: self.normalize_value(value)})

    def get_autocomplete_url(self, request: Any, model_admin: Any) -> str | None:
        """
        Hook to specify your custom view for autocomplete,
        instead of default django admin's search_results.
        """
        return None


class AutocompleteFilter(AutocompleteFilterBase):
    form_field = forms.ModelChoiceField
    widget_cls = AutocompleteSelect

    def generate_parameter_name(self) -> str:
        parameter_name = super().generate_parameter_name()
        if self.use_pk_exact:
            parameter_name += f'__{self.field_pk}__exact'
        return parameter_name


class AutocompleteFilterMultiple(AutocompleteFilterBase):
    form_field = forms.ModelMultipleChoiceField
    widget_cls = AutocompleteSelectMultiple

    def generate_parameter_name(self) -> str:
        parameter_name = super().generate_parameter_name()
        if self.use_pk_exact:
            parameter_name += f'__{self.field_pk}'
        parameter_name += '__in'
        return parameter_name

    @classmethod
    def normalize_value(cls, value: str) -> Sequence[str]:
        return value.split(',')


def generate_choice_field(label_item: Callable[[Any], str] | str) -> type[forms.ModelChoiceField]:
    """
    Create a ModelChoiceField variant with a modified label_from_instance.
    Note that label_item can be a callable, or a model field, or a model callable.
    """

    class LabelledModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj: Any) -> str:
            if callable(label_item):
                value = label_item(obj)
            elif hasattr(obj, str(label_item)):
                attr = getattr(obj, label_item)
                if callable(attr):
                    value = attr()
                else:
                    value = attr
            else:
                raise ValueError(f'Invalid label_item specified: {str(label_item)}')
            return value

    return LabelledModelChoiceField


def _get_rel_model(model: Any, parameter_name: str) -> Any | None:
    """
    A way to calculate the model for a parameter_name that includes LOOKUP_SEP.
    """
    field_names = str(parameter_name).split(LOOKUP_SEP)
    if len(field_names) == 1:
        return None
    else:
        rel_model = model
        for name in field_names[:-1]:
            rel_model = rel_model._meta.get_field(name).related_model
        return rel_model


def AutocompleteFilterFactory(  # noqa: N802 - keep public API name
    title: str,
    base_parameter_name: str,
    viewname: str | None = ADMIN_AUTOCOMPLETE_VIEW_NAME,
    use_pk_exact: bool = False,
    label_by: Callable[[Any], str] | str = str,
) -> type[AutocompleteFilterBase]:
    """
    An autocomplete widget filter with a customizable title. Use like this:
        AutocompleteFilterFactory('My title', 'field_name')
        AutocompleteFilterFactory('My title', 'fourth__third__second__first')
    Be sure to include distinct in the model admin get_queryset() if the second form is used.
    Assumes: parameter_name == f'fourth__third__second__{field_name}'
        * title: The title for the filter.
        * base_parameter_name: The field to use for the filter.
        * viewname: The name of the custom AutocompleteJsonView URL to use, if any.
        * use_pk_exact: Whether to use '__pk__exact' in the parameter name when possible.
        * label_by: How to generate the static label for the widget - a callable, the name
          of a model callable, or the name of a model field.
    """

    class NewMetaFilter(type(AutocompleteFilter)):  # type: ignore[misc]
        """A metaclass for an autogenerated autocomplete filter class."""

        def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> Any:
            super_new = super().__new__(cls, name, bases, attrs)
            super_new.use_pk_exact = use_pk_exact
            field_names = str(base_parameter_name).split(LOOKUP_SEP)
            super_new.field_name = field_names[-1]
            super_new.parameter_name = base_parameter_name
            if len(field_names) <= 1 and super_new.use_pk_exact:
                super_new.parameter_name += f'__{super_new.field_pk}__exact'
            return super_new

    class NewFilter(AutocompleteFilter, metaclass=NewMetaFilter):
        """An autogenerated autocomplete filter class."""

        def __init__(self, request: Any, params: dict[str, Any], model: Any, model_admin: Any) -> None:
            self.rel_model = _get_rel_model(model, base_parameter_name)
            self.form_field = generate_choice_field(label_by)
            super().__init__(request, params, model, model_admin)
            self.title = title

        def get_autocomplete_url(self, request: Any, model_admin: Any) -> str | None:
            if viewname:
                return reverse(viewname)

            # If viewname is not set (set to None or '' explicitly),
            # fallback to default Django admin `get_autocomplete_url`;
            return super().get_autocomplete_url(request, model_admin)

    return NewFilter
