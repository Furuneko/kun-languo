from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from ..views import NoMoreCqs, QuizQuestionView

views_to_add = [
    NoMoreCqs,
    QuizQuestionView
]
urlpatterns = [path(i.url_pattern, i.as_view(), name=i.url_name) for i in views_to_add]
