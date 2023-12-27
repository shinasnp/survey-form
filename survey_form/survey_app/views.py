from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Survey,
    QuestionOrder,
    ResponseChoice,
    Respondent,
    SurveyResponse,
    Question,
    QuestionType,
    Response as UserResponse,
    ConditionalOrder,
)

EMPTY_REQUEST_DATA_MSG = "Request data is empty"


class SurveyCreateView(APIView):
    """
    API to create Survey
    """

    def create_survey(self, data):
        """
        create survey from request data
        """
        validated_data = {
            "name": data["name"],
            "description": data["description"],
            "opening_time": data["opening_time"],
            "closing_time": data["closing_time"],
        }
        Survey.objects.create(**validated_data)

    def post(self, request):
        data = request.data
        if data:
            self.create_survey(data)
            return Response(
                {"msg": "Survey created successfully!"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "msg": EMPTY_REQUEST_DATA_MSG,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class QuestionCreateView(APIView):
    """
    API to create questions for survey
    """

    def create_question(self, data):
        """
        create question obj from request data
        """
        question_type = QuestionType.objects.get(type=data.get("question_type"))
        validated_data = {
            "name": data["name"],
            "text": data["text"],
            "question_type": question_type,
            "is_mandatory": data["is_mandatory"],
            "media_url": data.get("media_url"),
            "constraints": data.get("constraints"),
        }
        question = Question.objects.create(**validated_data)
        return question

    @transaction.atomic
    def post(self, request):

        data = request.data
        if data:
            question = self.create_question(data)
            survey_id = data.get("survey_id")
            survey = Survey.objects.get(id=survey_id)
            QuestionOrder.objects.create(
                question=question, survey=survey, order=data["order"]
            )
            response_choices = data.get("response_choices")
            if response_choices:
                for choice in response_choices:
                    ResponseChoice.objects.create(question=question, text=choice)
            return Response(
                {"msg": "Question created successfully!"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"msg": EMPTY_REQUEST_DATA_MSG},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ShowFormView(APIView):
    """
    API to show form for survey
    """

    def get_survey_data(self, survey_form, data):
        """
        get survey data
        """
        data["name"] = survey_form.name
        data["description"] = survey_form.description
        data["opening_time"] = survey_form.opening_time
        data["closing_time"] = survey_form.closing_time
        data["is_open"] = survey_form.is_open

    def get_question_details(self, question_order_obj):
        """
        get question details for survey
        """
        question_data = dict()
        question_data["order"] = question_order_obj.order
        question_data["id"] = question_order_obj.question.id
        question_data["name"] = question_order_obj.question.name
        question_data["text"] = question_order_obj.question.text
        question_data["question_type"] = question_order_obj.question.question_type.type
        question_data["is_mandatory"] = question_order_obj.question.is_mandatory
        question_data["media_url"] = question_order_obj.question.media_url
        question_data["constraints"] = question_order_obj.question.constraints
        response_choices = ResponseChoice.objects.filter(
            question=question_order_obj.question
        ).values_list("text", flat=True)
        question_data["response_choices"] = response_choices
        conditional_order = ConditionalOrder.objects.filter(
            question_order=question_order_obj
        ).first()
        if conditional_order:
            conditional_order = {
                "question_order": conditional_order.question_order.order
                if conditional_order.question_order
                else None,
                "response_question_order": conditional_order.response_question_order.order
                if conditional_order.response_question_order
                else None,
                "positive_response_question_order": conditional_order.positive_response_question_order.order
                if conditional_order.positive_response_question_order
                else None,
                "negative_response_question_order": conditional_order.negative_response_question_order.order
                if conditional_order.negative_response_question_order
                else None,
            }
            question_data["conditional_order"] = conditional_order
        return question_data

    def get(self, request, pk):

        data = {}
        survey_form = Survey.objects.get(id=pk)
        self.get_survey_data(survey_form, data)
        question_orders = QuestionOrder.objects.filter(
            survey=survey_form
        ).select_related("question", "question__question_type")
        questions_details = []
        for question_order in question_orders:
            question_data = self.get_question_details(question_order)
            questions_details.append(question_data)
        data["questions_details"] = questions_details

        return Response(
            {"data": data},
            status=status.HTTP_200_OK,
        )


class SaveResponseView(APIView):
    """
    API to save survey response
    """

    @transaction.atomic
    def post(self, request):
        data = request.data
        if data:
            survey = Survey.objects.get(id=data["survey_id"])
            respondent = Respondent.objects.get(id=data["respondent_id"])
            started_at = data.get("started_at")
            completed_at = data.get("completed_at")
            user_responses = data["responses"]
            survey_response, created = SurveyResponse.objects.update_or_create(
                survey=survey,
                respondent=respondent,
            )
            if started_at and not survey_response.started_at:
                survey_response.started_at = started_at
            if completed_at and not survey_response.completed_at:
                survey_response.completed_at = completed_at
            survey_response.save()
            for response in user_responses:
                question = Question.objects.get(id=response["question_id"])
                answer = response["answer"]
                UserResponse.objects.create(
                    survey_response=survey_response,
                    question=question,
                    answer=answer,
                )
                return Response(
                    {"msg": "Response successfully submitted"},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"msg": EMPTY_REQUEST_DATA_MSG},
                status=status.HTTP_400_BAD_REQUEST,
            )
