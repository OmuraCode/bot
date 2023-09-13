# import tensorflow as tf
# import numpy as np
# import random
# from bot.bot_model import tokenizer, index_to_intent, response_for_intent, new_model
# from .serializers import ChatbotInputSerializer, ChatbotResponseSerializer
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from keras.models import load_model
#
# # from chat.apps import loaded_model
#
#
# loaded_model = load_model('/usr/src/app/model/bot_model.keras')
#
#
#
# class ChatbotView(APIView):
#     def post(self, request):
#         serializer = ChatbotInputSerializer(data=request.data)
#         if serializer.is_valid():
#             user_input = serializer.validated_data['user_input']
#
#             # Check if language choice is needed
#             if 'language_choice' not in request.session:
#                 language_choice = self.get_language_choice(user_input)
#                 if language_choice:
#                     request.session['language_choice'] = language_choice
#                     if language_choice == 'KG':
#                         response = 'Саламатсызбы, кандай суроонузга жооп бере алам?'
#                     else:
#                         response = 'Здравствуйте, чем могу быть полезен?'
#                 else:
#                     response = 'Пожалуйста, выберите язык: 1 - кыргызский, 2 - русский.'
#             else:
#                 language_choice = request.session['language_choice']
#                 response = self.get_response(user_input, language_choice)
#
#             response_data = {'response': response}
#             response_serializer = ChatbotResponseSerializer(response_data)
#
#             return Response(response_serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def get_language_choice(self, input_text):
#         if input_text == "1":
#             return "KG"
#         elif input_text == "2":
#             return "RU"
#         else:
#             return None
#
#     def get_response(self, input_text, language_choice):
#         sent_tokens = []
#         words = input_text.split()
#         for word in words:
#             if word in tokenizer.word_index:
#                 sent_tokens.append(tokenizer.word_index[word])
#             else:
#                 sent_tokens.append(tokenizer.word_index['<unk>'])
#         sent_tokens = tf.expand_dims(sent_tokens, 0)
#         pred = loaded_model.predict(sent_tokens)
#         pred_class = np.argmax(pred, axis=1)
#         max_pred_prob = np.max(pred)
#
#         # Define a threshold probability for fallback intent
#         fallback_threshold = 0.1
#         print(max_pred_prob, '!!!!!')
#         print(fallback_threshold, '+++++++++')
#
#         if max_pred_prob < fallback_threshold:
#             selected_intent = "FallbackResponse"
#         else:
#             selected_intent = index_to_intent[pred_class[0]]
#             print('selected_intent', selected_intent)
#
#         if selected_intent in response_for_intent:
#             if language_choice == 'KG':
#                 response_options = response_for_intent[selected_intent]['KG']
#             else:
#                 response_options = response_for_intent[selected_intent]['RU']
#             if language_choice in response_options:
#                 selected_response = random.choice(response_options[language_choice])
#             else:
#                 selected_response = random.choice(response_options)
#
#             return selected_response
#
#         return "I'm sorry, I don't have a response for that."
