from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class NoConsent(Page):
    def is_displayed(self):
        return not self.participant.vars.get('consent', True)


class Results(Page):
    pass


class PaySlip(Page):
    form_model = 'player'
    form_fields = ['first_name', 'last_name', 'email', 'email_confirm']

    def error_message(self, values):
        email = values.get('email')
        email2 = values.get('email_confirm')
        if email != email2:
            return 'Email addressess are different. Please check your answer'


class Final(Page):
    pass


page_sequence = [
    NoConsent,
    Results,
    PaySlip,
    Final
]
