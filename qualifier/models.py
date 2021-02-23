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



class Subsession(BaseSubsession):
    def creating_session(self):
        self.session.vars['task_fun'] = getattr(ret_functions, self.session.config['task'])
        self.session.vars['task_params'] = self.session.config.get('task_params', {})


class Group(BaseGroup):
    pass


class Player(RETPlayer):

    def set_payoff(self):
        self.payoff = self.num_tasks_correct * self.session.config.get('performance_fee')


class Task(GeneralTask):
    player = djmodels.ForeignKey(to=Player, related_name='tasks', on_delete=djmodels.CASCADE)
