from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import pandas as pd
import numpy as np
from operator import add
from typing import List


def clean_data(text: str) -> List[str]:
    words = text.split(" ")
    return [word.lower() for word in words]


def evaluate(words: List[str]) -> float:
    return len(words) * np.random.normal()


spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

tweets = pd.DataFrame({
    "date": [1, 2, 3, 4],
    "text": ["I want to go to Radom", "I love you", "Elon Musk will be proud", "I am gonna buy myself a Tesla"]
})
sdf = spark.createDataFrame(tweets)


# Transforming dataframe first: cleaning tweet texts
transformed = sdf.rdd.map(lambda row: clean_data(row["text"]))

print(transformed)

for x in transformed.collect():
    print(x)

# Now calculating an evaluation of each text represented as list of words
print("Evaluation:")
evaluated = transformed.map(lambda words: evaluate(words))

for x in evaluated.collect():
    print(x)
