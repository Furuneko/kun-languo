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
from otree.lookup import get_page_lookup

practice_pages = ['Practice']


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
                    'num_tasks_correct': self.num_tasks_correct(),
                    'num_tasks_total': self.num_tasks_total(),
                    'correct_answer': new_task.correct_answer
                    }

            return {self.id_in_group: resp}

    def get_current_page_name(self):
        lookup = get_page_lookup(self.participant._session_code, self.participant._index_in_pages)
        return lookup.page_class.__name__

    def get_tasks_by_page(self, page_name=None):
        page_name = page_name or self.get_current_page_name()
        return self.tasks.filter(page_name=page_name)


    def num_tasks_correct(self, page_name=None):
        """returns total number of tasks to which a player provided a correct answer"""
        page_name = page_name or self.get_current_page_name()
        return self.get_tasks_by_page(page_name=page_name).filter(correct_answer=F('answer')).count()


    def num_tasks_total(self, page_name=None):
        """returns total number of tasks to which a player provided an answer"""
        page_name = page_name or self.get_current_page_name()
        return self.get_tasks_by_page(page_name=page_name).filter(answer__isnull=False, ).count()

    def get_or_create_task(self):
        """
            checks if there are any unfinished (with no answer) tasks. If yes, we return the unfinished
            task. If there are no uncompleted tasks we create a new one using a task-generating function from session settings
        """

        page_name = self.get_current_page_name()
        app_name = self._meta.app_label
        try:
            last_one = self.tasks.filter(page_name=page_name).latest()

            nlast = last_one.in_player_counter
        except ObjectDoesNotExist:
            nlast = 0

        try:
            task = self.tasks.get(answer__isnull=True, page_name=page_name)
        except ObjectDoesNotExist:

            params = self.session.vars['task_params']
            params['seed'] = app_name + page_name + str(nlast)
            fun = self.session.vars['task_fun']
            proto_task = fun(**params)

            task = self.tasks.create(player=self,
                                     body=proto_task.body,
                                     html_body=proto_task.html_body,
                                     correct_answer=proto_task.correct_answer,
                                     task_name=proto_task.name,
                                     in_player_counter=nlast + 1,
                                     app_name=app_name,
                                     page_name=page_name)

        return task

    def set_payoff(self):
        pass


class GeneralTask(djmodels.Model):
    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'in_player_counter'
        abstract = True

    body = models.LongStringField()
    html_body = models.LongStringField()
    correct_answer = models.StringField()
    answer = models.StringField(null=True)
    page_name = models.StringField()
    app_name = models.StringField()
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
