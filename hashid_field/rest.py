from django.apps import apps
from django.core import exceptions

from hashids import Hashids
from hashids_cpp import Hashids as Hashids_cpp
from rest_framework import fields, serializers

from hashid_field.conf import settings
from hashid_field.hashid import Hashid


class UnconfiguredHashidSerialField(fields.Field):
    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        raise exceptions.ImproperlyConfigured(
            "The field '{field_name}' on {parent} must be explicitly declared when used with a ModelSerializer".format(
                field_name=field_name, parent=parent.__class__.__name__))


class HashidSerializerMixin(object):
    usage_text = "Must pass a HashidField, HashidAutoField or 'app_label.model.field'"

    def __init__(self, **kwargs):
        self.hashid_salt = kwargs.pop('salt', settings.HASHID_FIELD_SALT)
        self.hashid_min_length = kwargs.pop('min_length', 7)
        self.hashid_alphabet = kwargs.pop('alphabet', Hashids.ALPHABET)
        self.hashid_prefix = kwargs.pop('prefix', None)

        source_field = kwargs.pop('source_field', None)
        if source_field:
            from hashid_field import HashidField, HashidAutoField
            if isinstance(source_field, str):
                try:
                    app_label, model_name, field_name = source_field.split(".")
                except ValueError:
                    raise ValueError(self.usage_text)
                model = apps.get_model(app_label, model_name)
                source_field = model._meta.get_field(field_name)
            elif not isinstance(source_field, (HashidField, HashidAutoField)):
                raise TypeError(self.usage_text)
            self.hashid_salt, self.hashid_min_length, self.hashid_alphabet, self.hashid_prefix = \
                source_field.salt, source_field.min_length, source_field.alphabet, source_field.prefix
        self._hashids = Hashids(salt=self.hashid_salt, min_length=self.hashid_min_length, alphabet=self.hashid_alphabet)
        self._hashids_cpp = Hashids_cpp(self.hashid_salt, self.hashid_min_length, self.hashid_alphabet)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            value = super().to_internal_value(data)
            if isinstance(value, str) and self.hashid_prefix is not None and value.startswith(self.hashid_prefix):
                value = value[len(self.hashid_prefix) + 1:]
            return Hashid(value, hashids=self._hashids, hashids_cpp=self._hashids_cpp)
        except ValueError:
            raise serializers.ValidationError("Invalid id format.")


class HashidSerializerCharField(HashidSerializerMixin, fields.CharField):
    def to_representation(self, value):
        return value.hashid


class HashidSerializerIntegerField(HashidSerializerMixin, fields.IntegerField):
    def to_representation(self, value):
        return value.id

