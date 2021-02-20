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
from django.db import models as djmodels
from . import ret_functions
from django.db.models import F

author = 'Philip Chapkovski, HSE-Moscow'

doc = """
Real effort task (decoding)
"""


class Constants(BaseConstants):
    name_in_url = 'qualifier'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    def creating_session(self):
        self.session.vars['task_fun'] = getattr(ret_functions, self.session.config['task'])
        self.session.vars['task_params'] = self.session.config.get('task_params', {})
        for p in self.get_players():
            # TODO: bulk creation
            p.get_or_create_task()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    _num_tasks_correct = models.IntegerField(default=0)
    _num_tasks_total = models.IntegerField(default=0)

    def live_ret(self, data):

        answer = data.get('answer')
        if answer:
            old_task = self.get_or_create_task()
            old_task.answer = answer
            old_task.save()
            new_task = self.get_or_create_task()
            resp = {'task_body': new_task.html_body,
                    'num_tasks_correct': self.num_tasks_correct,
                    'num_tasks_total': self.num_tasks_total,
                    }
            return {self.id_in_group: resp}

    @property
    def num_tasks_correct(self):
        """returns total number of tasks to which a player provided a correct answer"""
        return self.tasks.filter(correct_answer=F('answer')).count()

    @property
    def num_tasks_total(self):
        """returns total number of tasks to which a player provided an answer"""
        return self.tasks.filter(answer__isnull=False).count()

    def get_or_create_task(self):
        """
            checks if there are any unfinished (with no answer) tasks. If yes, we return the unfinished
            task. If there are no uncompleted tasks we create a new one using a task-generating function from session settings
        """
        unfinished_task = self.tasks.filter(answer__isnull=True).first()
        if unfinished_task:
            return unfinished_task
        else:
            task = Task.create(self, self.session.vars['task_fun'], **self.session.vars['task_params'])
            task.save()
            return task


class Task(djmodels.Model):
    # todo: add page to task to distinguish between practice and real tasks
    class Meta:
        ordering = ['-created_at']

    player = djmodels.ForeignKey(to=Player, related_name='tasks', on_delete=djmodels.CASCADE)
    body = models.LongStringField()
    html_body = models.LongStringField()
    correct_answer = models.StringField()
    answer = models.StringField(null=True)
    created_at = djmodels.DateTimeField(auto_now_add=True)
    updated_at = djmodels.DateTimeField(auto_now=True)
    task_name = models.StringField()

    @classmethod
    def create(cls, player, fun, **params):
        """
          the following method creates a new task, and requires as an input a task-generating function and (if any) some
          parameters fed into task-generating function.
        """
        proto_task = fun(**params)
        task = cls(player=player,
                   body=proto_task.body,
                   html_body=proto_task.html_body,
                   correct_answer=proto_task.correct_answer,
                   task_name=proto_task.name)
        return task
