# -*- coding: utf-8 -*-
from iosanita.contenttypes import _
from plone.app.contenttypes.interfaces import IDocument
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


class IArgomentiSchema(model.Schema):
    """Marker interface for Argomenti"""

    correlato_in_evidenza = RelationList(
        title=_("correlato_in_evidenza_label", default="Correlato in evidenza"),
        description=_(
            "correlato_in_evidenza_help",
            default="Seleziona un correlato da mettere in evidenza per questo"
            " contenuto.",
        ),
        value_type=RelationChoice(
            title=_("Correlato in evidenza"),
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=False,
        default=[],
    )

    form.widget(
        "correlato_in_evidenza",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={"maximumSelectionSize": 1},
    )


@provider(IFormFieldProvider)
class IArgomenti(IArgomentiSchema):
    """ """

    model.fieldset(
        "correlati",
        label=_("correlati_label", default="Contenuti collegati"),
        fields=["correlato_in_evidenza"],
    )
    form.order_after(correlato_in_evidenza="IRelatedItems.relatedItems")


@provider(IFormFieldProvider)
class IArgomentiDocument(IArgomentiSchema):
    """ """

    model.fieldset(
        "correlati",
        label=_("correlati_label", default="Contenuti collegati"),
        fields=["correlato_in_evidenza"],
    )

    form.order_after(correlato_in_evidenza="IRelatedItems.relatedItems")


@implementer(IArgomenti)
@adapter(IDexterityContent)
class Argomenti(object):
    """"""

    def __init__(self, context):
        self.context = context


@implementer(IArgomentiDocument)
@adapter(IDocument)
class ArgomentiDocument(Argomenti):
    """"""

    def __init__(self, context):
        self.context = context
