from iosanita.contenttypes.interfaces import IIosanitaContenttypesLayer
from iosanita.contenttypes.interfaces.settings import IIoSanitaContenttypesSettings
from iosanita.contenttypes.interfaces.settings import (
    IIoSanitaContenttypesSettingsControlpanel,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, IIosanitaContenttypesLayer)
@implementer(IIoSanitaContenttypesSettingsControlpanel)
class IoSanitaContenttypesSettingsControlpanel(RegistryConfigletPanel):
    schema = IIoSanitaContenttypesSettings
    configlet_id = "IoSanitaContenttypesSettings"
    configlet_category_id = "Products"
    schema_prefix = None
