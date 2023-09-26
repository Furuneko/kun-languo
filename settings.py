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
    err_msg="That answer was incorrect, please try again!",
    corr_msg="Well done! The correct answer is:",
    practice_time_sec=60,
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
        name='transp_no_info',
        display_name="Transparent + No Info (baseline)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=False,
        heterogenous=False,
        info=False,
        allocation_task=False
    ),
    dict(
        name='transp_info',
        display_name="Transparent + Info",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=False,
        heterogenous=False,
        info=True,
        allocation_task=False
    ),
    dict(
        name='secret_no_info',
        display_name="Secret + No Info",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=True,
        heterogenous=False,
        info=False,
        allocation_task=False
    ),
    dict(
        name='secret_info',
        display_name="Secret + Info",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=True,
        heterogenous=False,
        info=True,
        allocation_task=False
    ),
    dict(
        name='baseline',
        display_name="Transparent + homogeneous (baseline)",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=False,
        heterogenous=False,
        info=False,
        allocation_task=True
    ),
    dict(
        name='secret_homo',
        display_name="Secret + homogeneous",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=True,
        heterogenous=False,
        info=False,
        allocation_task=True
    ),
    dict(
        name='transp_hetero',
        display_name="Transparent + heterogeneous",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=False,
        heterogenous=True,
        info=False,
        allocation_task=True
    ),
    dict(
        name='secret_hetero',
        display_name="Secret + heterogeneous",
        num_demo_participants=4,
        app_sequence=app_sequence,
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
        **some_defaults,
        secret=True,
        heterogenous=True,
        info=False,
        allocation_task=True
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=.25,
    participation_fee=12.00,
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
