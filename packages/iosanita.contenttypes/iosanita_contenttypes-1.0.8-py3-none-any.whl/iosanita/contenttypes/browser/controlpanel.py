from iosanita.contenttypes import _
from iosanita.contenttypes.interfaces.settings import IIoSanitaContenttypesSettings
from plone.app.registry.browser import controlpanel


class IoSanitaContenttypesSettingsForm(controlpanel.RegistryEditForm):
    schema = IIoSanitaContenttypesSettings
    label = _(
        "iosanita_contenttypes_settings_label",
        default="Impostazioni IoSanita Contenty-types",
    )


class IoSanitaContenttypesControlPanel(controlpanel.ControlPanelFormWrapper):
    form = IoSanitaContenttypesSettingsForm
