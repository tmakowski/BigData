from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import Lasso
from typing import List


cv = joblib.load("models/count_vectorizer.h5")
lasso = joblib.load("models/tweets_model.h5")


def evaluate_tweet(words: List[str]) -> float:
    pred = lasso.predict(cv.transform([" ".join(words)]))[0]
    return float(pred)