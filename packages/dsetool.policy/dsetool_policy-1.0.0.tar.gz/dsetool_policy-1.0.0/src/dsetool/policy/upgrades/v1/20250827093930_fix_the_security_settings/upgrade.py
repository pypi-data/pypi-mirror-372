from Acquisition import aq_base
from ftw.upgrade import UpgradeStep
from plone import api


class FixTheSecuritySettings(UpgradeStep):
    """Fix the security settings.
    _Access_contents_information_Permission
    _Modify_portal_content_Permission
    _View_Permission

    """

    def __call__(self):
        permissions_attributes = [
            "_Access_contents_information_Permission",
            "_Modify_portal_content_Permission",
            "_View_Permission",
        ]

        brains = api.content.find(
            portal_type=[
                "euphorie.choice",
                "euphorie.recommendation",
                "euphorie.option",
            ]
        )

        for brain in brains:
            obj = brain.getObject()
            obj_base = aq_base(obj)

            for permission in permissions_attributes:
                try:
                    delattr(obj_base, permission)
                except AttributeError:
                    pass

            obj.reindexObjectSecurity()
