from django.views.generic import DetailView, UpdateView, TemplateView
from django.template.loader import render_to_string
from .models import CQ, Constants
from django.http import JsonResponse
import logging
from django import forms
import json
from django.core.exceptions import ValidationError
from django.utils.html import mark_safe


class QForm(forms.ModelForm):
    answer = forms.IntegerField(widget=forms.RadioSelect(choices=((0, 0), (1, 1))))

    class Meta:
        model = CQ
        fields = ['answer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [(i, j) for i, j in enumerate(json.loads(self.instance.choices))]
        self.fields['answer'].widget.choices = choices

    def correct_choice_label(self):
        instance = self.instance
        return self.fields['answer'].widget.choices[instance.correct][1]

    def clean_answer(self):
        instance = self.instance
        data = self.cleaned_data['answer']
        if data != instance.correct:
            self.instance.counter += 1
            self.instance.save()
            raise ValidationError(self.instance.owner.session.config.get("err_msg", Constants.CQ_ERR_DEFAULT_MSG))
        elif not instance.explained:
            instance.explained = True
            instance.save()
            explanation = instance.hint if instance.hint else self.correct_choice_label()
            raise ValidationError(mark_safe(
                f'<div style="color: green;">'
                f'<div>{self.instance.owner.session.config.get("corr_msg", Constants.CQ_CORR_DEFAULT_MSG)}</div>'
                f'<div>{explanation}</div>'
                f'</div>')
            )
        return data


logger = logging.getLogger(__name__)


class GeneralJsonCQMixin:
    extra_params = {}

    def render_to_response(self, context, **response_kwargs):
        html_form = render_to_string(self.template_name,
                                     context,
                                     request=self.request,
                                     )

        return JsonResponse(dict(form_data=html_form, **self.extra_params))


class NoMoreCqs(GeneralJsonCQMixin, TemplateView):
    url_name = 'no_more_cqs'
    url_pattern = 'quiz/<participant_code>/no_more'
    template_name = 'main/includes/no_more.html'
    extra_params = dict(no_more_cq=True)


class QuizQuestionView(GeneralJsonCQMixin, UpdateView):
    """
    Single quiz question
    """
    url_pattern = 'quiz/<int:pk>'
    url_name = 'single_quiz_question'
    template_name = 'main/includes/single_cq.html'

    model = CQ
    form_class = QForm

    def get_success_url(self):
        return self.get_object().owner.get_quiz_url()

    def form_valid(self, form):
        form.save()
        return JsonResponse(dict(form_is_valid=True,
                                 next_q=self.get_success_url(),
                                 ),
                            )

    def form_invalid(self, form):

        context = self.get_context_data(form=form)
        context['form_is_valid'] = False

        return self.render_to_response(context)
