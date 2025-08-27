from osha.oira.ploneintranet.quaive_create import QuaiveCreateFormMixin
from osha.oira.ploneintranet.quaive_create import QuaiveCreateViewMixin
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView


class QuaiveCreateEuphorieChoiceForm(QuaiveCreateFormMixin, DefaultAddForm):
    pass


class QuaiveCreateEuphorieChoiceView(QuaiveCreateViewMixin, DefaultAddView):
    form = QuaiveCreateEuphorieChoiceForm


class QuaiveCreateEuphorieOptionForm(QuaiveCreateFormMixin, DefaultAddForm):
    pass


class QuaiveCreateEuphorieOptionView(QuaiveCreateViewMixin, DefaultAddView):
    form = QuaiveCreateEuphorieOptionForm


class QuaiveCreateEuphorieRecommendationForm(QuaiveCreateFormMixin, DefaultAddForm):
    pass


class QuaiveCreateEuphorieRecommendationView(QuaiveCreateViewMixin, DefaultAddView):
    form = QuaiveCreateEuphorieRecommendationForm
