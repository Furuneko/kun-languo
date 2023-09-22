from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class GenPage(Page):
    title = 'Post Experimental Questionnaire'
    template_name = 'peq/GenPage.html'
    form_model = 'player'

    def get_form_fields(self):
        class_name = self.__class__.__name__.lower()
        fields = [f.name for f in self.player._meta.get_fields(include_parents=False) if f.name.startswith(class_name)]
        return fields

    def vars_for_template(self):
        return dict(
            comment="""To help us better understand your decisions in Stage Two, please respond to the following questions.  Recall that your identity will remain anonymous and your responses will be kept confidential.""",
            q_lead=''
        )


class MPage(GenPage):
    def is_displayed(self):
        return not self.participant.vars.get('is_worker')

    def vars_for_template(self):
        return dict(
            comment="""Irrespectively to how you actually allocated in the experiment, please indicate the degree 
            to which you agree with the following statements.""",
            q_lead=''
        )


class WPage(GenPage):
    def is_displayed(self):
        return self.participant.vars.get('is_worker')


class W1(WPage):
    pass


class W2(WPage):
    def vars_for_template(self):
        return dict(
            comment="""
            Irrespective of how the employee bonus pool was actually allocated in the experiment, please indicate the degree to which you agree with the following statements:  """

        )


class W3(WPage):
    def get_form_fields(self):
        if self.session.config.get('secret'):
            return ['w3_2', 'w3_3']
        return ['w3_1', 'w3_3']


class W4(WPage):
    pass


class M1(MPage):
    def vars_for_template(self):
        c = super().vars_for_template()
        c['comment'] = """To help us better understand your decisions in Stage Two, 
            please respond to the following questions. Recall that your identity will remain 
            anonymous and your responses will be kept confidential."""
        return c


class M2(MPage):
    pass


class M3(MPage):
    pass


class M4(MPage):
    def vars_for_template(self):
        c = super().vars_for_template()
        c['q_lead'] = ''
        c['comment'] = """When you were allocating the employee bonus pool, to what extend did you 
        try to do the following?"""

        return c


class Demo1(GenPage):
    title = 'Demographics'

    def vars_for_template(self):
        return dict(comment='Please provide some information about yourself:', q_lead='')

    def get_form_fields(self):
        return ['gender', 'age', 'school_year', 'school_year_other', 'major']


class Demo2(GenPage):
    template_name = 'peq/Demo2.html'
    title = 'Demographics'

    def vars_for_template(self):
        return dict(comment='Please provide some information about yourself:', q_lead='')

    def get_form_fields(self):
        return ['experience']


page_sequence = [
    W1,
    W2,
    W3,
    W4,
    M1,
    M2,
    M3,
    # M4,
    Demo1,
    Demo2,
]
