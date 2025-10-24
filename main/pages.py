from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Role
from qualifier.pages import RET
from django.db.models import Sum

#
class FirstPage(Page):
    def is_displayed(self):
        return self.round_number == 1


class FirstWP(WaitPage):
    body_text = 'Please wait until all participants have reviewed their performance before moving on.'

    def is_displayed(self):
        return self.round_number == 1

    wait_for_all_groups = True
    after_all_players_arrive = 'after_everyone_arrived'


class WorkerAnnounceNextPeriod(Page):
    def is_displayed(self):
        return self.player.role() == Role.worker and self.round_number > 1


class RoleAnnouncement(FirstPage):
    pass


class BackgroundStage2(FirstPage):
    pass


class WorkerAbilityExplained(FirstPage):
    pass


class ShockExplained(FirstPage):
    pass


class RealizedOutputExplained(FirstPage):
    pass


class WorkerBonusesExplained(FirstPage):
    pass


class ManagerBonusesExplained(FirstPage):
    pass


class BonusDistributionExplained(FirstPage):
    pass


class PaymentExplained(FirstPage):
    pass


class Quiz(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.cq_err_counter = self.player.cqs.filter(answer__isnull=False).aggregate(s=Sum('counter'))['s']


class BeforeWorkingRETWP(WaitPage):
    pass


class BeforeRETAnnouncement(FirstPage):
    pass


class WorkingRET(RET):
    template_name = 'qualifier/RET.html'

    def title(self):
        return f'Decode Task – Period {self.round_number}'

    def vars_for_template(self):
        return dict(show_worker_subtype=True if self.player.role() == Role.worker else False)

    def is_displayed(self):
        return self.player.role() == Role.worker or self.round_number == 1

    def before_next_page(self):
        self.player._num_tasks_attempted = self.player.num_tasks_attempted(page_name='WorkingRET')
        self.player._num_tasks_correct = self.player.num_tasks_correct(page_name='WorkingRET')
        self.player._num_tasks_total = self.player.num_tasks_total(page_name='WorkingRET')
        self.player.set_payoff()
        self.player.set_shock_and_realized_output()


class RETResults(Page):
    def is_displayed(self):
        return self.player.role() == Role.worker or self.round_number == 1

    def vars_for_template(self):
        return dict(
            correct_ret_tasks=self.player.num_tasks_correct(page_name='WorkingRET')
        )


class ShockAnnouncement(Page):
    def vars_for_template(self):
        p_shocked = [p for p in self.group.get_players() if p.is_shocked]

        correct_ret_tasks = p_shocked[0]._num_tasks_correct if p_shocked else 0
        return dict(
            correct_ret_tasks=correct_ret_tasks,
            is_shocked=self.player.is_shocked
        )

    # UPDATE
    def is_displayed(self):
        return self.player.is_shocked or not self.player.is_worker or self.participant.vars['treatments']['performance'] == Constants.TREATMENT_PERFORMANCE[-1]


class AfterWorkingRETWP(WaitPage):
    after_all_players_arrive = 'set_bonus_pool'


class BonusDistribution(Page):
    form_model = 'group'

    def vars_for_template(self):
        form = self.get_form()
        workers = self.group.get_workers()
        inputs = [dict(label=f'{w.role_desc()} {w.worker_subtype} {w.get_shock_msg()}',
                       work_result=w.realized_output,
                       name=f'bonus_{w.worker_subtype}') for w in workers
                  ]

        return dict(form_data=zip(workers, form), inputs=inputs)

    def is_displayed(self):
        participant = self.participant
        return self.player.role() == Role.manager

    def get_form_fields(self):
        return [f'bonus_{i}' for i in Constants.subtypes]

    def error_message(self, values):
        tot = sum([v for v in values.values()])
        if tot != self.group.total_bonus:
            return 'You should distribute the entire bonus among the workers'

    def before_next_page(self):
        for w in self.group.get_workers():
            w.bonus = getattr(self.group, f'bonus_{w.worker_subtype}')


class BonusDistributionInfo(Page):

    def vars_for_template(self):
        employees_info = [
            dict(
                role_desc=e.role_desc,
                worker_subtype=e.worker_subtype,
                realized_output=e.realized_output,
                event='Positively' if e.shock > 0 else 'Negatively' if e.shock < 0 else ''
            )
            for e in self.group.get_workers()
        ]

        return dict(
            employees_info=employees_info
        )

    def is_displayed(self):
        return self.player.role() == Role.worker and self.participant.vars['treatments']['performance'] != Constants.TREATMENT_PERFORMANCE[0]


class AfterBonusDistributionWP(WaitPage):
    def vars_for_template(self):
        if self.player.is_worker:
            body_text = f'Please wait while your Manager makes their bonus allocation decisions for Period {self.round_number}.'
            return dict(body_text=body_text)


class BonusInfo(Page):
    pass


class Allocation(Page):
    form_model = 'player'

    def get_form_fields(self):
        fields = ['public_allocation', 'self_allocation']
        if self.round_number == 1:
            fields.append('confirm_understanding')
        return fields

    def vars_for_template(self):
        """
        endowment: 20,
      coef: 2,
      workers: [
        { name: "worker A", selfalloc: null, publicalloc: 0, earning: 0 },
        { name: "worker B", selfalloc: null, publicalloc: 0, earning: 0 },
        { name: "worker C", selfalloc: null, publicalloc: 0, earning: 0 }
      ]

        """
        workers = [dict(name=f'{w.role_desc()} {w.worker_subtype}', selfalloc=None,
                        publicalloc=0, earning=0) for w in self.group.get_workers()]
        return dict(next_round=self.round_number + 1, workers=workers, confirm_understanding_label=Constants.confirm_understanding_label)

    def error_message(self, values):
        tot = sum([v for k, v in values.items() if k in ['public_allocation', 'self_allocation']])
        if tot != self.player.pgg_endowment:
            return f'You have to allocate the {self.player.pgg_endowment}  between ' \
                   f'the “self” account and “public” account '

    def is_displayed(self):
        return self.player.role() == Role.worker and self.session.config['allocation_task']


class AfterAllocationWP(WaitPage):
    def vars_for_template(self):
        if self.player.role() == Role.manager:
            return dict(
                body_text=f'This concludes Period {self.round_number}. Please wait for the three employees to complete the period to proceed to Period {self.round_number + 1}. ')

    after_all_players_arrive = 'set_payoffs'


class ManagerExplanation(Page):
    # form_fields = ['non_equal_splitting', 'allocation_explanation']
    form_model = 'player'

    timer_text = "Time left to complete this period:"

    def get_timeout_seconds(self):
        return self.session.config.get('working_time_sec', Constants.WORKING_TIME_SEC)

    def vars_for_template(self):
        return dict(
            prev_period=self.round_number - 1,
            prev_group=self.group.in_round(self.round_number - 1)
        )

    def js_vars(self):
        time_left = self.player.get_time_left('manager_explanation', 60 * Constants.max_minutes_manager_explanation)
        return dict(time_left=time_left)

    def is_displayed(self):
        return self.player.role() == Role.manager and self.round_number > 1


class LastManagerExplanation(Page):
    form_fields = ['last_non_equal_splitting', 'last_allocation_explanation']
    form_model = 'player'

    def js_vars(self):
        time_left = self.player.get_time_left('last_manager_explanation', 60 * Constants.max_minutes_manager_explanation)
        return dict(time_left=time_left)

    def is_displayed(self):
        return self.player.role() == Role.manager and self.round_number == Constants.num_rounds


page_sequence = [
    FirstWP,
    WorkerAnnounceNextPeriod,
    RoleAnnouncement,
    BackgroundStage2,
    WorkerAbilityExplained,
    ShockExplained,
    RealizedOutputExplained,
    WorkerBonusesExplained,
    ManagerBonusesExplained,
    BonusDistributionExplained,
    PaymentExplained,
    Quiz,
    BeforeWorkingRETWP,
    BeforeRETAnnouncement,
    WorkingRET,
    ManagerExplanation,
    AfterWorkingRETWP,
    RETResults,
    ShockAnnouncement,
    BonusDistribution,
    BonusDistributionInfo,
    AfterBonusDistributionWP,
    BonusInfo,
    Allocation,
    AfterAllocationWP,
    # LastManagerExplanation,
]
