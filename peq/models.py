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
    name_in_url = 'peq'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


from .widgets import LikertWidget
from .fields import LikertField

FairParams = dict(choices=list(range(1, 8)),
                  headers={1: "Not at all", 4: "Somewhat",
                           7: "Very much"})
AgreeParams = dict(choices=list(range(1, 8)),
                   headers={1: "Strongly disagree", 4: "Neither disagree nor agree",
                            7: "Strongly agree"})


class Player(BasePlayer):
    w1_1 = LikertField(label='1. Did your Manager allocate the employee bonus pool fairly?', **FairParams)
    w1_2 = models.LongStringField(
        label='2. Please explain your above opinion about the fairness of the Manager’s bonus allocation?')
    w2_1 = LikertField(
        label='3. In my opinion, the Manager should allocate the employee bonus pool equally among the three employees.',
        **AgreeParams)
    w2_2 = LikertField(
        label='4. In my opinion, the Manager should allocate the employee bonus pool mainly based on the employees’ realized output.',
        **AgreeParams
    )
    w2_3 = LikertField(
        label='5. In my opinion, the Manager should make adjustment for employees who are <i>positively</i> affected by the uncontrollable events.',
        **AgreeParams
    )
    w2_4 = LikertField(
        label='6. In my opinion, the Manager should make an adjustment for employees who are <i>negatively</i> affected by the uncontrollable events',
        **AgreeParams
    )
    w2_5 = models.LongStringField(label="""
    Please briefly explain your reasoning behind your response to Q5 and Q6. Specifically, if and how do you think a Manager 
    should adjust employee bonuses considering the effect of uncontrollable events?""")
    w3_1 = LikertField(
        label="""8. Was it important to you to compare your bonuses with the other employees’ bonuses?""", **FairParams)
    w3_2 = LikertField(
        label="""8. If you had the information, would it be important to you to compare your bonuses with the other employees’ bonuses?""",
        **FairParams)
    w3_3 = models.LongStringField(label="""
    9.	If you changed your effort level on the decode task over the 8 periods, please explain how and why you made the change:""")
    w4_1 = LikertField(
        label='10.	Did the other employees in your firm put in a fair amount of effort?', **FairParams)
    w4_2 = LikertField(
        label='11.	Would you trust working with the other employees in your firm again?', **FairParams)
    w4_3 = LikertField(
        label='12.	Would you trust working for your Manager again?', **FairParams)
    m1_1 = models.LongStringField(label="""
    1.	What process did you use to distribute the employee bonus pool among your three employees? Please briefly explain your strategy""")
    m2_1 = LikertField(
        label='2. In your opinion, should the Manager consider the effects of the uncontrollable events while allocating the employee bonus pool?',
        choices=list(range(1, 8)),
        headers={1: "Not consider at all", 4: "Sometimes ",
                 7: "Definitely consider"}
    )
    m2_2 = models.LongStringField(
        label="""
        3.	Please briefly elaborate on your response to the last question.
         Specifically, if your answer is positive, then how do you think the Manager 
         should adjust for uncontrollable events when allocating bonuses? If your answer is negative, 
         why do you think the Manager should not adjust for uncontrollable events when allocating bonuses?""")
    m3_1 = LikertField(
        label="""4.	In my opinion, the Manager should allocate the employee bonus pool equally among the three employees""",
        **AgreeParams)
    m3_2 = LikertField(
        label="""5.	In my opinion, the Manager should allocate the employee bonus pool mainly based on the employees’ realized output.""",
        **AgreeParams)
    m3_3 = LikertField(label="""
       6.	In my opinion, the Manager should make adjustment for employees who are <i>positively</i> affected by the uncontrollable events?""",
                       **AgreeParams)
    m3_4 = LikertField(
        label='7.	In my opinion, the Manager should make adjustment for employees who are <i>negatively</i> affected by the uncontrollable events?',
        **AgreeParams)
    m3_5 = models.LongStringField(label="""
       Please briefly explain your reasoning behind your response to Q6 and Q7. Specifically, if and how do you think a 
       Manager should make bonus adjustments considering the effect of uncontrollable events?""")
    m4_1 = LikertField(
        label=""" a. Assign the bonus pool to best reflect the employees’ realized output?""", **FairParams)
    m4_2 = LikertField(
        label=""" b. Assign the bonus pool to best reflect the employees’ effort?""", **FairParams)
    m4_3 = LikertField(label="""
       c. Assign the bonus pool to best reflect the employees’ ability?""", **FairParams)
    m4_4 = LikertField(
        label=' d. Assign the bonus pool in a way that I felt I was able to justify to my employees?', **FairParams)
    m4_5 = LikertField(label="""
       e. Assign the bonus pool in a way that best motivated employees in later periods?""", **FairParams)
    m4_6 = LikertField(label="""
       f. Assign the bonus pool to avoid creating conflicts among the employees?""", **FairParams)
    gender = models.StringField(widget=widgets.RadioSelect, label='1.	What gender do you identify most with?',
                                choices=['a.	Male',
                                         'b.	Female',
                                         'c.	Non-binary',
                                         'd.	Prefer not to Disclose',
                                         ])
    age = models.IntegerField(label='2.	What is your age today (in years):',
                              )
    school_year = models.StringField(widget=widgets.RadioSelect, label='3.	Current academic status:',
                                     choices=['a.	1st year',
                                              'b.	2nd year',
                                              'c.	3rd year',
                                              'd.	4th year',
                                              'e.	5th year',
                                              'f.   Graduate',
                                              'g.	Other',
                                              ]
                                     )
    school_year_other = models.StringField(blank=True, label='If you chose "Other", please specify')
    major = models.StringField(label='4.	What is your academic major? (answer "none" or "undecided" if applicable)')
    experience = models.IntegerField(label="""
    5.	How many months of full-time work experience do you have? Please convert part-time work experience to
     full-time work experience based on the time you worked. """)
