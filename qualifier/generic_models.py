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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F


class RETPlayer(BasePlayer):
    class Meta:
        abstract = True

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
                    'correct_answer':new_task.correct_answer
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
        try:
            last_one = self.tasks.latest()
            nlast = last_one.in_player_counter
        except ObjectDoesNotExist:
            nlast = 0

        try:
            task = self.tasks.get(answer__isnull=True)
        except ObjectDoesNotExist:
            params = self.session.vars['task_params']
            params['seed'] = self._meta.app_label + str(nlast)
            fun = self.session.vars['task_fun']
            proto_task = fun(**params)
            task = self.tasks.create(player=self,
                                     body=proto_task.body,
                                     html_body=proto_task.html_body,
                                     correct_answer=proto_task.correct_answer,
                                     task_name=proto_task.name,
                                     in_player_counter=nlast + 1)

        return task

    def set_payoff(self):
        pass


class GeneralTask(djmodels.Model):
    # todo: add page to task to distinguish between practice and real tasks
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'in_player_counter'
        abstract = True

    body = models.LongStringField()
    html_body = models.LongStringField()
    correct_answer = models.StringField()
    answer = models.StringField(null=True)
    created_at = djmodels.DateTimeField(auto_now_add=True)
    updated_at = djmodels.DateTimeField(auto_now=True)
    task_name = models.StringField()
    in_player_counter = models.IntegerField(default=0)

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
