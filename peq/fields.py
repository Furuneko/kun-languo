# form_fields.py
from otree.models import IntegerField as oTreeIntegerField
from .widgets import LikertWidget
from django.forms import IntegerField


class FormLikertField(IntegerField):
    widget = LikertWidget

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices')
        self.headers = kwargs.pop('headers')
        kwargs['widget'] = self.widget(headers=self.headers, choices=self.choices)
        super().__init__(*args, **kwargs)




class LikertField(oTreeIntegerField):

    def __init__(self,  *args,    **kwargs ):
        self.headers = kwargs.pop('headers',{})


        super().__init__(         *args,        **kwargs,)

    def formfield(self, **kwargs):
        return FormLikertField(label=self.verbose_name, choices=self.choices, headers=self.headers)
