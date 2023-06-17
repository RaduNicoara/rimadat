from django.urls import path
from core.views import (
    ConversationMessageListCreateView,
    ConversationMessageRetrieveUpdateDestroyView,
    ChatConversationListCreateView,
    ChatConversationRetrieveUpdateDestroyView,
    MainView,
    login_user,
    submit_response
)

urlpatterns = [
    path('', MainView.as_view(), name="main"),
    path('login/', login_user, name="login"),
    path('submit/', submit_response, name="submit"),
    path('messages/', ConversationMessageListCreateView.as_view(), name='message-list'),
    path('messages/<int:pk>/', ConversationMessageRetrieveUpdateDestroyView.as_view(), name='message-detail'),
    path('conversations/', ChatConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ChatConversationRetrieveUpdateDestroyView.as_view(), name='conversation-detail'),
]