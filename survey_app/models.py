from django.db import models
from django.contrib.auth.models import User


class Respondent(User):
    pass


class CommonTimestamp(models.Model):  # COMM0N
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Survey(CommonTimestamp):
    name = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    opening_time = models.DateTimeField(null=True, blank=True)
    closing_time = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=False)


class QuestionType(CommonTimestamp):
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"

    ITEM_TYPES = (
        (INTEGER, "INTEGER"),
        (TEXT, "TEXT"),
        (MULTIPLE_CHOICE, "MULTIPLE_CHOICE"),
    )
    type = models.CharField(max_length=251, choices=ITEM_TYPES)


class Question(CommonTimestamp):
    name = models.CharField(max_length=240)
    text = models.TextField()
    question_type = models.ForeignKey(
        QuestionType,
        on_delete=models.CASCADE,
    )
    is_mandatory = models.BooleanField(default=True)
    media_url = models.URLField(max_length=200, null=True, blank=True)
    constraints = models.JSONField(null=True, blank=True)


class QuestionOrder(CommonTimestamp):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(default=0)


class ResponseChoice(CommonTimestamp):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )
    text = models.TextField()


class QuestionConstraints(CommonTimestamp):
    name = models.CharField(max_length=240)
    question_type = models.ForeignKey(
        QuestionType,
        on_delete=models.CASCADE,
    )


class SurveyResponse(CommonTimestamp):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
    )
    respondent = models.ForeignKey(
        Respondent,
        on_delete=models.CASCADE,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class Response(CommonTimestamp):
    survey_response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )
    answer = models.TextField(null=True, blank=True)


class ConditionalOrder(CommonTimestamp):
    question_order = models.ForeignKey(
        QuestionOrder,
        related_name="question_order",
        on_delete=models.CASCADE,
    )
    response_question_order = models.ForeignKey(
        QuestionOrder,
        related_name="response_question_order",
        on_delete=models.CASCADE,
    )
    positive_response_question_order = models.ForeignKey(
        QuestionOrder,
        related_name="positive_response_question_order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    negative_response_question_order = models.ForeignKey(
        QuestionOrder,
        related_name="negative_response_question_order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
