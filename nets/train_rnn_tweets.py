import pandas as pd
import numpy as np
from itertools import cycle

import gensim.downloader as api

from sklearn.model_selection import train_test_split

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Masking
from keras.callbacks import EarlyStopping, ModelCheckpoint


def ohe(data, label_name="up"):
    """One hot encodes column named label_name of data"""
    label_array = np.zeros((len(data), 2), dtype=np.int8)
    for index, label in enumerate(data[label_name]):
        label_array[index, label] = 1
    return label_array


print("Loading glove word vectors. Please wait.")
GLOVE_VECTORS = api.load("glove-twitter-50")  # may take a while
GLOVE_SIZE = 50


def get_vector(word):
    """For a given word returns it's vector representation to be fed into model"""
    try:
        vec = GLOVE_VECTORS.get_vector(word)
    except KeyError:
        # we don't want it to be all zeros, because all zeros vectors will be masked (ignored)
        vec = np.random.normal(0, 0.0001, 50)
    return vec


def train_generator(tweets, batch_size):
    """Generates data form tweets in batches of size batch_size"""

    sentences = [sentence.split(" ") for sentence in tweets["cleaned_text"]]
    labels = ohe(tweets)

    max_len = max([len(sentence) for sentence in sentences])

    x_train = np.zeros((batch_size, max_len, GLOVE_SIZE))
    y_train = np.zeros((batch_size, 2))
    i = 0
    for sentence, label in cycle(zip(sentences, labels)):
        for j, word in enumerate(sentence):
            x_train[i, j, :] = get_vector(word)
        y_train[i, :] = label
        if i == batch_size - 1:
            i = 0
            yield x_train, y_train
        else:
            i += 1


def get_model():
    model = Sequential()

    model.add(Masking(mask_value=0., input_shape=(None, 50)))

    # Masking layer for pre-trained embeddings
    model.add(Masking(mask_value=0.0))

    # Recurrent layer
    model.add(LSTM(64, return_sequences=False,
                   dropout=0.1, recurrent_dropout=0.1))

    # Fully connected layer
    model.add(Dense(64, activation='relu'))

    # Dropout for regularization
    model.add(Dropout(0.5))

    # Output layer
    model.add(Dense(2, activation='softmax'))

    # Compile the model
    model.compile(
        optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model


if __name__ == "__main__":
    data = pd.read_csv("../data/tweets_prices.csv", index_col=0, parse_dates=[0])
    tweets = data[data["text"].notna()]
    tweets = tweets.drop(["favorite_count", "retweet_count", "id"], axis=1)
    tweets["cleaned_text"] = tweets["cleaned_text"].apply(str)
    tweets["up"] = [1 if profit > 0 else 0 for profit in tweets.profit]  # careful here
    tweets_train, tweets_test, y_train, y_test = train_test_split(tweets, tweets.up, test_size=0.10, random_state=42)

    # Create callbacks
    callbacks = [EarlyStopping(monitor='val_loss', patience=10),
                 ModelCheckpoint('model.h5', save_best_only=True, save_weights_only=False)]

    model = get_model()

    model.fit_generator(train_generator(tweets_train, 1000),
                        validation_data=train_generator(tweets_test, 1),
                        steps_per_epoch=50,
                        validation_steps=50,
                        epochs=10,
                        verbose=1,
                        callbacks=callbacks)
