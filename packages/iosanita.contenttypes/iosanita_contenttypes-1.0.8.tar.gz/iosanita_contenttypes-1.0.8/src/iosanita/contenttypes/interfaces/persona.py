# -*- coding: utf-8 -*-
from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from iosanita.contenttypes.interfaces import IIosanitaContenttypes
from plone.app.dexterity import textindexer
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.namedfile import field
from plone.supermodel import model
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema


class IPersona(model.Schema, IIosanitaContenttypes):
    """Marker interface for contenttype Persona"""

    cognome = schema.TextLine(
        title=_("cognome_label", default="Cognome"),
        description="",
        required=True,
        missing_value="",
        default="",
    )
    nome = schema.TextLine(
        title=_("nome_label", default="Nome"),
        description="",
        required=True,
        missing_value="",
        default="",
    )
    titolo_persona = schema.TextLine(
        title=_("titolo_persona_label", default="Titolo persona"),
        description=_(
            "titolo_persona_help", default="Un titolo personale come ad esempio Dr. "
        ),
        required=False,
        missing_value="",
        default="",
    )
    title = schema.TextLine(
        title=_("label_title", default="Titolo"),
        description="",
        required=False,
        missing_value="",
        readonly=True,
        default="",
    )
    description = schema.Text(
        title=_("label_description", default="Descrizione"),
        description=_(
            "help_description",
            default="Usato nell'elenco degli elementi e nei risultati delle ricerche.",
        ),
        required=False,
        missing_value="",
    )

    image = field.NamedBlobImage(
        title=_("foto_persona_label", default="Foto"),
        required=False,
        description=_(
            "foto_persona_help",
            default="Foto da mostrare dentro al sito. "
            "La dimensione suggerita è 100x180px.",
        ),
    )

    altri_incarichi = BlocksField(
        title=_("altri_incarichi_label", default="Altri incarichi"),
        description=_(
            "altri_incarichi_help",
            default="Indicazione degli altri incarichi della persona all'interno dell'ASL.",
        ),
        required=False,
    )

    competenze = BlocksField(
        title=_("competenze_label", default="Competenze"),
        description=_(
            "competenze_help",
            default="Descrizione del ruolo e dei compiti della persona.",
        ),
        required=True,
    )

    orari_ricevimento = BlocksField(
        title=_("orari_ricevimento_label", default="Orari di ricevimento"),
        description=_(
            "orari_ricevimento_help",
            default="Orari durante i quali è possibile incontrare la persona descritta, se effettua ricevimento.",
        ),
        required=False,
    )
    struttura_in_cui_opera = RelationList(
        title=_(
            "struttura_in_cui_opera_label",
            default="Strutture in cui opera",
        ),
        description=_(
            "struttura_in_cui_opera_help",
            default="Seleziona una lista di strutture in cui opera la persona. Necessario per le persone interne all'ASL, mentre è opzionale per i medici di base e pediatri.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
        missing_value=(),
    )
    struttura_ricevimento = RelationList(
        title=_(
            "struttura_ricevimento_label",
            default="Struttura ricevimento",
        ),
        description=_(
            "struttura_ricevimento_help",
            default="Seleziona una struttura presente sul portale dove la persona riceve i pazienti. Se non è disponibile, compila i campi successivi.",
        ),
        default=[],
        value_type=RelationChoice(vocabulary="plone.app.vocabularies.Catalog"),
        required=False,
        missing_value=(),
    )

    biografia = BlocksField(
        title=_("biografia_label", default="Biografia"),
        description=_("biografia_help", default=""),
        required=False,
    )

    # custom widgets
    form.widget(
        "struttura_ricevimento",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            # "maximumSelectionSize": 1,
            "selectableTypes": ["Struttura"],
        },
    )
    form.widget(
        "struttura_in_cui_opera",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Struttura"],
        },
    )

    # custom fieldsets
    model.fieldset(
        "incarichi",
        label=_("incarichi_label", default="Incarichi"),
        fields=[
            "altri_incarichi",
        ],
    )
    model.fieldset(
        "competenze",
        label=_("competenze_label", default="Competenze"),
        fields=[
            "competenze",
        ],
    )

    model.fieldset(
        "dove",
        label=_("dove_label", default="Dove"),
        description=_(
            "dove_persona_help",
            default="Se la persona fa ricevimento, indicare dove. "
            "Questo elemento è necessario per i medici di base e pediatri.",
        ),
        fields=["struttura_ricevimento", "struttura_in_cui_opera"],
    )

    model.fieldset(
        "orari_ricevimento",
        label=_("orari_ricevimento_label", default="Orari di ricevimento"),
        fields=[
            "orari_ricevimento",
        ],
    )

    model.fieldset(
        "biografia",
        label=_("biografia_label", default="Biografia"),
        fields=[
            "biografia",
        ],
    )

    form.order_before(description="*")
    form.order_before(title="*")
    form.order_before(titolo_persona="*")
    form.order_before(nome="*")
    form.order_before(cognome="*")
    form.order_after(altri_incarichi="incarico")

    form.omitted("description")
    form.omitted("title")
    form.no_omit(IEditForm, "description")
    form.no_omit(IAddForm, "description")

    # SearchableText fields
    textindexer.searchable("nome")
    textindexer.searchable("cognome")
    textindexer.searchable("competenze")
