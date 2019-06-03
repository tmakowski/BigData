import numpy as np
import keras
import gensim.downloader as api
from typing import List


glove_vectors = api.load("glove-twitter-50")
GLOVE_SIZE = 50

# In Keras you can save model with architecture, weights and all other stuff with one file
# Just load it with one function and it should work
model = keras.models.load_model('model.h5')

def get_vector(word, glove_vectors):
    """For a given word returns it's vector representation"""
    try:
        vec = glove_vectors.get_vector(word)
    except KeyError:
        # we don't want it to be all zeros, because all zeros vectors will be masked (ignored)
        vec = np.random.normal(0, 0.0001, 50)  
    return vec

def tweet_to_result(words, model, GLOVE_SIZE, glove_vectors):
    """For given words sequence, calculates LSTM network output
    Inputs:
    -------
    words - list of string objects (without stop words, without special symbols as ?,!...)
    model - keras model loaded from file
    GLOVE_SIZE - size of glove vector
    glove_vectors - loaded at the begining from program from gensim library

    Outputs:
    --------
    model_prediction - one number (float), a prediction for whole word sequence (words)
    """
    tweet_len = len(words)
    x_to_predict = np.zeros((1, tweet_len, GLOVE_SIZE))
    for j, word in enumerate(words):
        x_to_predict[0, j, :] = get_vector(word, glove_vectors)
    return model.predict(x_to_predict)

def evaluate_rnn(words: List[str]) -> float:
    return tweet_to_result(words, model, GLOVE_SIZE, glove_vectors)[0]