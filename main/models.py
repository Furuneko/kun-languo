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
import yaml
from django.urls import reverse_lazy, reverse
from django.utils.html import mark_safe
import json
import time

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
    # some fallbacks here JIC
    CQ_ERR_DEFAULT_MSG = "That answer was incorrect, please try again!"
    CQ_CORR_DEFAULT_MSG = "Well done! The correct answer is:"
    DEFAULT_PGG_ENDOWMENT = 20
    num_rounds = len(shocks)
    max_minutes_manager_explanation = 2
    confirm_understanding_label = mark_safe("<b>I confirm that I understand the allocation game.</b>")
    subtypes = ('A', 'B', 'C')
    with open(r'./data/quiz.yaml') as file:
        cqs = yaml.load(file, Loader=yaml.FullLoader)

    type_correspondence = {Role.manager: 'Manager', Role.worker: 'Employee'}


class Subsession(BaseSubsession):
    shock_size = models.IntegerField()
    shock_worker_subtype = models.StringField(choices=Constants.subtypes)

    def shock_direction(self):
        return 'positive' if self.shock_size > 0 else 'negative'

    def creating_session(self):
        candidate = Constants.shocks[self.round_number - 1]
        shock, _ = Shock.objects.get_or_create(round_number=self.round_number, defaults=candidate)
        self.shock_size = int(shock.size)
        self.shock_worker_subtype = shock.worker_subtype
        if self.round_number == 1:
            qs = []

            for p in self.get_players():
                for q in Constants.cqs:
                    treatment = q.get('treatment')
                    # we kinda assume here that the condition is stable within a session. so this can be sped up a bit
                    addable = True
                    if treatment:
                        for i in treatment:
                            for k, v in i.items():
                                if self.session.config.get(k) != v:
                                    addable = False
                    if addable:
                        qs.append(CQ(label=q.get('label'),
                                     choices=json.dumps(q.get('choices')),
                                     correct=q.get('correct'),
                                     hint=q.get('hint'),
                                     owner=p
                                     )
                                  )
            CQ.objects.bulk_create(qs)

            for p in self.get_players():
                p.payable_round = random.randint(1, Constants.num_rounds)
        else:
            for p in self.get_players():
                p.payable_round = p.in_round(1).payable_round

    def after_everyone_arrived(self):
        """What we do here:
        1. We annotate all participants using their players from qualifier data num of correct tasks.
        2. we sort them based on this annotation.
        3. we split them into two categories (top-25 etc).
        4. assign manager role to top-25 and workers to bottom-75
        5.  workers (still sorted by ability) are divided into chunks of three.
        6. managers shuffled.
        7. manager+chunks of 3 workers are zipped into groups of 4
        8. workers get subtype (A,B,C) randomly
        9. we assign new group matrix
        """
        self.get_group_matrix()
        subtypes = cycle(Constants.subtypes)
        for p in self.player_set.all():
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
        for p in self.player_set.all():
            p._is_frozen = True
        self.set_group_matrix(semi_groups)
        allothers = Player.objects.filter(session=self.session).exclude(subsession=self)
        for i in allothers:
            i.inner_role = i.in_round(1).inner_role
            i.worker_subtype = i.in_round(1).worker_subtype
        Player.objects.bulk_update(allothers, ['worker_subtype', 'inner_role'], batch_size=100)
        Player.objects.filter(session=self.session, inner_role=Role.worker).update(
            pgg_endowment=self.session.config.get('pgg_endowment', Constants.DEFAULT_PGG_ENDOWMENT))
        for subsession in self.in_rounds(2, Constants.num_rounds):
            subsession.group_like_round(1)


class Group(BaseGroup):
    bonus_A = models.IntegerField(min=0)
    bonus_B = models.IntegerField(min=0)
    bonus_C = models.IntegerField(min=0)
    total_bonus = models.IntegerField()
    total_output = models.IntegerField()
    pgg_total_contribution = models.CurrencyField()
    pgg_individual_share = models.CurrencyField()

    def get_workers(self):
        return self.player_set.filter(inner_role=Role.worker).order_by('worker_subtype')

    def set_bonus_pool(self):

        self.total_output = sum([i.realized_output or 0 for i in self.get_workers()])
        stage2_fee = self.session.config.get('stage2_fee')
        worker_share = self.session.config.get('worker_share')
        self.total_bonus = int(round(worker_share * self.total_output * stage2_fee))

        manager_share = self.session.config.get('manager_share')
        manager = self.get_player_by_role(Role.manager)
        manager.raw_payoff = int(manager_share * self.total_output*stage2_fee)
        manager.save()

    def set_payoffs(self):

        for i in self.get_workers():
            i.raw_payoff = getattr(self, f'bonus_{i.worker_subtype}')
            i.save()
        self.set_pgg_payoffs()
        if self.round_number == Constants.num_rounds:
            self.set_final_payoffs()

    def set_final_payoffs(self):
        for p in self.get_players():
            payable = p.in_round(p.payable_round)
            p.payoff = payable.raw_payoff + payable.pgg_payoff
            stage1_payoff = p.participant.vars.get('stage1payoff', 0)
            total_payoff = c(stage1_payoff + p.payoff).to_real_world_currency(self.session)
            r = dict(
                payable_round=p.payable_round,
                stage2_work_bonus=c(payable.raw_payoff),
                stage2_allocation_bonus=c(payable.pgg_payoff),
                total_payoff=total_payoff,
                is_worker=p.is_worker,
            )
            p.participant.vars.update(**r)

    def set_pgg_payoffs(self):

        self.pgg_total_contribution = sum([i.public_allocation for i in self.get_workers()])
        coef = self.session.config.get('pgg_coef', 0)
        self.pgg_individual_share = self.pgg_total_contribution * coef / 3
        for p in self.get_workers():
            p.pgg_payoff = p.pgg_endowment - p.public_allocation + self.pgg_individual_share


class Player(RETPlayer):
    non_equal_splitting = models.BooleanField()
    allocation_explanation = models.LongStringField()
    last_non_equal_splitting = models.BooleanField()
    last_allocation_explanation = models.LongStringField()
    inner_role = models.StringField()
    worker_subtype = models.StringField()
    shock = models.IntegerField(default=0)
    raw_payoff = models.IntegerField(default=0)
    payable_round = models.IntegerField(min=1, max=Constants.num_rounds)
    realized_output = models.IntegerField()
    confirm_understanding = models.BooleanField(widget=widgets.CheckboxInput)
    self_allocation = models.IntegerField(min=0)
    public_allocation = models.IntegerField(min=0)

    def self_allocation_max(self):
        return self.pgg_endowment

    def public_allocation_max(self):
        return self.pgg_endowment

    pgg_endowment = models.CurrencyField(initial=0)
    pgg_payoff = models.CurrencyField(initial=0)
    cq_err_counter = models.IntegerField(initial=0)
    bonus = models.IntegerField()

    @property
    def is_worker(self):
        return self.role() == Role.worker

    def get_shock_msg(self):
        if not self.is_shocked:
            return ''
        direction  = 'positively' if self.shock >0 else 'negatively'
        return f'({direction} affected by uncontrollable event)'

    @property
    def is_shocked(self):
        return self.shock != 0

    def role_desc(self):
        # TODO: later on move to session.config
        return Constants.type_correspondence[self.role()]

    def set_shock_and_realized_output(self):
        if self.subsession.shock_worker_subtype == self.worker_subtype:
            self.shock = self.subsession.shock_size
        self.realized_output = max(self.num_tasks_correct(page_name='WorkingRET') + self.shock, 0)

    def role(self):
        if self.session.config.get('debug'):
            if self.id_in_group == 1:
                return Role.manager
            return Role.worker

        return self.inner_role

    def get_quiz_url(self):
        available_q = self.cqs.filter(answer__isnull=True).first()

        if not available_q:
            return reverse('no_more_cqs', kwargs=dict(participant_code=self.participant.code))
        return available_q.get_absolute_url()

    def get_time_left(self, page_name, timer):
        time_start = self.participant.vars.setdefault(f'time_left_{page_name}_{self.round_number}', time.time())
        return timer - (time.time() - time_start)


class Task(GeneralTask):
    player = djmodels.ForeignKey(to=Player, related_name='tasks', on_delete=djmodels.CASCADE)


class Shock(djmodels.Model):
    round_number = models.IntegerField()
    worker_subtype = models.StringField(choices=Constants.subtypes)
    size = models.IntegerField()

    def __str__(self):
        return f'Shock at {self.worker_subtype} of a size {self.size} in round {self.round_number}'


class CQ(djmodels.Model):
    class Meta:
        ordering = ['pk']

    """Actual cq for specific player. stores the number of wrong answers."""
    owner = djmodels.ForeignKey(to=Player, on_delete=djmodels.CASCADE, related_name="cqs")
    counter = models.IntegerField(initial=0)
    answer = models.IntegerField()
    label = models.StringField()
    choices = models.StringField()
    correct = models.IntegerField()
    explained = models.BooleanField(initial=False)
    hint = models.StringField()

    def get_absolute_url(self):
        return reverse('single_quiz_question', args=[str(self.id)])
