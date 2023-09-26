from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    def is_displayed(self):
        config = self.session.config
        return config['wilfrid_laurier_university'] or config['western_university']

    def before_next_page(self):
        self.participant.vars['consent'] = self.player.consent

    def app_after_this_page(self, upcoming_apps):
        if not self.player.consent:
            return upcoming_apps[-1]


class FirstIntro(Page):
    pass


class RoleExplanation(Page):
    pass


page_sequence = [
    Consent,
    FirstIntro,
    RoleExplanation
]
