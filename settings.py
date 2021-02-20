from os import environ

SESSION_CONFIGS = [
    dict(
        name='qualifier',
        display_name="qualifier",
        num_demo_participants=1,
        app_sequence=['qualifier'],
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
    ),
    dict(
        name='full',
        display_name="full",
        num_demo_participants=4,
        app_sequence=['qualifier', 'main'],
        task='Decoding',
        task_params={'dict_length': 10, 'task_len': 5},
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'qq694yy)3)w-=_83_lul-1ts14f_)q+6sdbhn#r4%p-i#_fout'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
