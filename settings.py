# TODO:
#  - Check ShockAnnouncement.html
#       -> how to display realized outputs to affected Employee?
#  - Check BonusDistribution.html
#       -> not displayed if pay == 'Transparency' and performance in ['Partial Transparency', 'Transparency']?


from os import environ

EXTENSION_APPS = ['main']
some_defaults = dict(
    wilfrid_laurier_university=False,
    western_university=True,
    stage1_fee=1,
    stage2_fee=10,
    worker_share=0.3,
    manager_share=0.1,
    pgg_coef=2,
    pgg_endowment=10,
    err_msg="That anwer was incorrect, please try again!",
    corr_msg="Well done! The correct answer is:",
    practice_time_sec=120,
    working_time_sec=120,
    debug=True,
)
app_sequence = [
    'intro',
    'qualifier',
    'main',
    'peq',
    'exitapp'
]
SESSION_CONFIGS = [
    dict(
        name='pay_secrecy_performance_secrecy',
        display_name="Pay (Secrecy) + Performance (Secrecy)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        pay='Secrecy',
        performance='Secrecy',
        secret=False,
        heterogenous=False,
        info=True,
        allocation_task=False
    ),
    dict(
        name='pay_secrecy_performance_partial_transp',
        display_name="Pay (Secrecy) + Performance (Partial Transparency)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        pay='Secrecy',
        performance='Partial Transparency',
        secret=False,
        heterogenous=False,
        info=True,
        allocation_task=False
    ),
    dict(
        name='pay_secrecy_performance_transp',
        display_name="Pay (Secrecy) + Performance (Transparency)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        pay='Secrecy',
        performance='Transparency',
        secret=False,
        heterogenous=False,
        info=True,
        allocation_task=False
    ),
    dict(
        name='pay_transp_performance_secrecy',
        display_name="Pay (Transparency) + Performance (Secrecy)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        pay='Transparency',
        performance='Secrecy',
        heterogenous=False,
        secret=False,
        info=False,
        allocation_task=False
    ),
    dict(
        name='pay_transp_performance_partial_transp',
        display_name="Pay (Transparency) + Performance (Partial Transparency)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        pay='Transparency',
        performance='Partial Transparency',
        heterogenous=False,
        secret=False,
        info=False,
        allocation_task=False
    ),
    dict(
        name='pay_transp_performance_transp',
        display_name="Pay (Transparency) + Performance (Transparency)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        pay='Transparency',
        performance='Transparency',
        secret=False,
        heterogenous=False,
        info=True,
        allocation_task=False
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=.20,
    participation_fee=5.00,
    doc="",
    use_browser_bots=False
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'CDN'
USE_POINTS = True
POINTS_CUSTOM_NAME='Liras'

ROOMS = [
    dict(
        name='virtual_lab',
        display_name='Virtual Lab',
        participant_label_file='_rooms/virtual_lab.txt'
    ),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'qq694yy)3)w-=_83_lul-1ts14f_)q+6sdbhn#r4%p-i#_fout'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree', 'qualifier']
