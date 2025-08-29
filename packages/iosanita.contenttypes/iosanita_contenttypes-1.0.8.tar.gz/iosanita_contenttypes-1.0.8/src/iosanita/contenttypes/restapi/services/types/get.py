# -*- coding: utf-8 -*-
from plone.restapi.services.types.get import TypesGet as BaseGet
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class FieldsetsMismatchError(Exception):
    """Exception thrown when we try to reorder fieldsets, but the order list is
    different from the fieldsets returned from Plone
    """


FIELDSETS_ORDER = {
    "Bando": [
        "default",
        "cosa_e",
        "a_chi_si_rivolge",
        "come_partecipare",
        "modalita_selezione",
    ],
    "ComeFarePer": [
        "default",
        "a_chi_si_rivolge",
        "come_fare",
        "utenti",
        "ulteriori_informazioni",
    ],
    "Documento": [
        "default",
        "cosa_e",
        "riferimenti",
        "a_chi_si_rivolge",
    ],
    "Event": [
        "default",
        "cosa_e",
        "partecipanti",
        "a_chi_si_rivolge",
        "dove",
        "costi",
        "contatti",
        "ulteriori_informazioni",
        "contenuti_collegati",
    ],
    "Document": [
        "default",
        "testata",
        "settings",
        "correlati",
        "categorization",
        "dates",
        "ownership",
        "seo",
    ],
    "Struttura": [
        "default",
        "cosa_e",
        "a_chi_si_rivolge",
        "dove",
        "come_accedere",
        "orari",
        "contatti",
        "servizi",
        "persone_struttura",
        "contenuti_collegati",
        "ulteriori_informazioni",
        "seo",
    ],
    "News Item": [
        "default",
        "correlati",
        "dates",
    ],
    "Persona": [
        "default",
        "incarichi",
        "competenze",
        "dove",
        "orari_ricevimento",
        "contatti",
        "biografia",
        "ulteriori_informazioni",
    ],
    "PuntoDiContatto": [
        "default",
    ],
    "Servizio": [
        "default",
        "cosa_serve",
        "accedi_al_servizio",
        "tempi_attesa",
        "costi",
        "dove",
        "orari",
        "contatti",
        "cosa_e",
        "a_chi_si_rivolge",
        "procedure_collegate_esito",
        "responsabili",
        "ulteriori_informazioni",
        "contenuti_collegati",
    ],
    "UnitaOrganizzativa": [
        "default",
        "cosa_fa",
        "persone_uo",
        "struttura",
        "persone",
        "servizi",
        "dove",
        "orari",
        "contatti",
        "documenti",
        "ulteriori_informazioni",
    ],
    "Step": [
        "default",
        "contatti",
    ],
    "Modulo": ["default", "formati"],
}


@implementer(IPublishTraverse)
class TypesGet(BaseGet):
    def customize_versioning_fields_fieldset(self, result):
        """
        Unico modo per spostare i campi del versioning.
        Perché changeNotes ha l'order after="*" che vince su tutto.
        """
        versioning_fields = ["versioning_enabled", "changeNote"]
        for field in versioning_fields:
            found = False
            for fieldset in result["fieldsets"]:
                if fieldset.get("id") == "default" and field in fieldset["fields"]:
                    found = True
                    fieldset["fields"].remove(field)
                if fieldset.get("id") == "settings" and found:
                    fieldset["fields"].append(field)

    def reply(self):
        result = super(TypesGet, self).reply()
        if "fieldsets" in result:
            result["fieldsets"] = self.reorder_fieldsets(schema=result)

        if "title" in result:
            self.customize_versioning_fields_fieldset(result)
        return result

    def get_order_by_type(self, portal_type):
        return [x for x in FIELDSETS_ORDER.get(portal_type, [])]

    def reorder_fieldsets(self, schema):
        original = schema["fieldsets"]
        pt = self.request.PATH_INFO.split("/")[-1]
        order = self.get_order_by_type(portal_type=pt)
        if not order:
            # no match
            return original
        original_fieldsets = [x["id"] for x in original]
        for fieldset_id in original_fieldsets:
            # if some fieldsets comes from additional addons (not from the
            # base ones), then append them to the order list.
            if fieldset_id not in order:
                order.append(fieldset_id)

        # create a new fieldsets list with the custom order
        new = []
        for id in order:
            for fieldset in original:
                if fieldset["id"] == id and self.fieldset_has_fields(fieldset, schema):
                    new.append(fieldset)
        if not new:
            # no match
            return original
        return new

    def fieldset_has_fields(self, fieldset, schema):
        """
        If a fieldset has all hidden fields (maybe after a schema tweak),
        these are not in the schema data, but are still in fieldset data.
        This happens only in add, because the schema is generate with the parent's context.
        """
        fieldset_fields = fieldset["fields"]

        schema_fields = [x for x in fieldset_fields if x in schema["properties"].keys()]

        return len(schema_fields) > 0
