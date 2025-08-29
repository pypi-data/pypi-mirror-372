from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.relationfield import (
    RelationListFieldSerializer as BaseSerializer,
)
from z3c.relationfield.interfaces import IRelationList
from zope.component import adapter
from zope.interface import implementer


@adapter(IRelationList, IDexterityContent, IIosanitaContenttypesLayer)
@implementer(IFieldSerializer)
class RelationListFieldSerializer(BaseSerializer):
    def __call__(self):
        """
        Do not return broken relations
        """
        data = super().__call__()
        return [x for x in data if x is not None]
