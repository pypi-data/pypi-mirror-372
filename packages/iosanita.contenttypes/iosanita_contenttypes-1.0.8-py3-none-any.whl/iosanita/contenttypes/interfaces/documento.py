# -*- coding: utf-8 -*-

from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from iosanita.contenttypes.interfaces import IIosanitaContenttypes
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema


class IDocumento(model.Schema, IIosanitaContenttypes):
    """Marker interface for content type"""

    protocollo = schema.TextLine(
        title=_(
            "protocollo_documento_label",
            default="Numero di protocollo",
        ),
        description=_(
            "protocollo_documento_help",
            default="Il numero di protocollo del documento.",
        ),
        max_length=255,
        required=False,
    )

    data_protocollo = schema.Date(
        title=_("data_protocollo", default="Data del protocollo"),
        required=False,
    )

    descrizione_estesa = BlocksField(
        title=_("descrizione_estesa_label", default="Cos'è"),
        required=True,
        description=_(
            "descrizione_estesa_documento_help",
            default="Descrizione estesa e completa del Documento.",
        ),
    )

    servizio_procedura_riferimento = RelationList(
        title=_(
            "servizio_procedura_riferimento_label",
            default="Servizio di riferimento / Procedura di riferimento",
        ),
        description=_(
            "servizio_procedura_riferimento_help",
            default="Indicazione del servizio, la  prestazione o la procedura (Come fare per) a cui fa riferimento il documento.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
        missing_value=(),
    )

    uo_correlata = RelationList(
        title=_("uo_correlata_documento_label", default="Responsabile del documento"),
        description=_(
            "uo_correlata_documento_help",
            default="Indicazione dell'unità organizzativa responsabile del documento.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=True,
        missing_value=(),
    )

    autori = RelationList(
        title=_(
            "autori_label",
            default="Autore/i",
        ),
        description=_(
            "autori_help",
            default="Seleziona una lista di autori che hanno pubblicato "
            "il documento.",
        ),
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
        default=[],
    )

    # widgets
    form.widget(
        "uo_correlata",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "maximumSelectionSize": 1,
            "selectableTypes": ["UnitaOrganizzativa"],
        },
    )
    form.widget(
        "autori",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Persona"],
        },
    )
    form.widget(
        "servizio_procedura_riferimento",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["ComeFarePer", "Servizio"],
        },
    )

    model.fieldset(
        "cosa_e",
        label=_("cosa_e_fieldset", default="Cos'è"),
        fields=["descrizione_estesa"],
    )

    model.fieldset(
        "riferimenti",
        label=_("riferimenti_fieldset", default="Riferimenti"),
        fields=["servizio_procedura_riferimento", "uo_correlata", "autori"],
    )
