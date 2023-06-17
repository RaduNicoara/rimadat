from django.db import models
from django.utils import timezone


class ConversationMessage(models.Model):
    class Meta:
        app_label = "core"

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    conversation = models.ForeignKey("core.ChatConversation", on_delete=models.CASCADE, related_name="messages")


class ChatConversation(models.Model):
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    name = models.CharField(max_length=256)

    def get_messages_json(self):
        return [
            {
                "role": "user" if m.user.username != "system" else "system",
                "content": m.content
            } for m in self.messages.order_by("created_at")
        ]


class Entity(models.Model):
    name = models.CharField(max_length=256)
    interactions = models.JSONField()