from django.urls import path

from .views import SurveyCreateView, QuestionCreateView, ShowFormView, SaveResponseView

urlpatterns = [
    path("create-survey/", SurveyCreateView.as_view()),
    path("create-question/", QuestionCreateView.as_view()),
    path("show-form/<int:pk>/", ShowFormView.as_view()),
    path("submit-response/", SaveResponseView.as_view()),
]
