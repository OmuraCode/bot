import json
from django.db import models

class Intent(models.Model):
    intent = models.CharField(max_length=255)
    function = models.CharField(max_length=255, blank=True)
    entities = models.BooleanField(default=False)
    context_in = models.CharField(max_length=255, blank=True)
    context_out = models.CharField(max_length=255, blank=True)
    context_clear = models.BooleanField(default=False)
    entity_type = models.CharField(max_length=255, blank=True)

class IntentText(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE)
    language = models.CharField(max_length=10)  # For example: "RU", "KG"
    texts = models.JSONField()
    responses = models.JSONField()

class Entity(models.Model):
    intent1 = models.ForeignKey(Intent, on_delete=models.CASCADE)
    entity1 = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)



def load_data_to_database(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for intent_data in data['intents']:
        intent = Intent.objects.create(
            intent=intent_data['intent'],
            function=intent_data['extension'].get('function', ''),
            entities=intent_data['extension'].get('entities', False),
            context_in=intent_data['context'].get('in', ''),
            context_out=intent_data['context'].get('out', ''),
            context_clear=intent_data['context'].get('clear', False),
            entity_type=intent_data.get('entityType', '')
        )

        # Save text and response for each language
        for language, text_list in intent_data['text'].items():
            responses = intent_data['responses'][language]

            IntentText.objects.create(
                intent=intent,
                language=language,
                texts=text_list,
                responses=responses
            )

        for entity_data in intent_data['entities']:
            Entity.objects.create(
                intent1=intent,
                entity1=entity_data['entity'],
                value=entity_data.get('value', '')
            )


# Замените 'path_to_your_json.json' на актуальный путь к вашему JSON файлу
# load_data_to_database('data_json/case.json')



