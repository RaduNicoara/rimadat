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


class Adventure(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    starting_point_longitude = models.DecimalField(max_digits=12, decimal_places=6)
    starting_point_latitude = models.DecimalField(max_digits=12, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=12, decimal_places=6)
    destination_latitude = models.DecimalField(max_digits=12, decimal_places=6)
    points_earned = models.PositiveSmallIntegerField(default=0)


class PointOfInterest(models.Model):
    name = models.CharField(max_length=64)
    longitude = models.DecimalField(max_digits=12, decimal_places=6)
    latitude = models.DecimalField(max_digits=12, decimal_places=6)
    order = models.SmallIntegerField(default=0)
    visited = models.BooleanField(default=False)
    story = models.TextField()
    adventure = models.ForeignKey('core.Adventure', related_name='points_of_interest', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
