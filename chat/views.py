import tensorflow as tf
import numpy as np
import random
from django.http import HttpResponse
from django.shortcuts import render
from bot.bot_model import tokenizer, index_to_intent, response_for_intent, train_bot_model
from .serializers import ChatbotInputSerializer, ChatbotResponseSerializer
from rest_framework import status, viewsets, response
from rest_framework.response import Response
from rest_framework.views import APIView
from keras.models import load_model
from rest_framework.decorators import action

# loaded_model = load_model('/usr/src/app/model/test3.keras')

def load_chatbot_model(model_path):
    try:
        loaded_model = load_model(model_path)
        return loaded_model
    except Exception as e:
        # Обработка ошибки, если модель не может быть загружена
        print(f"Ошибка при загрузке модели: {e}")
        return None

def train_model(request):
    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        train_bot_model(model_name=model_name)
        return HttpResponse(f"Обучение модели '{model_name}' завершено.")
    else:
        return render(request, 'chat.html')  # Отобразите HTML-шаблон с формой для ввода названия модели


# class ChatbotView(APIView):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'chat.html')
#
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
#
#             # response_data = {'response': response}
#             # response_serializer = ChatbotResponseSerializer(response_data)
#
#             # return Response(response_serializer.data, status=status.HTTP_200_OK)
#
#             response = self.get_response(user_input, language_choice)
#             return render(request, 'chat.html', {'response': response})
#
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


class ChatbotViewSet(viewsets.ModelViewSet):
    serializer_class = ChatbotInputSerializer

    def __init__(self, loaded_model,  *args, **kwargs):
        self.loaded_model = loaded_model  # Инициализируйте атрибут loaded_model здесь

    @action(methods='POST', detail=False)
    def load_model(self, request, model_name):
        self.model_name = request.POST.get('model_name')
        self.loaded_model = load_model(f'/usr/src/app/model/{model_name}.keras')
        return response.Response({'msg': 'вы загрузили модель'})

    def get_queryset(self):
        return None

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data['user_input']

            # Check if language choice is needed
            if 'language_choice' not in request.session:
                language_choice = self.get_language_choice(user_input)
                if language_choice:
                    request.session['language_choice'] = language_choice
                    if language_choice == 'KG':
                        response = 'Саламатсызбы, кандай суроонузга жооп бере алам?'
                    else:
                        response = 'Здравствуйте, чем могу быть полезен?'
                else:
                    response = 'Пожалуйста, выберите язык: 1 - кыргызский, 2 - русский.'
            else:
                language_choice = request.session['language_choice']

            response = self.get_response(user_input, language_choice)
            return render(request, 'chat.html', {'response': response})

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_language_choice(self, input_text):
        if input_text == "1":
            return "KG"
        elif input_text == "2":
            return "RU"
        else:
            return None

    def get_response(self, input_text, language_choice):
        sent_tokens = []
        words = input_text.split()
        for word in words:
            if word in tokenizer.word_index:
                sent_tokens.append(tokenizer.word_index[word])
            else:
                sent_tokens.append(tokenizer.word_index['<unk>'])
        sent_tokens = tf.expand_dims(sent_tokens, 0)
        pred = self.loaded_model.predict(sent_tokens)
        pred_class = np.argmax(pred, axis=1)
        max_pred_prob = np.max(pred)

        # Define a threshold probability for fallback intent
        fallback_threshold = 0.1

        if max_pred_prob < fallback_threshold:
            selected_intent = "FallbackResponse"
        else:
            selected_intent = index_to_intent[pred_class[0]]

        if selected_intent in response_for_intent:
            if language_choice == 'KG':
                response_options = response_for_intent[selected_intent]['KG']
            else:
                response_options = response_for_intent[selected_intent]['RU']
            if language_choice in response_options:
                selected_response = random.choice(response_options[language_choice])
            else:
                selected_response = random.choice(response_options)

            return selected_response

        return "I'm sorry, I don't have a response for that."


