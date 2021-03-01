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


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'exitapp'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

from django.db import models as djmodels
class Player(BasePlayer):
    first_name = models.StringField(verbose_name='Your First Name')
    last_name=models.StringField(verbose_name='Your Last Name')
    email = djmodels.EmailField(null=True, verbose_name='Email address')
    email_confirm = djmodels.EmailField(null=True, verbose_name='Re-enter your Email address')
