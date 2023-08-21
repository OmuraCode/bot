from rest_framework import serializers

class ChatbotInputSerializer(serializers.Serializer):
    user_input = serializers.CharField()

class ChatbotResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
