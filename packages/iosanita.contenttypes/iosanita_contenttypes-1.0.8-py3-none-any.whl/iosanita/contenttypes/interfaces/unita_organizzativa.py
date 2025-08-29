# -*- coding: utf-8 -*-
from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from plone.app.dexterity import textindexer
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList


class IUnitaOrganizzativa(model.Schema):
    """Marker interface for content type UnitaOrganizzativa"""

    competenze = BlocksField(
        title=_("uo_competenze_label", default="Competenze"),
        description=_(
            "uo_competenze_help",
            default="Descrizione dei compiti assegnati a quest unità organizzativa.",
        ),
        required=True,
    )

    responsabile_correlato = RelationList(
        title=_("responsabile_correlato_uo_label", default="Responsabile"),
        description=_(
            "responsabile_correlato_uo_help",
            default="La persona che dirige l'unità organizzativa.",
        ),
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        default=[],
        required=False,
    )

    personale_correlato = RelationList(
        title=_("personale_correlato_uo_label", default="Personale"),
        description=_(
            "personale_correlato_uo_help",
            default="Elenco del personale che opera nell'unità organizzativa.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
    )

    orari = BlocksField(
        title=_("orari_uo_label", default="Orari di apertura"),
        description=_(
            "orari_uo_help",
            default="Indicazione delle fasce orarie in cui è possibile contattare o accedere all'unità organizzativa.",
        ),
        required=True,
    )

    documento_correlato = RelationList(
        title=_("documento_correlato_label", default="Documenti"),
        default=[],
        description=_(
            "documento_correlato_help",
            default="Seleziona dei documenti correlati.",
        ),
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
    )

    #  custom widgets
    form.widget(
        "documento_correlato",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Documento"],
        },
    )
    form.widget(
        "personale_correlato",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={"selectableTypes": ["Persona"]},
    )
    form.widget(
        "responsabile_correlato",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "maximumSelectionSize": 1,
            "selectableTypes": ["Persona"],
            # "basePath": "/amministrazione",
        },
    )

    # custom fieldsets and order
    model.fieldset(
        "cosa_fa",
        label=_("cosa_fa_label", default="Competenze"),
        fields=["competenze"],
    )
    model.fieldset(
        "persone_uo",
        label=_("persone_uo_fieldset_label", default="Persone Unità organizzativa"),
        fields=[
            "responsabile_correlato",
            "personale_correlato",
        ],
    )
    model.fieldset(
        "orari",
        label=_("orari_uo_label", default="Orari di apertura"),
        fields=["orari"],
    )

    model.fieldset(
        "documenti",
        label=_("documenti_label", default="Documenti"),
        fields=["documento_correlato"],
    )

    # SearchableText indexers
    textindexer.searchable("competenze")
    textindexer.searchable("orari")
