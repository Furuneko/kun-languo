from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from .generic_models import RETPlayer, GeneralTask
from django.db import models as djmodels
from . import ret_functions
from django.db.models import F

author = 'Philip Chapkovski, HSE-Moscow'

doc = """
Real effort task (decoding)
"""


class Constants(BaseConstants):
    name_in_url = 'qualifier'
    players_per_group = None
    num_rounds = 1
    PRACTICE_TIME_SEC = 60
    WORKING_TIME_SEC = 120


class Subsession(BaseSubsession):
    def get_secs_performance(self):
        secs = self.session.config.get('working_time_sec', Constants.WORKING_TIME_SEC)
        mins = int(secs / 60)
        plur = 's' if mins > 1 else ''
        return f'{secs} seconds (or {mins} minute{plur})'

    def creating_session(self):
        self.session.vars['task_fun'] = getattr(ret_functions, self.session.config['task'])
        self.session.vars['task_params'] = self.session.config.get('task_params', {})


class Group(BaseGroup):
    pass


class Player(RETPlayer):

    def set_payoff(self):
        self.payoff = self.num_tasks_correct(page_name='RET') * self.session.config.get('stage1_fee', 0)
        self.participant.vars['stage1payoff'] = self.payoff


class Task(GeneralTask):
    player = djmodels.ForeignKey(to=Player, related_name='tasks', on_delete=djmodels.CASCADE)
