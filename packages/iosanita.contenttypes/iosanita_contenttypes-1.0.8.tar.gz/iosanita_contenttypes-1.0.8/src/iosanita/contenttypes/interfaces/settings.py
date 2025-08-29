from iosanita.contenttypes import _
from plone.restapi.controlpanels.interfaces import IControlpanel
from zope.interface import Interface
from zope.schema import Bool


class IIoSanitaContenttypesSettingsControlpanel(IControlpanel):
    """ """


class IIoSanitaContenttypesSettings(Interface):
    """
    Control panel settings
    """

    show_modified_default = Bool(
        title=_("show_modified_default_label", default="Mostra la data di modifica"),
        description=_(
            "show_modified_default_help",
            default="Questo è il valore di default per decidere se mostrare "
            "o meno la data di modifica nei contenuti che hanno la behavior "
            "abilitata. E' poi possibile sovrascrivere il default nei singoli "
            'contenuti (nel tab "Impostazioni").',
        ),
        default=True,
        required=False,
    )

    enable_struttura_related_people = Bool(
        title=_(
            "enable_struttura_related_people_label",
            default="Abilita la visualizzazione delle Persone correlate ad una Struttura",
        ),
        description=_(
            "enable_struttura_related_people_help",
            default="Questo è il valore di default per decidere se mostrare "
            "o meno i contenuti Persona correlati con i contenuti Struttura "
            'tramite i campi "dove opera" o "dove riceve".',
        ),
        default=False,
        required=False,
    )
