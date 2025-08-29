# -*- coding: utf-8 -*-
from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from iosanita.contenttypes.interfaces import IIosanitaContenttypes
from plone.autoform import directives as form
from plone.supermodel import model


class IComeFarePer(model.Schema, IIosanitaContenttypes):
    """Marker interface for content type"""

    panoramica = BlocksField(
        title=_("panoramica_label", default="Panoramica"),
        description=_(
            "panoramica_help",
            default="Descrizione più estesa della procedura di cui viene descritto il processo di usufruizione.",
        ),
        required=True,
    )
    come_fare = BlocksField(
        title=_("come_fare_label", default="Come fare"),
        description=_(
            "come_fare_help",
            default="Descrizione generale del processo da seguire per effettuare la procedura."
            ' Se il processo è composto da più step, allora vanno creati dei contenuti di tipo "Step" con informazioni dettagliate.',
        ),
        required=True,
    )
    form.order_after(panoramica="sottotitolo")

    # custom fieldsets
    model.fieldset(
        "come_fare",
        label=_("come_fare_label", default="Come fare"),
        fields=[
            "come_fare",
        ],
    )
