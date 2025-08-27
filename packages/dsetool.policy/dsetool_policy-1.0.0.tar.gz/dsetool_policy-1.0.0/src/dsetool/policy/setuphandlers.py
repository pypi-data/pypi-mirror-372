from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "dsetool.policy:uninstall",
        ]

    def getNonInstallableProducts(self):
        return [
            "euphorie.deployment.upgrade",
            "euphorie.deployment",
            "euphorie.upgrade.content.v1",
            "euphorie.upgrade.deployment.v1",
            "euphorie.upgrade.deployment.v18",
            "ftw.upgrade",
            "osha.oira.upgrade.v1",
            "osha.oira.upgrade.v12",
            "osha.oira.upgrade",
            "osha.oira",
            "pas.plugins.ldap.plonecontrolpanel",
            "plone.app.caching",
            "plone.app.discussion",
            "plone.app.imagecropping",
            "plone.app.iterate",
            "plone.app.multilingual",
            "plone.formwidget.recaptcha",
            "plone.patternslib",
            "plone.restapi",
            "plone.session",
            "plone.volto",
            "plonetheme.nuplone",
            "Products.CMFPlacefulWorkflow",
            "Products.membrane",
            "yafowil.plone",
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def post_uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
