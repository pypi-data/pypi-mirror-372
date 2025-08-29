# -*- coding: utf-8 -*-
from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from plone.app.dexterity import textindexer
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IEvento(model.Schema):
    """Marker inteerface for content type Evento"""

    descrizione_estesa = BlocksField(
        title=_("descrizione_estesa_label", default="Cos'è"),
        required=True,
        description=_(
            "evento_descrizione_estesa_help",
            default="Descrizione dettagliata e completa.",
        ),
    )

    costo = BlocksField(
        title=_("costo_label", default="Costo"),
        required=True,
        description=_(
            "costo_help",
            default="Eventuale costo dell'evento (se ci sono uno o più biglietti), "
            "con link all'acquisto se disponibile.",
        ),
    )

    organizzato_da_interno = RelationList(
        title=_(
            "organizzato_da_interno_label",
            default="Organizzato da: Unità organizzativa",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
        description=_(
            "organizzato_da_interno_help",
            default="Se l'evento è organizzato da un'Unità organizzativa dell'ASL, includere collegamento alla relativa pagina.",
        ),
    )
    organizzato_da_esterno = BlocksField(
        title=_("organizzato_da_esterno_label", default="Organizato da: altro"),
        required=False,
        description=_(
            "organizzato_da_esterno_help",
            default="Indicazione di chi orgnanizza l'evento, se diverso da un'Unità organizzativa.",
        ),
    )

    #  campi aggiunti con il pnrr
    patrocinato_da = BlocksField(
        title=_("patrocinato_da_label", default="Patrocinato da"),
        required=False,
        description=_(
            "patrocinato_da_help",
            default="Indicare l'ente che supporta l'evento, se presente.",
        ),
    )

    persona_correlata = RelationList(
        title=_("persona_correlata_event_label", default="Parteciperanno (Persone)"),
        required=False,
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        description=_(
            "persona_correlata_event_help",
            default="Seleziona una serie di Persone dell'ASL che interverranno all'evento.",
        ),
    )
    parteciperanno = BlocksField(
        title=_("parteciperanno_label", default="Parteciperanno"),
        required=False,
        description=_(
            "parteciperanno_help",
            default="Lista delle persone che parteciperanno, se non fanno parte dell'ASL.",
        ),
    )

    eventi_correlati = RelationList(
        title="Eventi correlati",
        default=[],
        required=False,
        description=_(
            "eventi_correlati_help",
            default="Seleziona altri eventi simili o collegati.",
        ),
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
    )

    webinar = BlocksField(
        title=_("webinar_label", default="Webinar"),
        required=False,
        description=_(
            "webinar_help",
            default="Se l'evento è un webinar, specificare che è online e includere il link alla piattaforma di streaming.",
        ),
    )
    struttura_correlata = RelationList(
        title=_("struttura_correlata_label", default="Struttura di riferimento"),
        description=_(
            "struttura_correlata_help",
            default="Indicare una o più strutture che fanno a capo a questo contenuto.",
        ),
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        default=[],
        required=False,
    )

    # custom order
    form.order_after(organizzato_da_interno="pdc_correlato")
    form.order_after(organizzato_da_esterno="organizzato_da_interno")
    form.order_after(patrocinato_da="organizzato_da_esterno")

    # custom widgets

    form.widget(
        "eventi_correlati",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Event"],
        },
    )
    form.widget(
        "organizzato_da_interno",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["UnitaOrganizzativa"],
        },
    )
    form.widget(
        "persona_correlata",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Persona"],
        },
    )
    form.widget(
        "struttura_correlata",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={"selectableTypes": ["Struttura"]},
    )

    # custom fieldsets and order
    model.fieldset(
        "cosa_e",
        label=_("cosa_e_fieldset", default="Cos'è"),
        fields=[
            "descrizione_estesa",
        ],
    )

    model.fieldset("costi", label=_("costi_label", default="Costi"), fields=["costo"])
    model.fieldset(
        "contatti",
        label=_("contatti_label", default="Contatti"),
        description=_(
            "contatti_fieldset_help",
            default='Almeno uno dei due campi "Organizzato da" deve essere compilato.',
        ),
        fields=[
            "organizzato_da_interno",
            "organizzato_da_esterno",
            "patrocinato_da",
        ],
    )
    model.fieldset(
        "partecipanti",
        label=_("partecipanti_label", default="Chi partecipa"),
        fields=["persona_correlata", "parteciperanno"],
    )
    model.fieldset(
        "contenuti_collegati",
        label=_("contenuti_collegati_label", default="Contenuti collegati"),
        fields=["eventi_correlati"],
    )

    model.fieldset(
        "dove",
        label=_("dove_label", default="Dove"),
        description=_(
            "dove_event_help",
            default="Se la sede di questo contenuto non coincide con la Struttura di riferimento o non è un webinar, compilare gli altri campi.",
        ),
        fields=["webinar", "struttura_correlata"],
    )
    textindexer.searchable("descrizione_estesa")


@implementer(IEvento)
@adapter(IDexterityContent)
class Evento(object):
    """ """

    def __init__(self, context):
        self.context = context
