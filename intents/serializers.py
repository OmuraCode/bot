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

    # def to_representation(self, instance):
    #     repr = super().to_representation(instance)

