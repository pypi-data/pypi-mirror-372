# -*- coding: utf-8 -*-
from collective.volto.blocksfield.field import BlocksField
from iosanita.contenttypes import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IAChiSiRivolge(model.Schema):
    """Marker interface"""

    a_chi_si_rivolge = BlocksField(
        title=_("a_chi_si_rivolge_label", default="A chi si rivolge"),
        required=False,
        description=_(
            "a_chi_e_rivolta_help",
            default="Descrizione testuale degli utenti dell'ASL a cui è rivolto questo contenuto.",
        ),
    )
    model.fieldset(
        "a_chi_si_rivolge",
        label=_("a_chi_si_rivolge_label", default="A chi si rivolge"),
        description=_(
            "a_chi_si_rivolge_fieldset_help",
            default="Compila almeno uno dei due campi.",
        ),
        fields=["a_chi_si_rivolge"],
    )


@implementer(IAChiSiRivolge)
@adapter(IDexterityContent)
class AChiSiRivolge(object):
    """"""

    def __init__(self, context):
        self.context = context
