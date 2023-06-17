from rest_framework import serializers
from core.models import ConversationMessage, ChatConversation, Adventure, PointOfInterest


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = '__all__'


class ChatConversationSerializer(serializers.ModelSerializer):
    messages = ConversationMessageSerializer(many=True, required=False)

    class Meta:
        model = ChatConversation
        fields = '__all__'


class AdventureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adventure
        fields = '__all__'


class PointOfInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointOfInterest
        fields = '__all__'
