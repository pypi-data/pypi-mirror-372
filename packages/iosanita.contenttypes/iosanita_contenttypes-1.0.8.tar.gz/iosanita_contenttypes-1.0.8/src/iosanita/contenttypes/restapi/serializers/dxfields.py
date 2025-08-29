# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.volto.enhancedlinks.interfaces import IEnhancedLinksEnabled
from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from plone.base.utils import human_readable_size
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedFileField
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter


@adapter(INamedFileField, IDexterityContent, IIosanitaContenttypesLayer)
class FileFieldViewModeSerializer(DefaultFieldSerializer):
    """
    Ovveride the basic DX serializer to:
        - handle the visualize file functionality
        - add getObjSize info
    """

    def __call__(self):
        namedfile = self.field.get(self.context)
        if namedfile is None:
            return

        url = "/".join(
            (
                self.context.absolute_url(),
                self.get_file_view_mode(namedfile.contentType),
                self.field.__name__,
            )
        )
        size = namedfile.getSize()
        result = {
            "filename": namedfile.filename,
            "content-type": namedfile.contentType,
            "size": size,
            "download": url,
        }
        if IEnhancedLinksEnabled.providedBy(self.context):
            result.update(
                {
                    "getObjSize": human_readable_size(size),
                    "enhanced_links_enabled": True,
                }
            )

        return json_compatible(result)

    def get_file_view_mode(self, content_type):
        """Pdf view depends on the anteprima_file property in thq aq_chain"""
        if self.context and "pdf" in content_type:
            if getattr(aq_inner(self.context), "anteprima_file", None):
                return "@@display-file"

        return "@@download"
