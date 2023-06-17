import json

from django.contrib.auth import login
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework import generics, status

from core.models import ConversationMessage, ChatConversation
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


class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context["users"] = User.objects.all().values("id", "first_name")

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

