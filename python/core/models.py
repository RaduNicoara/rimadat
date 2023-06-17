from django.db import models


class ConversationMessage(models.Model):
    class Meta:
        app_label = "core"

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    content = models.TextField()
    conversation = models.ForeignKey("core.ChatConversation", on_delete=models.CASCADE)


class ChatConversation(models.Model):
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)


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
