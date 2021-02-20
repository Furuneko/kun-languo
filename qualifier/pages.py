from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class RET(Page):
    live_method = 'live_ret'

    def vars_for_template(self):
        self.player.get_or_create_task()
        return dict()

    def get_timeout_seconds(self):
        # todo - adjust based on practice or real task page
        return 100

    def before_next_page(self):
        self.player._num_tasks_correct = self.player.num_tasks_correct
        self.player._num_tasks_total = self.player.num_tasks_total
        self.player.set_payoff()


page_sequence = [RET]
