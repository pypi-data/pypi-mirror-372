# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from iosanita.contenttypes import _
from iosanita.contenttypes.interfaces import IIosanitaContenttypes
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema


class IPDCValueSchema(model.Schema):
    tipo = schema.Choice(
        title=_("pdc_tipo_label", default="Tipo"),
        # description=_(
        #     "pdc_tipo_help",
        #     default="Tipologia di contatto",
        # ),
        vocabulary="collective.taxonomy.tipologia_pdc",
        required=True,
        default="",
    )
    valore = schema.TextLine(
        title=_("pdc_valore_label", default="Contatto"),
        # description=_(
        #     "pdc_valore_help",
        #     default="Il valore del contatto",
        # ),
        required=True,
        default="",
        max_length=255,
    )
    descrizione = schema.TextLine(
        title=_("pdc_descrizione_label", default="Descrizione"),
        # description=_(
        #     "pdc_descrizione_help",
        #     default="Eventuale descrizione per questo valore",
        # ),
        required=False,
        default="",
        max_length=255,
    )


class IPuntoDiContatto(model.Schema, IIosanitaContenttypes):
    """Marker interface for content type PuntoDiContatto"""

    contatti = schema.List(
        title="Contatti",
        default=[],
        value_type=DictRow(schema=IPDCValueSchema),
        description=_(
            "value_punto_contatto_help",
            default="Il valore del punto di contatto: il numero compreso di prefisso "
            "internazionale (se telefono), l'account (se social network), "
            "l'URL (se sito o pagina web), l'indirizzo email (se email).",
        ),
        required=True,
    )
    uo_correlata = RelationList(
        title=_("uo_correlata_label", default="Unità Organizzativa correlata"),
        description=_(
            "uo_correlata_help",
            default="Selezionare l'Unità Organizzativa per cui questo Punto di contatto è valido. "
            "Se il Punto di contatto è associato ad una Persona, allora quella persona avrà questi contatti nell'Unità organizzativa selezionata.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
    )

    form.widget(
        "contatti",
        DataGridFieldFactory,
        frontendOptions={
            "widget": "data_grid",
            "widgetProps": {
                "allow_reorder": True,
            },
        },
    )

    form.widget(
        "uo_correlata",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["UnitaOrganizzativa"],
        },
    )
