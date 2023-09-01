import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
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
loss, accuracy = model.evaluate(padded_sequences, categorical_vec)

model.save('my_model.h5')

# Сохраните модель в файл
# model.save('lstmModel')
# Загрузка модели
# loaded_model = load_model('lstmModel')
# Дообучение модели
# loaded_model.fit(padded_sequences, categorical_vec, epochs=epochs, verbose=0, initial_epoch=epochs)