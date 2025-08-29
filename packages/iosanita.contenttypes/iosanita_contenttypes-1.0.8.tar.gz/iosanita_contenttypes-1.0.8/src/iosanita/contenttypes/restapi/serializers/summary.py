from collective.taxonomy import PATH_SEPARATOR
from iosanita.contenttypes.indexers.taxonomies import get_taxonomy_vocab
from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from iosanita.contenttypes.interfaces.punto_di_contatto import IPuntoDiContatto
from plone import api
from plone.app.contenttypes.interfaces import INewsItem
from plone.indexer.interfaces import IIndexableObject
from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from plone.restapi.interfaces import ISerializeToJsonSummary
from redturtle.volto.restapi.serializer.summary import DefaultJSONSummarySerializer
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import logging


logger = logging.getLogger(__name__)


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    def default_metadata_fields(self):
        """
        Force always return some metadata
        """
        return {
            "parliamo_di_metadata",
            "a_chi_si_rivolge_tassonomia_metadata",
            "id",
            "tipologia_notizia",
            "tipologia_notizia_metadata",
            "start",
            "end",
            "recurrence",
            "whole_day",
            "open_end",
            "street",
            "zip_code",
            "city",
            "provincia",
            "geolocation",
            "servizio_attivo",
            "parent",
            "Date",
            "incarico_metadata",
            "modified",
        }


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IIosanitaContenttypesLayer)
class IOSanitaJSONSummarySerializer(DefaultJSONSummarySerializer):
    def __call__(self, force_all_metadata=False):
        """
        Customize type_title for News Items
        """
        data = super().__call__(force_all_metadata=force_all_metadata)
        obj = None
        if self.is_get_call() or data["@type"] == "Bando":
            obj = self.get_real_object()
        if self.is_get_call():
            data["has_children"] = self.has_children(obj=obj)
        if data["@type"] == "News Item":
            data["type_title"] = self.get_news_type_title()
        if data["@type"] == "Bando":
            metadata_fields = self.metadata_fields()
            if "bando_state" in metadata_fields or self.show_all_metadata_fields:
                data["bando_state"] = self.get_bando_state(obj=obj)
        return data

    def get_real_object(self):
        try:
            return self.context.getObject()
        except AttributeError:
            return self.context

    def get_news_type_title(self):
        tipologia_notizia = getattr(self.context, "tipologia_notizia")
        if tipologia_notizia:
            tipologia_notizia = tipologia_notizia[0]
            taxonomy_vocab = get_taxonomy_vocab("tipologia_notizia")
            taxonomy_value = taxonomy_vocab.inv_data.get(tipologia_notizia, None)
            if taxonomy_value:
                return taxonomy_value.replace(PATH_SEPARATOR, "", 1)
        return "Notizia"

    def is_get_call(self):
        if self.request.get("other", {}).get("method", "") == "GET":
            return True
        if getattr(self.request, "environ", {}).get("REQUEST_METHOD", "") == "GET":
            return True
        return False

    def has_children(self, obj):
        """
        Return info if the item has at least one child
        """
        try:
            if obj.aq_base.keys():
                return True
        except AttributeError:
            return False
        return False

    def get_bando_state(self, obj):
        bando_view = api.content.get_view(
            "bando_view", context=obj, request=self.request
        )
        return bando_view.getBandoState()


@implementer(ISerializeToJsonSummary)
@adapter(IPuntoDiContatto, IIosanitaContenttypesLayer)
class PuntoDiContattoJSONSummarySerializer(IOSanitaJSONSummarySerializer):
    def __call__(self):
        data = super().__call__()

        data["contatti"] = getattr(self.context, "contatti", [])

        return data


@implementer(ISerializeToJsonSummary)
@adapter(INewsItem, IIosanitaContenttypesLayer)
class NewsItemJSONSummarySerializer(IOSanitaJSONSummarySerializer):
    def __call__(self):
        data = super().__call__()

        catalog = api.portal.get_tool(name="portal_catalog")
        adapter = queryMultiAdapter((self.context, catalog), IIndexableObject)

        for metadata in ["tipologia_notizia", "tipologia_notizia_metadata"]:
            data[metadata] = getattr(adapter, metadata, data.get(metadata, ""))
        return data
