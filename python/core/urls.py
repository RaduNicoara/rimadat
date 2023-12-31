from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from core.views import (
    ConversationMessageListCreateView,
    ConversationMessageRetrieveUpdateDestroyView,
    ChatConversationListCreateView,
    ChatConversationRetrieveUpdateDestroyView,
    MainView,
    login_user,
    submit_response,
    AdventureRetrieveUpdateDestroyView,
    AdventureListCreateView,
    PointOfInterestRetrieveUpdateDestroyView,
    PointOfInterestListCreateView,
    quiz_completed,
    start_quiz,
    get_story
)

urlpatterns = [
    path('', MainView.as_view(), name="main"),
    path('login/', login_user, name="login"),
    path('submit/', submit_response, name="submit"),
    path('messages/', ConversationMessageListCreateView.as_view(), name='message-list'),
    path('messages/<int:pk>/', ConversationMessageRetrieveUpdateDestroyView.as_view(), name='message-detail'),
    path('conversations/', ChatConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ChatConversationRetrieveUpdateDestroyView.as_view(), name='conversation-detail'),
    path('adventures/', AdventureListCreateView.as_view(), name='adventure-list'),
    path('adventures/<int:pk>/', AdventureRetrieveUpdateDestroyView.as_view(), name='adventure-detail'),
    path('poi/', PointOfInterestListCreateView.as_view(), name='poi-list'),
    path('poi/<int:pk>/', PointOfInterestRetrieveUpdateDestroyView.as_view(), name='poi-detail'),
    path('quiz/', start_quiz, name="quiz"),
    path('quiz-completed/', quiz_completed, name="quiz-completed"),
    path('story/', get_story, name="story")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
