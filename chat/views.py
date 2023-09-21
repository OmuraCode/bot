import tensorflow as tf
import numpy as np
import random
from django.http import HttpResponse
from django.shortcuts import render, redirect
from bot.bot_model import tokenizer, index_to_intent, response_for_intent, train_bot_model
from .serializers import ChatbotInputSerializer, ChatbotResponseSerializer
from rest_framework import status, viewsets, response
from rest_framework.response import Response
from rest_framework.views import APIView
from keras.models import load_model
from rest_framework.decorators import action
import os

# loaded_model = load_model('/usr/src/app/model/2.keras')

import random
import numpy as np

# Установите значение seed для модуля random
seed = 42  # Вы можете выбрать любое целочисленное значение в качестве seed
random.seed(seed)


def get_available_models():
    model_dir = '/usr/src/app/model/'
    model_paths = [os.path.join(model_dir, model_name) for model_name in os.listdir(model_dir) if model_name.endswith('.keras')]
    return [(model_name, model_path) for model_name, model_path in zip(os.listdir(model_dir), model_paths)]


def train_model(request):
    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        train_bot_model(model_name=model_name)
        return HttpResponse(f"Обучение модели '{model_name}' завершено.")
    else:
        return render(request, 'chat.html')  # Отобразите HTML-шаблон с формой для ввода названия модели

def select_model(request):
    if request.method == 'POST':
        selected_model = request.POST.get('selected_model')
        print('selected_model: ', selected_model)
        request.session['selected_model'] = selected_model
    return redirect('chatbot')

class ChatbotView(APIView):
    def __init__(self, *args, **kwargs):
        self.loaded_model = None  # Initialize loaded_model as None
        super().__init__(*args, **kwargs)
    def get(self, request, *args, **kwargs):
        available_models = get_available_models()
        return render(request, 'chat.html', {'available_models': available_models})


    def post(self, request):
        serializer = ChatbotInputSerializer(data=request.data)
        selected_model_path = request.session.get('selected_model')
        if selected_model_path:
            self.loaded_model = load_model(selected_model_path)
        else:
            self.loaded_model = load_model('/usr/src/app/model/1.keras')

        if serializer.is_valid():
            user_input = serializer.validated_data['user_input']
            user_input = user_input.lower()

            chat_history = request.session.get('chat_history', [])
            user_message = f"Пользователь: {user_input}"
            chat_history.append(user_message)

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

            bot_message = f"Бот: {response}"
            chat_history.append(bot_message)

            request.session['chat_history'] = chat_history

            return render(request, 'chat.html', {'response': response, 'chat_history': chat_history})
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
        print(max_pred_prob, '!!!!!')
        print(fallback_threshold, '+++++++++')

        if max_pred_prob < fallback_threshold:
            selected_intent = "FallbackResponse"
        else:
            selected_intent = index_to_intent[pred_class[0]]
            print('selected_intent', selected_intent)

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
