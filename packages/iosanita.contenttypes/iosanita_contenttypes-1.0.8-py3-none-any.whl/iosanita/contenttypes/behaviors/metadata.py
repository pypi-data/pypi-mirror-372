from plone.app.dexterity import _
from plone.app.dexterity import textindexer
from plone.app.dexterity.behaviors.metadata import Basic
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IIoSanitaBasic(model.Schema):
    """
    Make description required
    """

    # default fieldset
    title = schema.TextLine(title=_("label_title", default="Title"), required=True)

    description = schema.Text(
        title=_("label_description", default="Summary"),
        description=_(
            "help_description", default="Used in item listings and search results."
        ),
        required=True,
        missing_value="",
    )

    directives.order_before(description="*")
    directives.order_before(title="*")

    directives.omitted("title", "description")
    directives.no_omit(IEditForm, "title", "description")
    directives.no_omit(IAddForm, "title", "description")

    textindexer.searchable("title")
    textindexer.searchable("description")


class IoSanitaBasic(Basic):
    """ """
