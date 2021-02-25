from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Role
from qualifier.pages import RET
from django.db.models import Sum


class FirstWP(WaitPage):
    def is_displayed(self):
        return self.round_number == 1

    wait_for_all_groups = True
    after_all_players_arrive = 'after_everyone_arrived'


class RoleAnnouncement(Page):
    def is_displayed(self):
        return self.round_number == 1


class Quiz(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.cq_err_counter = self.player.cqs.filter(answer__isnull=False).aggregate(s=Sum('counter'))['s']


class Allocation(Page):
    pass


class WorkingRET(RET):
    template_name = 'qualifier/RET.html'

    def __init__(self):
        return self.player.role() == Role.worker or self.round_number == 1

    def before_next_page(self):
        super().before_next_page()
        self.player.set_shock_and_realized_output()


class BeforeBonusDistributionWP(WaitPage):
    after_all_players_arrive = 'set_bonus_pool'


class BonusDistribution(Page):
    form_model = 'group'

    def is_displayed(self):
        return self.player.role() == Role.manager

    def get_form_fields(self):
        return [f'bonus_{i}' for i in Constants.subtypes]

    def error_message(self, values):
        tot = sum([v for v in values.values()])
        if tot != self.group.total_bonus:
            return 'You should distribute the entire bonus among the workers'


class AfterBonusDistributionWP(WaitPage):
    pass


class Allocation(Page):
    form_fields = ['allocation']
    form_model = 'player'

    def is_displayed(self):
        return self.player.role() == Role.worker


class AfterAllocationWP(WaitPage):
    after_all_players_arrive = 'set_payoffs'


page_sequence = [
    # FirstWP,
    # RoleAnnouncement,
    Quiz,
    # WorkingRET,
    # BeforeBonusDistributionWP,
    # BonusDistribution,
    # AfterBonusDistributionWP,
    # Allocation,
    # AfterAllocationWP,

]
