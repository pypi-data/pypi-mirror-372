# -*- coding: utf-8 -*-
from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.dexterity import textindexer
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class INewsAdditionalFields(model.Schema):
    descrizione_estesa = BlocksField(
        title=_("descrizione_estesa_news_label", default="Testo"),
        required=True,
        description=_(
            "descrizione_estesa_news_help",
            default="Testo principale della notizia.",
        ),
    )

    numero_progressivo_cs = schema.TextLine(
        title=_(
            "numero_progressivo_cs_label",
            default="Numero progressivo del comunicato stampa",
        ),
        description=_(
            "numero_progressivo_cs_help",
            default="Se è un comunicato stampa, indicare un'eventuale numero progressivo del comunicato stampa.",
        ),
        required=False,
    )

    persona_correlata = RelationList(
        title=_("persona_correlata_news_label", default="Persone"),
        required=False,
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        description=_(
            "persona_correlata_news_help",
            default="Seleziona una serie di Persone dell'ASL citate nella notizia.",
        ),
    )
    struttura_correlata = RelationList(
        title=_("struttura_correlata_news_label", default="Strutture"),
        required=False,
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        description=_(
            "struttura_correlata_news_help",
            default="Seleziona una serie di Strutture dell'ASL citate nella notizia.",
        ),
    )

    servizio_correlato = RelationList(
        title=_("servizio_correlato_label", default="Servizi e prestazioni"),
        description=_(
            "servizio_correlato_help",
            default="Elenco dei servizi e delle prestazioni dell'ASL citati nella notizia, con collegamento alle relative pagine foglia servizio. L'elemento è necessario se nella notizia sono citati specifici servizi o prestazioni dell'ASL.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
    )
    uo_correlata = RelationList(
        title=_("uo_correlata_news_label", default="A cura di"),
        description=_(
            "uo_correlata_news_help",
            default="Unità Organizzativa che ha curato il comunicato.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=True,
    )
    notizia_correlata = RelationList(
        title=_("notizia_correlata_label", default="Notizie correlate"),
        description=_(
            "notizia_correlata_help",
            default="Elenco di notizie simili o collegate.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
    )
    # custom widgets
    form.widget(
        "persona_correlata",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Persona"],
        },
    )
    form.widget(
        "notizia_correlata",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["News Item"],
        },
    )
    form.widget(
        "struttura_correlata",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Struttura"],
        },
    )
    form.widget(
        "servizio_correlato",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Servizio"],
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
    model.fieldset(
        "correlati",
        label=_("correlati_label", default="Contenuti collegati"),
        fields=[
            "persona_correlata",
            "struttura_correlata",
            "servizio_correlato",
            "uo_correlata",
            "notizia_correlata",
        ],
    )
    # custom fieldsets and order
    form.order_after(numero_progressivo_cs="description")
    form.order_after(descrizione_estesa="numero_progressivo_cs")

    textindexer.searchable("descrizione_estesa")


@implementer(INewsAdditionalFields)
@adapter(INewsItem)
class NewsAdditionalFields(object):
    """ """

    def __init__(self, context):
        self.context = context
