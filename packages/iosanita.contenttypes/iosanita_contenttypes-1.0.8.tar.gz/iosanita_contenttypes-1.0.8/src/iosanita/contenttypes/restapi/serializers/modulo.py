# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from iosanita.contenttypes.interfaces.modulo import IModulo
from iosanita.contenttypes.restapi.serializers.summary import (
    DefaultJSONSummarySerializer,
)
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.schema import getFields


@implementer(ISerializeToJsonSummary)
@adapter(IModulo, IIosanitaContenttypesLayer)
class SerializeModuloToJsonSummary(DefaultJSONSummarySerializer):
    def __call__(self, **kwargs):
        summary = super().__call__(**kwargs)
        fields = [
            "file",
            "formato_alternativo_1",
            "formato_alternativo_2",
        ]
        for schema in iterSchemata(self.context):
            for name, field in getFields(schema).items():
                if name not in fields:
                    continue

                # serialize the field
                serializer = queryMultiAdapter(
                    (field, self.context, self.request), IFieldSerializer
                )
                value = serializer()
                summary[name] = value
        return summary
