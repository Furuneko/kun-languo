from otree.api import Currency as c, currency_range, Submission
from .pages import *
from .generic_tests import PlayerBot as Bot
import random
from string import ascii_lowercase

class PlayerBot(Bot):
    def play_round(self):
        for i in range(random.randint(5,15)):
            self.call_method(RET)
        yield Submission(RET, check_html=False)
