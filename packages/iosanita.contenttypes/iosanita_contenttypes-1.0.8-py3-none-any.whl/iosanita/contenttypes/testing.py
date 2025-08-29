from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE
from redturtle.volto.testing import RedturtleVoltoLayer
from zope.configuration import xmlconfig

import collective.address
import collective.geolocationbehavior
import collective.taxonomy
import collective.volto.blocksfield
import collective.volto.enhancedlinks
import collective.z3cform.datagridfield
import iosanita.contenttypes
import iosanita.contenttypes.adapters
import kitconcept.seo
import plone.app.caching
import plone.formwidget.geolocation
import plone.restapi
import redturtle.bandi


class TestLayer(RedturtleVoltoLayer):
    def setUpZope(self, app, configurationContext):
        super().setUpZope(app, configurationContext)
        self.loadZCML(package=collective.taxonomy)
        self.loadZCML(package=collective.volto.blocksfield)
        self.loadZCML(package=collective.volto.enhancedlinks)
        self.loadZCML(package=collective.z3cform.datagridfield)
        self.loadZCML(package=kitconcept.seo)
        self.loadZCML(package=plone.formwidget.geolocation)
        self.loadZCML(package=collective.geolocationbehavior)
        self.loadZCML(package=redturtle.bandi)
        self.loadZCML(package=collective.address)
        self.loadZCML(package=iosanita.contenttypes, context=configurationContext)
        xmlconfig.file(
            "configure.zcml",
            iosanita.contenttypes,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        applyProfile(portal, "iosanita.contenttypes:default")


FIXTURE = TestLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="IoSanitaContenttypesLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name="IoSanitaContenttypesLayer:FunctionalTesting",
)

RESTAPI_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="IoSanitaContenttypesLayer:RestAPITesting",
)
