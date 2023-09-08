import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from intents.models import Intent, IntentText
import nltk
from nltk.corpus import stopwords
import random


nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))
custom_stop_words = ["анан", "кийин", "бирок", "болбосо", "ошого", "кантип", "ошондой", "эгер",
                     "ошо", "менен", "ошолор", "алар", "ошол", "тигил", "эме", "эменер", "эмне",
                     "эми", "ошондо", "башка", "сен", "мен", "ал", "силер", "сиздер", "биз",
                     "ар", "бир", "жана", "болсо", "болбосо", "бол", "кана", "мына", "тигине",
                     "жакта", "эмнеге", "башкалар", "биринчи", "жатат", "кылганга", "жок",
                     "жокмун", "тур", "озум", "озумдуку", "тиги", "тигиники", "биздики", "алардыкы",
                     "озунор", "озубуз", "сиз", "орто", "ананырык", "кечирек", "кеч", "бул", "жактан",
                     "жанымда", "кайра", "тен", "керек", "эрте", "силердики", "сеники", "меники", "менин",
                     "сенин", "анын", "тигинини", "анда", "кандай", "сага", "дагы", "эле", "неге",
                     "эметип", "тигинтип", "ошонтип", "ошон", "учун", "кыл", "кылсам", "кылбасам",
                     "деле", "андай", "мындай", "тигиндей", "ким"]

stop_words.update(custom_stop_words)

# print(stop_words)

def remove_stopwords(text):
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)


def clean(line):
    cleaned_line = ''
    for char in line:
        if char.isalnum() or char.isspace():
            cleaned_line += char
        else:
            cleaned_line += ' '
    cleaned_line = ' '.join(cleaned_line.split())
    return cleaned_line


# data = Intent.objects.all()
# intents = []
# unique_intents = []
# text_input = []
# response_for_intent = {}
#
# for intent in data:
#     # List of unique intents
#     if intent.intent not in unique_intents:
#         unique_intents.append(intent.intent)
#
#     # Iterate through text associated with the intent
#     for text_obj in IntentText.objects.filter(intent=intent):
#         cleaned_texts = [clean(text) for text in text_obj.texts]
#         filtered_texts = [remove_stopwords(text) for text in cleaned_texts]  # Удаление стоп-слов
#         text_input.extend(filtered_texts)
#         intents.extend([intent.intent] * len(filtered_texts))
#
#         # Create a dictionary to hold responses for the intent
#         if intent.intent not in response_for_intent:
#             response_for_intent[intent.intent] = {}
#
#         # Add responses for different languages
#         response_for_intent[intent.intent][text_obj.language] = text_obj.responses


# Функция для случайной перестановки слов в тексте
def augment_text_with_word_permutation(text):
    words = text.split()
    random.shuffle(words)
    return ' '.join(words)


# Функция для добавления шума к тексту
def augment_text_with_noise(text, noise_level=0.1):
    words = text.split()
    noisy_words = [add_noise(word, noise_level) for word in words]
    return ' '.join(noisy_words)


# Функция для добавления шума к слову с определенной вероятностью
def add_noise(word, noise_level):
    if random.random() < noise_level:
        # Вставляем случайный символ в слово (можно настроить другие варианты)
        index = random.randint(0, len(word))
        random_char = chr(random.randint(1072, 1103))  # Случайная маленькая буква
        return word[:index] + random_char + word[index:]
    else:
        return word


# Вероятность аугментации для каждой из методов
permutation_probability = 0.2
noise_probability = 0.2

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
        cleaned_texts = [clean(text) for text in text_obj.texts]
        filtered_texts = [remove_stopwords(text) for text in cleaned_texts]  # Удаление стоп-слов

        augmented_texts = []
        for text in filtered_texts:
            augmented_text = text

            # Аугментация текста методом перестановки слов
            if random.random() < permutation_probability:
                augmented_text = augment_text_with_word_permutation(augmented_text)

            # Аугментация текста добавлением шума
            if random.random() < noise_probability:
                augmented_text = augment_text_with_noise(augmented_text)

            augmented_texts.append(augmented_text)

        text_input.extend(augmented_texts)
        intents.extend([intent.intent] * len(augmented_texts))

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
print('categorical_vec: ', len(categorical_vec))
print('num_classes: ', num_classes)

epochs = 100
embed_dim = 300
lstm_num = 50
output_dim = categorical_vec.shape[1]
print(output_dim)
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
loss, accuracy = model.evaluate(padded_sequences, categorical_vec)

# model.save('bot_model.keras')


# Дообучение
# Компилируйте модель
# optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
# loaded_model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

# # Дообучение модели
# loaded_model.fit(padded_sequences, categorical_vec, epochs=epochs, verbose=0)
# loss, accuracy = loaded_model.evaluate(padded_sequences, categorical_vec)
#
# # Сохраните обновленную модель
# loaded_model.save('updated_model.h5')

