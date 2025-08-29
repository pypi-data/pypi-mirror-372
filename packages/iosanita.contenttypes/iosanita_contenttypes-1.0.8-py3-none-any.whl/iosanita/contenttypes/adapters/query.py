from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from plone import api
from plone.restapi.interfaces import IZCatalogCompatibleQuery
from plone.restapi.search.query import ZCatalogCompatibleQueryAdapter as BaseAdapter
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IZCatalogCompatibleQuery)
@adapter(Interface, IIosanitaContenttypesLayer)
class ZCatalogCompatibleQueryAdapter(BaseAdapter):
    """ """

    def __call__(self, query):
        """
        Do not show excluded from search items when anonymous are performing
        some catalog searches
        """
        query = super().__call__(query=query)

        if api.user.is_anonymous():
            # For the anonymous user, only content that is not "excluded from the search" is found
            query["exclude_from_search"] = False

        return query
