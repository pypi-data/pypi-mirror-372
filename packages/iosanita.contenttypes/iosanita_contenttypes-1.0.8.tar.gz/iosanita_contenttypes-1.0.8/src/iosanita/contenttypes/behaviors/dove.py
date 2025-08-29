# -*- coding: utf-8 -*-
from collective.address import _ as _addresmf
from collective.address.behaviors import IAddress
from collective.geolocationbehavior.geolocation import IGeolocatable
from iosanita.contenttypes import _
from plone.app.dexterity import textindexer
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IDove(IGeolocatable, IAddress):
    nome_sede = schema.TextLine(
        title=_("nome_sede", default="Nome sede"),
        description=_(
            "help_nome_sede",
            default="Inserisci il nome della "
            "sede, se non è presente tra quelle del sito.",
        ),
        required=False,
    )

    provincia = schema.TextLine(
        title=_("provincia", default="Provincia"),
        description=_("help_provincia", default=""),
        required=False,
    )

    circoscrizione = schema.TextLine(
        title=_("circoscrizione", default="Circoscrizione"),
        description=_("help_circoscrizione", default=""),
        required=False,
    )

    # searchabletext indexer
    textindexer.searchable("street")
    textindexer.searchable("nome_sede")
    textindexer.searchable("provincia")
    textindexer.searchable("circoscrizione")
    textindexer.searchable("zip_code")
    textindexer.searchable("city")
    textindexer.searchable("country")

    model.fieldset(
        "dove",
        label=_("dove_label", default="Dove"),
        fields=[
            "nome_sede",
            "street",
            "zip_code",
            "city",
            "provincia",
            "circoscrizione",
            "country",
            "geolocation",
        ],
    )


@provider(IFormFieldProvider)
class IDoveRequired(IDove):
    """redefine some required fields"""

    provincia = schema.TextLine(
        title=_("provincia", default="Provincia"),
        description=_("help_provincia", default=""),
        required=True,
    )
    street = schema.TextLine(
        title=_addresmf("label_street", default="Street"),
        description=_addresmf("help_street", default=""),
        required=True,
    )
    zip_code = schema.TextLine(
        title=_addresmf("label_zip_code", default="Zip Code"),
        description=_addresmf("help_zip_code", default=""),
        required=True,
    )
    city = schema.TextLine(
        title=_addresmf("label_city", default="City"),
        description=_addresmf("help_city", default=""),
        required=True,
    )
    country = schema.Choice(
        title=_addresmf("label_country", default="Country"),
        description=_addresmf(
            "help_country", default="Select the country from the list."
        ),
        required=True,
        vocabulary="collective.address.CountryVocabulary",
    )


@implementer(IDove)
@adapter(IDexterityContent)
class Dove(object):
    """ """

    def __init__(self, context):
        self.context = context


@implementer(IDoveRequired)
@adapter(IDexterityContent)
class DoveRequired(object):
    """ """

    def __init__(self, context):
        self.context = context
