from otree.api import Currency as c, currency_range, Submission, SubmissionMustFail
from .pages import *
from qualifier.generic_tests import PlayerBot as Bot
import random
from numpy.random import multinomial
import numpy as np


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield RoleAnnouncement
        if self.player.role() == Role.worker and self.round_number > 1:
            yield WorkerAnnounceNextPeriod
        if self.player.role() == Role.manager and self.round_number > 1:
            yield ManagerExplanation, {"non_equal_splitting": True, "allocation_explanation": "whoatver else"}
        if self.round_number == 1:
            yield BackgroundStage2,
            yield WorkerAbilityExplained,
            yield ShockExplained,
            yield RealizedOutputExplained,
            yield WorkerBonusesExplained,
            yield ManagerBonusesExplained,
            yield BonusDistributionExplained,
            yield PaymentExplained,
            yield Submission(Quiz, check_html=False)
            yield BeforeRETAnnouncement,
        for i in range(random.randint(3, 5)):
            self.call_method(RET)
        if self.player.role() == Role.worker or self.round_number == 1:
            yield Submission(WorkingRET, check_html=False)
        yield RETResults,
        yield ShockAnnouncement,

        n = 3
        m = self.group.total_bonus
        wrong_bonuses = np.random.multinomial(m + 100, np.ones(n) / n)
        bonuses = np.random.multinomial(m, np.ones(n) / n)
        keys = [f'bonus_{i}' for i in Constants.subtypes]
        if self.player.role() == Role.manager:
            yield SubmissionMustFail(BonusDistribution, dict(zip(keys, wrong_bonuses)), check_html=False)
            yield Submission(BonusDistribution, dict(zip(keys, bonuses)), check_html=False)
        yield BonusInfo
        random.seed()
        if self.player.role() == Role.worker:
            public = random.randint(0, self.player.pgg_endowment)
            r = dict(public_allocation=public,
                     self_allocation=self.player.pgg_endowment - public)
            yield Submission(Allocation, r, check_html=False)

