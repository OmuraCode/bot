# import json
# from .models import Intent
#
# with open('C:\Users\user\Desktop\manychat\data_json\content.json', 'r') as file:
#     data = json.load(file)
#
# for intent_data in data['intents']:
#     intent = Intent(
#         tag=intent_data['tag'],
#         input=intent_data['input'],
#         responses=intent_data['responses']
#     )
#     intent.save()

import json
from chat.models import Intent, Entity


def load_data_to_database(json_file_path):
    with open('data_json/2content.json', 'r') as f:
        data = json.load(f)

    for intent_data in data['intents']:
        intent = Intent.objects.create(
            intent=intent_data['intent'],
            text=intent_data['text'],
            responses=intent_data['responses'],
            function=intent_data['extension']['function'],
            entities=intent_data['extension']['entities'],
            context_in=intent_data['context']['in'],
            context_out=intent_data['context']['out'],
            context_clear=intent_data['context']['clear'],
            entity_type=intent_data['entityType']
        )

        for entity_data in intent_data['entities']:
            Entity.objects.create(
                intent=intent,
                entity=entity_data['entity'],
                value=entity_data['value']
            )


# Замените 'path_to_your_json.json' на актуальный путь к вашему JSON файлу
load_data_to_database('data_json/2content.json')
