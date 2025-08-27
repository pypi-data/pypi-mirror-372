from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer

import cs.translator.elhuyar


class CsTranslatorElhuyarLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=cs.translator.elhuyar)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "cs.translator.elhuyar:default")


CS_TRANSLATOR_ELHUYAR_FIXTURE = CsTranslatorElhuyarLayer()


CS_TRANSLATOR_ELHUYAR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CS_TRANSLATOR_ELHUYAR_FIXTURE,),
    name="CsTranslatorElhuyarLayer:IntegrationTesting",
)


CS_TRANSLATOR_ELHUYAR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CS_TRANSLATOR_ELHUYAR_FIXTURE,),
    name="CsTranslatorElhuyarLayer:FunctionalTesting",
)
