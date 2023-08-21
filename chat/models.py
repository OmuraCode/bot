





























# import json
# from chat.models import Intent, Entity


# def load_data_to_database(json_file_path):
#     with open('data_json/intent.json', 'r') as f:
#         data = json.load(f)
#
#     for intent_data in data['intents']:
#         intent = Intent.objects.create(
#             intent=intent_data['intent'],
#             text=intent_data['text'][0],  # Мы берем только первое значение из списка text
#             responses=json.dumps(intent_data['responses']),  # Сохраняем список responses как JSON-строку
#             function=intent_data['extension']['function'],
#             entities=intent_data['extension']['entities'],
#             context_in=intent_data['context']['in'],
#             context_out=intent_data['context']['out'],
#             context_clear=intent_data['context']['clear'],
#             entity_type=intent_data['entityType']
#         )
#
#         for entity_data in intent_data['entities']:
#             Entity.objects.create(
#                 intent1=intent,
#                 entity1=entity_data['entity'],
#                 value=entity_data['value']
#             )
#
#
# # Замените 'path_to_your_json.json' на актуальный путь к вашему JSON файлу
# load_data_to_database('data_json/intent.json')
