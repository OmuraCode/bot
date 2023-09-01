from rest_framework import serializers
from .models import Intent, IntentText, Entity

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'

class IntentTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntentText
        fields = '__all__'

class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = '__all__'

    def clean_intent(self, value):
        if Intent.objects.filter(intent=value).exists():
            raise serializers.ValidationError("Интент с таким названием уже существует!")
        return value
