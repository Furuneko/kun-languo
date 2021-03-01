from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class ExplainingDecodingTask(Page):
    pass


class Practice(Page):
    live_method = 'live_ret'
    practice = True
    template_name = 'qualifier/RET.html'

    def vars_for_template(self):
        self.player.get_or_create_task()
        return dict()

    def get_timeout_seconds(self):
        return self.session.config.get('practice_time_sec', Constants.PRACTICE_TIME_SEC)


class PracticeRETFeedback(Page):
    def vars_for_template(self):
        return dict(
            correct_practice_tasks=self.player.num_tasks_correct(page_name='Practice')
        )


class BeforeRET_WP(WaitPage):
    body_text = 'Please wait until all participants have reviewed their performance before moving on.'


class RETIntro(Page):
    pass





class RET(Page):
    live_method = 'live_ret'

    def vars_for_template(self):
        self.player.get_or_create_task()
        return dict()

    def get_timeout_seconds(self):
        return self.session.config.get('working_time_sec', Constants.WORKING_TIME_SEC)

    def before_next_page(self):
        self.player._num_tasks_correct = self.player.num_tasks_correct(page_name='RET')
        self.player._num_tasks_total = self.player.num_tasks_total(page_name='RET')
        self.player.set_payoff()
class PerformanceRETFeedback(Page):
    def vars_for_template(self):
        return dict(
            correct_ret_tasks=self.player.num_tasks_correct(page_name='RET')
        )

page_sequence = [
    # ExplainingDecodingTask,
    # Practice,
    # PracticeRETFeedback,
    # BeforeRET_WP,
    # RETIntro,
    RET,
    # PerformanceRETFeedback,
]
