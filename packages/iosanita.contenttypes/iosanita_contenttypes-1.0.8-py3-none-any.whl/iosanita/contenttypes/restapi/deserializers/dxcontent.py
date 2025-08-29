from copy import deepcopy
from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from iosanita.contenttypes.interfaces import IoSanitaMigrationMarker
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.restapi import _
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson as BaseDeserializer
from plone.restapi.interfaces import IDeserializeFromJson
from zExceptions import BadRequest
from zope.component import adapter
from zope.interface import implementer

import json


@implementer(IDeserializeFromJson)
@adapter(IDexterityContent, IIosanitaContenttypesLayer)
class DeserializeFromJson(BaseDeserializer):
    def __call__(
        self, validate_all=False, data=None, create=False, mask_validation_errors=True
    ):
        if data is None:
            data = json_body(self.request)
        # iosanità validations
        self.validate_data_iosanita(data=data, create=create)

        return super().__call__(
            validate_all=validate_all,
            data=data,
            create=create,
            mask_validation_errors=mask_validation_errors,
        )

    @property
    def mutual_required_msg(self):
        return api.portal.translate(
            _(
                "mutual_required_field_msg",
                default="Compila almeno uno di questi campi.",
            )
        )

    def validate_data_iosanita(self, data, create):
        if IoSanitaMigrationMarker.providedBy(self.request):
            return
        if create:
            portal_type = data.get("@type", "")
        else:
            portal_type = self.context.portal_type
        self.validate_a_chi_si_rivolge(
            portal_type=portal_type, data=data, create=create
        )

        if portal_type == "Event":
            self.validate_event(data=data, create=create)
        if portal_type in ["Struttura", "UnitaOrganizzativa"]:
            self.validate_dove(data=data, create=create)

    def validate_a_chi_si_rivolge(self, portal_type, data, create):
        portal_types = api.portal.get_tool(name="portal_types")
        behaviors = portal_types[portal_type].behaviors

        has_behaviors = False
        for bhv in [
            "iosanita.contenttypes.behavior.a_chi_si_rivolge",
            "collective.taxonomy.generated.a_chi_si_rivolge_tassonomia",
        ]:
            if bhv in behaviors:
                has_behaviors = True
        if not has_behaviors:
            # skip check
            return

        has_a_chi_si_rivolge = self.has_field_value(
            data=data, create=create, field_id="a_chi_si_rivolge", is_block_field=True
        )
        has_a_chi_si_rivolge_tassonomia = self.has_field_value(
            data=data, create=create, field_id="a_chi_si_rivolge_tassonomia"
        )

        if not has_a_chi_si_rivolge and not has_a_chi_si_rivolge_tassonomia:
            raise BadRequest(
                json.dumps(
                    [
                        {
                            "field": "a_chi_si_rivolge",
                            "message": self.mutual_required_msg,
                        },
                        {
                            "field": "a_chi_si_rivolge_tassonomia",
                            "message": self.mutual_required_msg,
                        },
                        {
                            "message": api.portal.translate(
                                _(
                                    "a_chi_si_rivolge_validation_error",
                                    default='Devi compilare almeno uno dei due campi del tab "A chi si rivolge".',
                                )
                            )
                        },
                    ]
                )
            )

    def validate_event(self, data, create):
        # validate organizzato da

        has_organizzato_da_esterno = self.has_field_value(
            data=data,
            create=create,
            field_id="organizzato_da_esterno",
            is_block_field=True,
        )
        has_organizzato_da_interno = self.has_field_value(
            data=data, create=create, field_id="organizzato_da_interno"
        )

        if not has_organizzato_da_esterno and not has_organizzato_da_interno:
            raise BadRequest(
                json.dumps(
                    [
                        {
                            "field": "organizzato_da_esterno",
                            "message": self.mutual_required_msg,
                        },
                        {
                            "field": "organizzato_da_interno",
                            "message": self.mutual_required_msg,
                        },
                        {
                            "message": api.portal.translate(
                                _(
                                    "organizzato_validation_error",
                                    default='Devi compilare almeno uno dei due campi per "Organizzato da" nel tab "Contatti".',
                                )
                            )
                        },
                    ]
                )
            )

        # validate dove
        has_webinar = self.has_field_value(
            data=data, create=create, field_id="webinar", is_block_field=True
        )
        has_struttura_correlata = self.has_field_value(
            data=data, create=create, field_id="struttura_correlata"
        )

        has_location_infos = self.has_location_infos(data=data, create=create)
        if not has_webinar and not has_struttura_correlata and not has_location_infos:
            raise BadRequest(
                json.dumps(
                    [
                        {
                            "field": "webinar",
                            "message": self.mutual_required_msg,
                        },
                        {
                            "field": "struttura_correlata",
                            "message": self.mutual_required_msg,
                        },
                        {
                            "field": "geolocation",
                            "message": self.mutual_required_msg,
                        },
                        {
                            "message": api.portal.translate(
                                _(
                                    "dove_validation_error",
                                    default='Devi compilare almeno uno dei campi obbligatori nel tab "Dove".',
                                )
                            )
                        },
                    ]
                )
            )

    def validate_dove(self, data, create):
        if not self.has_location_infos(data=data, create=create):
            msg = api.portal.translate(
                _(
                    "dove_validation_error",
                    default="Devi compilare questi campi per poter cercare la posizione in mappa.",
                )
            )
            raise BadRequest(
                json.dumps(
                    [
                        {"field": "street", "message": msg},
                        {"field": "city", "message": msg},
                        {
                            "message": api.portal.translate(
                                _(
                                    "dove_validation_error",
                                    default='Devi compilare almeno uno dei due campi del tab "Dove" e impostare la Geolocation.',
                                )
                            )
                        },
                    ]
                )
            )

    def has_location_infos(self, data, create):
        value = self.get_field_value(data, create, "geolocation")
        if not value:
            return False
        if isinstance(value, Geolocation):
            geolocation = {
                "latitude": getattr(value, "latitude", 0),
                "longitude": getattr(value, "longitude", 0),
            }
        else:
            geolocation = deepcopy(value)
        if geolocation in [{"latitude": 0, "longitude": 0}]:
            return False
        return True

    def has_field_value(self, data, create, field_id, is_block_field=False):
        value = self.get_field_value(data, create, field_id)
        if not value:
            return False
        if is_block_field:
            blocks = value.get("blocks", {})
            if not blocks:
                return False
            blocks_data = list(blocks.values())
            for block in blocks_data:
                if block.get("plaintext", ""):
                    # there is some text
                    return True
            return False
        return True

    def get_field_value(self, data, create, field_id):
        if field_id in data:
            return data[field_id]
        if not create:
            return getattr(self.context, field_id, None)
        return None
