from django.contrib import admin

# Register your models here.
from .models import (
    QuestionType,
    QuestionConstraints,
    Survey,
    SurveyResponse,
    Question,
    QuestionOrder,
    ResponseChoice,
    Respondent,
    Response,
    ConditionalOrder,
)

admin.site.register(QuestionType)
admin.site.register(QuestionConstraints)
admin.site.register(Survey)
admin.site.register(SurveyResponse)
admin.site.register(Question)
admin.site.register(QuestionOrder)
admin.site.register(ResponseChoice)
admin.site.register(Respondent)
admin.site.register(Response)
admin.site.register(ConditionalOrder)
