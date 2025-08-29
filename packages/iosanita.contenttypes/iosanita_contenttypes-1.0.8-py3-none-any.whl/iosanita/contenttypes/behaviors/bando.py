# -*- coding: utf-8 -*-
from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from plone.app.dexterity import textindexer
from plone.app.event.base import default_timezone
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IBando(model.Schema):
    """Marker interface for content type Bando"""

    descrizione_estesa = BlocksField(
        title=_("descrizione_estesa_label", default="Cos'è"),
        required=True,
        description=_(
            "descrizione_estesa_bando_help",
            default="Descrizione dettagliata e completa.",
        ),
    )

    come_partecipare = BlocksField(
        title=_("come_partecipare_label", default="Come partecipare"),
        required=True,
        description=_(
            "come_partecipare_help",
            default="Descrizione delle modalità di partecipazione al bando o al concorso e collegamento.",
        ),
    )
    modalita_selezione = BlocksField(
        title=_("modalita_selezione_label", default="Modalità di selezione"),
        required=True,
        description=_(
            "modalita_selezione_help",
            default="Informazioni sulle modalità di selezione, ad esempio da quante prove e di che tipo è composta la selezione.",
        ),
    )

    scadenza_domande_bando = schema.Datetime(
        title=_(
            "scadenza_domande_bando_label",
            default="Termine per le richieste di chiarimenti",
        ),
        description=_(
            "scadenza_domande_bando_help",
            default="Data entro la quale sarà possibile far pervenire domande"
            " e richieste di chiarimento a chi eroga il bando",
        ),
        required=False,
    )

    note_aggiornamento = schema.TextLine(
        title=_("note_aggiornamento_label", default="Note di aggiornamento"),
        description=_(
            "help_note_aggiornamento",
            default="Inserisci una nota per indicare che il contenuto corrente è stato aggiornato."  # noqa
            " Questo testo può essere visualizzato nei blocchi elenco con determinati layout per informare "  # noqa
            "gli utenti che un determinato contenuto è stato aggiornato. "
            "Ad esempio se in un bando sono stati aggiunti dei documenti.",
        ),
        required=False,
    )

    # custom fieldsets and order
    model.fieldset(
        "cosa_e",
        label=_("cosa_e_fieldset", default="Cos'è"),
        fields=[
            "descrizione_estesa",
        ],
    )
    model.fieldset(
        "come_partecipare",
        label=_("come_partecipare_label", default="Come partecipare"),
        fields=[
            "come_partecipare",
        ],
    )
    model.fieldset(
        "modalita_selezione",
        label=_("modalita_selezione_label", default="Modalità di selezione"),
        fields=[
            "modalita_selezione",
        ],
    )

    # custom widgets
    form.widget(
        "scadenza_domande_bando",
        DatetimeFieldWidget,
        default_timezone=default_timezone,
    )

    # custom order
    form.order_after(scadenza_domande_bando="apertura_bando")

    textindexer.searchable("descrizione_estesa")


@implementer(IBando)
@adapter(IDexterityContent)
class Bando(object):
    """ """

    def __init__(self, context):
        self.context = context
