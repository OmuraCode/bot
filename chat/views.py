import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import random
from .serializers import ChatbotInputSerializer, ChatbotResponseSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from intents.models import Intent, IntentText
from keras.models import load_model


def clean(line):
    cleaned_line = ''
    for char in line:
        if char.isalpha():
            cleaned_line += char
        else:
            cleaned_line += ' '
    cleaned_line = ' '.join(cleaned_line.split())
    return cleaned_line


data = Intent.objects.all()
intents = []
unique_intents = []
text_input = []
response_for_intent = {}

for intent in data:
    # List of unique intents
    if intent.intent not in unique_intents:
        unique_intents.append(intent.intent)

    # Iterate through text associated with the intent
    for text_obj in IntentText.objects.filter(intent=intent):
        text_input.extend(text_obj.texts)
        intents.extend([intent.intent] * len(text_obj.texts))

        # Create a dictionary to hold responses for the intent
        if intent.intent not in response_for_intent:
            response_for_intent[intent.intent] = {}

        # Add responses for different languages
        response_for_intent[intent.intent][text_obj.language] = text_obj.responses

tokenizer = Tokenizer(filters='', oov_token='<unk>')
tokenizer.fit_on_texts(text_input)
sequences = tokenizer.texts_to_sequences(text_input)
padded_sequences = pad_sequences(sequences, padding='pre')


intent_to_index = {}
categorical_target = []
index = 0
for intent in intents:
    if intent not in intent_to_index:
        intent_to_index[intent] = index
        index += 1
    categorical_target.append(intent_to_index[intent])
num_classes = len(intent_to_index)

# Convert intent_to_index to index_to_intent
index_to_intent = {index: intent for intent, index in intent_to_index.items()}


categorical_vec = tf.keras.utils.to_categorical(categorical_target,
                                                num_classes=num_classes, dtype='int32')

epochs = 100
embed_dim = 300
lstm_num = 50
output_dim = categorical_vec.shape[1]
input_dim = len(unique_intents)

model = tf.keras.models.Sequential([
    tf.keras.layers.Embedding(len(tokenizer.word_index) + 1, embed_dim),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(lstm_num, dropout=0.1)),
    tf.keras.layers.Dense(lstm_num, activation='relu'),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(output_dim, activation='softmax')
])

optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
# model.summary()

model.fit(padded_sequences, categorical_vec, epochs=epochs, verbose=0)

# Сохраните модель в файл
# model.save('lstmModel')
# Загрузка модели
# loaded_model = load_model('lstmModel')
# Дообучение модели
# loaded_model.fit(padded_sequences, categorical_vec, epochs=epochs, verbose=0, initial_epoch=epochs)

class ChatbotView(APIView):
    def post(self, request):
        serializer = ChatbotInputSerializer(data=request.data)
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

            response_data = {'response': response}
            response_serializer = ChatbotResponseSerializer(response_data)

            return Response(response_serializer.data, status=status.HTTP_200_OK)
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
        pred = model.predict(sent_tokens)
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

