from django.contrib import admin
from .models import Adventure, PointOfInterest, ChatConversation, ConversationMessage

admin.site.register(Adventure)
admin.site.register(PointOfInterest)
admin.site.register(ChatConversation)
admin.site.register(ConversationMessage)
