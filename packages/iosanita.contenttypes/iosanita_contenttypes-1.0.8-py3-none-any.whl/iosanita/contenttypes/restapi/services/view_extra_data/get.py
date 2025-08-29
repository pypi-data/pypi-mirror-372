# -*- coding: utf-8 -*-
from iosanita.contenttypes.interfaces import IoSanitaViewExtraData
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class ViewExtraData(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "view-extra-data": {
                "@id": f"{self.context.absolute_url()}/@view-extra-data"
            }
        }
        data = queryMultiAdapter((self.context, self.request), IoSanitaViewExtraData)()
        result["view-extra-data"].update(data)

        return result


class ViewExtraDataGet(Service):
    def reply(self):
        data = ViewExtraData(self.context, self.request)
        return data(expand=True)["view-extra-data"]
