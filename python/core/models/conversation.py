from django.db import models


class ConversationMessage(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    content = models.TextField()
    conversation = models.ForeignKey("core.ChatConversation", on_delete=models.CASCADE)


class ChatConversation(models.Model):
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
