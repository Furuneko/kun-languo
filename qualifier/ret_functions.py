# this is the module responsible for generation functions for different rets
# if you need new rets you need to define generating functions here and attach them to corresponding tasks

import random
from random import randint
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from string import digits, ascii_lowercase
import logging

logger = logging.getLogger(__name__)


# function slices a list with n elements in each sublist (if possible)
def slicelist(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


# slices a list into n parts  of an equal size (if possible)
def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]


def get_random_list(max_len):
    low_upper_bound = 50
    high_upper_bound = 99
    return [randint(10, randint(low_upper_bound, high_upper_bound)) for i in range(max_len)]


# Shared properties for the tasks collected under the TaskGenerator Class
class TaskGenerator:
    path_to_render = None

    def __init__(self, **kwargs):
        self.body = self.get_body(**kwargs)

        self.correct_answer = self.get_correct_answer()
        self.html_body = self.get_html_body()
        # logger.info(f'Correct answer: {self.correct_answer}')

    def get_context_for_body(self):
        return {}

    def get_html_body(self):
        return mark_safe(render_to_string(self.path_to_render, self.get_context_for_body()))

    def get_body(self, **kwargs):
        pass

    def get_correct_answer(self):
        pass


class Decoding(TaskGenerator):
    path_to_render = 'qualifier/includes/decoding.html'
    name = 'Deconding tasks (numbers to letters)'

    def get_correct_answer(self):
        correct_answer = ''.join([self.task_dict[i] for i in self.question])
        return correct_answer

    def get_body(self, **kwargs):
        seed =  kwargs.get('seed')
        dict_length = kwargs.get('dict_length', 5)
        task_len = kwargs.get('task_len', 5)
        random.seed(seed)
        digs = random.sample(list(digits), k=dict_length)
        random.shuffle(digs)
        lts = random.sample(ascii_lowercase, k=dict_length)
        self.task_dict = dict(zip(digs, lts))
        self.question = random.sample(digs, k=task_len)
        random.seed()
        return {
            'question': self.question,
            'task_dict': self.task_dict,
        }

    def get_context_for_body(self):
        return {
            'question': self.question,
            'task_dict': self.task_dict,
        }
