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
import enum
from otree.models import Participant
from django.db.models import Count, Sum
from django.db import models as djmodels
from itertools import cycle
import random
from qualifier.generic_models import RETPlayer, GeneralTask
from csv import DictReader

author = 'Philipp Chapkovski, HSE-Moscow'

doc = """
Your app description
"""


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class MyPerson(Participant):
    _is_frozen = False

    class Meta:
        proxy = True


class Role(str, enum.Enum):
    manager = 'manager'
    worker = 'employee'


class Constants(BaseConstants):
    name_in_url = 'main'
    players_per_group = None
    with open("data/shock.csv") as csvfile:
        shocks = list(DictReader(csvfile))
    num_rounds = len(shocks)
    subtypes = ('A', 'B', 'C')


class Subsession(BaseSubsession):
    def creating_session(self):

        if self.round_number == 1:
            for p in self.get_players():
                p.payable_round = random.randint(1, Constants.num_rounds)
        else:
            for p in self.get_players():
                p.payable_round = p.in_round(1).payable_round

    def after_everyone_arrived(self):
        """What we do here:
        1. We annotate all partiipants using their players from qualifier data num of correct tasks.
        2. we sort them based on this annotation.
        3. we split them into two categroies (top-25 etc).
        4. assign manager role to top-25 and workers to bottom-75
        5.  workers (still sorted by ability) are divided into chunks of three.
        6. managers shuffled.
        7. manager+chunks of 3 woerkes are zipped into groups of 4
        8. workers get subtype (A,B,C) randomly
        9. we assign new group matrix
        """
        self.get_group_matrix()
        subtypes = cycle(Constants.subtypes)
        for p in Player.objects.all():
            p._is_frozen = False

        q = Player.objects.filter(session=self.session, subsession=self).annotate(
            cor_count=Sum('participant__qualifier_player___num_tasks_correct')).order_by('-cor_count')

        first25 = int(q.count() / 4)
        managers = list(q[:first25])
        workers = list(q[first25:])
        random.shuffle(managers)
        for i in managers:
            i.inner_role = Role.manager
        for i in workers:
            i.inner_role = Role.worker

        Player.objects.bulk_update(managers + workers, ['inner_role'])
        chunked_workers = list(chunks(workers, 3))
        updworkers = []
        for i in chunked_workers:
            random.shuffle(i)
            for j in i:
                j.worker_subtype = next(subtypes)
            updworkers.extend(i)
        Player.objects.bulk_update(updworkers, ['worker_subtype'])

        semi_groups = [[i] + j for i, j in
                       zip(managers, chunked_workers)]

        self.set_group_matrix(semi_groups)
        allothers = Player.objects.filter(session=self.session).exclude(subsession=self)
        for i in allothers:
            i.inner_role = i.in_round(1).inner_role
            i.worker_subtype = i.in_round(1).worker_subtype
        Player.objects.bulk_update(allothers, ['worker_subtype', 'inner_role'])
        Player.objects.filter(session=self.session, inner_role=Role.worker).update(
            pgg_endowment=self.session.config.get('pgg_endowment', 0))




class Group(BaseGroup):
    bonus_A = models.IntegerField()
    bonus_B = models.IntegerField()
    bonus_C = models.IntegerField()
    total_bonus = models.IntegerField()
    pgg_total_contribution = models.CurrencyField()
    pgg_individual_share = models.CurrencyField()

    def get_workers(self):
        return self.player_set.filter(inner_role=Role.worker)

    def set_bonus_pool(self):
        total_output = sum([i.realized_output for i in self.get_players()])
        bonus_fee = self.session.config.get('bonus_fee')
        worker_share = self.session.config.get('worker_share')
        self.total_bonus = int(worker_share * total_output * bonus_fee)

    def set_payoffs(self):
        manager_share = self.session.config.get('manager_share')
        manager = self.get_player_by_role(Role.manager)
        workers = self.player_set.filter(inner_role=Role.worker)
        manager.raw_payoff = manager_share * self.total_bonus
        manager.save()
        for i in workers:
            i.raw_payoff = getattr(self, f'bonus_{i.worker_subtype}')
            i.save()
        self.set_pgg_payoffs()
        if self.round_number == Constants.num_rounds:
            self.set_final_payoffs()

    def set_final_payoffs(self):
        for p in self.get_players():
            payable = p.in_round(p.payable_round)
            p.payoff = payable.raw_payoff + payable.pgg_payoff

    def set_pgg_payoffs(self):
        self.pgg_total_contribution = sum([i.allocation for i in self.get_workers()])
        coef = self.session.config.get('pgg_coef', 0)
        self.pgg_individual_share = self.pgg_total_contribution * coef / 3
        for p in self.get_workers():
            p.pgg_payoff = p.pgg_endowment - p.allocation + self.pgg_individual_share


class Player(RETPlayer):
    inner_role = models.StringField()
    worker_subtype = models.StringField()
    shock = models.IntegerField(default=0)
    raw_payoff = models.CurrencyField(default=0)
    payable_round = models.IntegerField(min=1, max=Constants.num_rounds)
    realized_output = models.IntegerField()
    allocation = models.CurrencyField()
    pgg_endowment = models.CurrencyField(initial=0)
    pgg_payoff = models.CurrencyField(initial=0)

    def set_shock_and_realized_output(self):
        current_shock = Constants.shocks[self.round_number - 1]
        if current_shock.get('worker') == self.worker_subtype:
            self.shock = int(current_shock.get('shock'))
        self.realized_output = max(self.num_tasks_correct + self.shock, 0)

    def role(self):
        return self.inner_role


class Task(GeneralTask):
    player = djmodels.ForeignKey(to=Player, related_name='tasks', on_delete=djmodels.CASCADE)
