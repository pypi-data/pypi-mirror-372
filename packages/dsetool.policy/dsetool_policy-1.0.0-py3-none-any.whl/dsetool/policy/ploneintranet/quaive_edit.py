from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin
from plone.dexterity.browser.edit import DefaultEditForm


class ChoiceQuaiveEditForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class OptionQuaiveEditForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class RecommendationQuaiveEditForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""
