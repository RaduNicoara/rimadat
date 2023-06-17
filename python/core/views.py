import json

from django.contrib.auth import login
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from rest_framework import generics

from core.models import ConversationMessage, ChatConversation
from core.serializers import ConversationMessageSerializer, ChatConversationSerializer
from rest_framework.authtoken.admin import User


def login_user(request, *args, **kwargs):
    data = json.loads(request.body.decode())
    user = User.objects.get(id=int(data["id"]))
    login(request, user)
    return HttpResponse(200)


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

