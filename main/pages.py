from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Role
from qualifier.pages import RET


class FirstWP(WaitPage):
    def is_displayed(self):
        return self.round_number == 1

    wait_for_all_groups = True
    after_all_players_arrive = 'after_everyone_arrived'

class RoleAnnouncement(Page):
    def is_displayed(self):
        return self.round_number==1
class WorkingRET(RET):
    template_name = 'qualifier/RET.html'

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
    FirstWP,
    RoleAnnouncement,
    WorkingRET,
    BeforeBonusDistributionWP,
    BonusDistribution,
    AfterBonusDistributionWP,
    Allocation,
    AfterAllocationWP,

]
