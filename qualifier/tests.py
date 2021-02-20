from otree.api import Currency as c, currency_range, Submission
from .pages import *
from ._builtin import Bot
import random
from string import ascii_lowercase


def method_capturer(method, **kwargs):
    p = kwargs.get('player')
    page = kwargs.get('page_class').__name__
    # todo: add page to task to distinguish between practice and real tasks
    cur_task = p.get_or_create_task()
    # TODO randomize the strategy
    cor_answer = cur_task.correct_answer
    random_answer = random.sample(ascii_lowercase, k=5)
    answer = random.choice([cor_answer, random_answer])
    method(p.id_in_group, {'answer': answer})


class PlayerBot(Bot):

    def call_method(self, page_class):
        live_method_name = page_class.live_method

        def method(id_in_group, data):
            return getattr(self.player, live_method_name)(data)

        method_capturer(
            method=method,
            case=self.case,
            round_number=self.round_number,
            page_class=page_class,
            player=self.player
        )

    def play_round(self):
        for i in range(5):
            self.call_method(RET)
        yield Submission(RET, check_html=False)
