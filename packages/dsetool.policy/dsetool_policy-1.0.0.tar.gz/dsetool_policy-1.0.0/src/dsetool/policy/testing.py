from osha.oira.testing import OiRAFixture
from plone.app.testing import IntegrationTesting


class DSEToolPolicyFixture(OiRAFixture):

    def setUpZope(self, app, configurationContext):
        super().setUpZope(app, configurationContext)

        import dsetool.policy

        self.loadZCML(package=dsetool.policy, context=configurationContext)

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        self.applyProfile(portal, "dsetool.policy:default")


DSETOOL_POLICY_FIXTURE = DSEToolPolicyFixture()

DSETOOL_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DSETOOL_POLICY_FIXTURE,),
    name="DSEToolPolicyLayer:IntegrationTesting",
)
