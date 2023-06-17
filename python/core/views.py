import json

from django.contrib.auth import login
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework import generics, status

from core.models import ConversationMessage, ChatConversation, Adventure
from core.serializers import ConversationMessageSerializer, ChatConversationSerializer
from rest_framework.authtoken.admin import User

from api.client import OpenAPIClient


def login_user(request, *args, **kwargs):
    data = json.loads(request.body.decode())
    user = User.objects.get(id=int(data["id"]))
    login(request, user)
    return HttpResponse(200)


def submit_response(request, *args, **kwargs):
    data = json.loads(request.body.decode())
    client = OpenAPIClient()
    conversation = ChatConversation.objects.get(id=data["conversation_id"])
    response = client.submit(conversation.get_messages_json())
    user = User.objects.get(username="system")
    ConversationMessage.objects.create(user=user, content=response["content"], conversation=conversation)
    content = json.dumps({"message": response["content"]}).encode()
    return HttpResponse(status=200, content_type="application_json", content=content)


def quiz_completed(request, *args, **kwargs):
    data = json.loads(request.body.decode())
    points_earned = data['points_earned']
    adventure = Adventure.objects.get(id=data['adventure_id'])
    adventure.points_earned += points_earned
    adventure.save()
    content = json.dumps({"message": 'Congratulations! Your have a total of %d points!' % adventure.points_earned})
    return HttpResponse(status=200, content_type="application_json", content=content)


class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context["users"] = User.objects.all().values("id", "first_name")

        return context


class QuizView(TemplateView):
    template_name = "quiz.html"

    def get_context_data(self, **kwargs):
        questions = [
          {
            "question": "Who led the Legion of the Iron Wolves in the battle for independence?",
            "optionA": "General Adrian Vasilescu",
            "optionB": "Colonel Victor Popescu",
            "optionC": "Captain Radu Constantinescu",
            "optionD": "Major Alexandru Ionescu",
            "correctOption": "optionA"
          },
          {
            "question": "In which year did the famous battle for independence take place in Romania?",
            "optionA": "1910",
            "optionB": "1923",
            "optionC": "1935",
            "optionD": "1948",
            "correctOption": "optionB"
          },
          {
            "question": "What became a symbol of resistance in Romania after the victory in the battle?",
            "optionA": "The Legion of the Iron Wolves",
            "optionB": "The Legion of the Golden Eagles",
            "optionC": "The Battalion of the Silver Falcons",
            "optionD": "The Regiment of the Bronze Lions",
            "correctOption": "optionA"
          }
        ]
        context = super(QuizView, self).get_context_data(**kwargs)
        context['questions_dict'] = questions
        context['adventure_id'] = 1
        return context

# API Views


class ConversationMessageListCreateView(generics.ListCreateAPIView):
    queryset = ConversationMessage.objects.all()
    serializer_class = ConversationMessageSerializer
    authentication_classes = []


class ConversationMessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ConversationMessage.objects.all()
    serializer_class = ConversationMessageSerializer
    authentication_classes = []


class ChatConversationListCreateView(generics.ListCreateAPIView):
    queryset = ChatConversation.objects.all()
    serializer_class = ChatConversationSerializer
    authentication_classes = []


class ChatConversationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatConversation.objects.all()
    serializer_class = ChatConversationSerializer
    authentication_classes = []

