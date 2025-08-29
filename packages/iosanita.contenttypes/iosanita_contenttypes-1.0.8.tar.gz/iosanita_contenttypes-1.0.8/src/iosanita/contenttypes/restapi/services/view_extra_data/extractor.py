# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from iosanita.contenttypes.interfaces import IoSanitaViewExtraData
from iosanita.contenttypes.interfaces.persona import IPersona
from iosanita.contenttypes.interfaces.servizio import IServizio
from iosanita.contenttypes.interfaces.settings import IIoSanitaContenttypesSettings
from iosanita.contenttypes.interfaces.struttura import IStruttura
from iosanita.contenttypes.interfaces.unita_organizzativa import IUnitaOrganizzativa
from plone import api
from plone.restapi.interfaces import ISerializeToJsonSummary
from redturtle.bandi.interfaces.bando import IBando
from zc.relation.interfaces import ICatalog
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission


LIMIT = 25


@implementer(IoSanitaViewExtraData)
@adapter(Interface, Interface)
class ViewExtraDataExtractor(object):
    reference_id = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """
        By default does not return anything
        """
        return {}

    def get_back_references(self, reference_id):
        """
        Return a mapping of back references splitted by portal_type.
        News Items are sorted by date, other are sorted by title
        """

        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        relations = []
        for ref_id in reference_id:
            relations.extend(
                catalog.findRelations(
                    {
                        "to_id": intids.getId(aq_inner(self.context)),
                        "from_attribute": ref_id,
                    }
                )
            )
        data = {}
        for rel in relations:
            obj = intids.queryObject(rel.from_id)
            if obj is None:
                continue
            portal_type = obj.portal_type
            if checkPermission("zope2.View", obj):
                if portal_type not in data:
                    data[portal_type] = []
                summary = getMultiAdapter(
                    (obj, getRequest()), ISerializeToJsonSummary
                )()
                if summary not in data[portal_type]:
                    data[portal_type].append(summary)
        for portal_type, values in data.items():
            if portal_type == "News Item":
                data[portal_type] = sorted(
                    values, key=lambda k: k["Date"], reverse=True
                )[:LIMIT]
            else:
                data[portal_type] = sorted(values, key=lambda k: k["title"])[:LIMIT]
        return data


@implementer(IoSanitaViewExtraData)
@adapter(IServizio, Interface)
class ViewExtraDataExtractorServizio(ViewExtraDataExtractor):
    def __call__(self):
        """
        Servizio can also be referenced by a custom field
        """

        data = self.get_back_references(reference_id=["servizio_correlato"])

        data.update(
            self.get_back_references(reference_id=["servizio_procedura_riferimento"])
        )
        return {"back-references": data}


@implementer(IoSanitaViewExtraData)
@adapter(IStruttura, Interface)
class ViewExtraDataExtractorStruttura(ViewExtraDataExtractor):
    def __call__(self):
        """ """

        data = self.get_back_references(reference_id=["struttura_correlata"])
        view_related_people = api.portal.get_registry_record(
            "enable_struttura_related_people", interface=IIoSanitaContenttypesSettings
        )
        if view_related_people:
            data.update(
                self.get_back_references(
                    reference_id=["struttura_ricevimento", "struttura_in_cui_opera"]
                )
            )
        return {"back-references": data}


@implementer(IoSanitaViewExtraData)
@adapter(IUnitaOrganizzativa, Interface)
class ViewExtraDataExtractorUnitaOrganizzativa(ViewExtraDataExtractor):
    def __call__(self):
        """ """
        return {
            "back-references": self.get_back_references(
                reference_id=["uo_correlata", "struttura_correlata"]
            )
        }


@implementer(IoSanitaViewExtraData)
@adapter(IPersona, Interface)
class ViewExtraDataExtractorPersona(ViewExtraDataExtractor):
    def __call__(self):
        data = self.get_back_references(reference_id=["persona_correlata"])

        # append additional references
        data.update(
            {
                "responsabile": self.get_back_references(
                    reference_id=["responsabile_correlato"]
                ),
                "personale": self.get_back_references(
                    reference_id=["personale_correlato"]
                ),
            }
        )
        return {"back-references": data}


@implementer(IoSanitaViewExtraData)
@adapter(IBando, Interface)
class ViewExtraDataExtractorBando(ViewExtraDataExtractor):
    def __call__(self):
        bando_view = self.context.restrictedTraverse("bando_view")
        return {
            "approfondimenti": self.get_approfondimenti(),
            "stato_bando": bando_view.getBandoState(),
        }

    def get_approfondimenti(self):
        """ """
        folders = self.context.listFolderContents(
            contentFilter={"portal_type": "Bando Folder Deepening"}
        )

        result = []

        for folder in folders:
            if folder.exclude_from_nav:
                continue
            folder_data = getMultiAdapter(
                (folder, self.request), ISerializeToJsonSummary
            )()
            items = []
            for child in folder.listFolderContents():
                if child.exclude_from_nav:
                    continue
                child_data = getMultiAdapter(
                    (child, self.request), ISerializeToJsonSummary
                )()
                # if child.portal_type == "Link":
                #     url = getattr(child, "remoteUrl", "") or ""

                #     if url.startswith("${portal_url}/resolveuid/"):
                #         uid = url.replace("${portal_url}/", "")
                #         child_data["@id"] = uid_to_url(uid)
                items.append(child_data)
            if items:
                folder_data["items"] = items
                result.append(folder_data)
        return result
