from otree.api import Currency as c, currency_range, Submission,SubmissionMustFail
from .pages import *
from qualifier.generic_tests import PlayerBot as Bot
import random
from numpy.random import multinomial
import numpy as np


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number==1:
            yield RoleAnnouncement
        for i in range(random.randint(3, 5)):
            self.call_method(RET)
        yield Submission(WorkingRET, check_html=False)
        n = 3
        m = self.group.total_bonus
        wrong_bonuses = np.random.multinomial(m+100, np.ones(n) / n)
        bonuses = np.random.multinomial(m, np.ones(n) / n)
        keys = [f'bonus_{i}' for i in Constants.subtypes]
        if self.player.role() == Role.manager:
            yield SubmissionMustFail(BonusDistribution, dict(zip(keys, wrong_bonuses)))
            yield BonusDistribution, dict(zip(keys, bonuses))
        random.seed()
        if self.player.role() == Role.worker:
            yield Allocation, {'allocation': random.randint(0, self.player.pgg_endowment)}
