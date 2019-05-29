from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import udf, col, to_timestamp
from pyspark.sql.types import FloatType, ArrayType, StringType
import pandas as pd
import numpy as np
from typing import List

#from evaluate_net import evaluate_rnn
from clean_tweets import clean_text


def evaluate_rnn(words):  # simple function for tests TODO: remove and insert real model evaluation here
    return len(words) + 0.1

clean_text = udf(clean_text, returnType=ArrayType(StringType()))
evaluate = udf(evaluate_rnn)

# example file_path
spark = SparkSession\
    .builder\
    .appName("Transforming data frame and evaluation")\
    .getOrCreate()

sql_context = SQLContext(spark)

tweets_path = "hdfs://sandbox.hortonworks.com:8020/user/flume/tweets/FlumeData.1558869963212"  # example file path
tweets = spark.read.csv(tweets_path)\
    .select(col("_c0").alias("id"), col("_c1").alias("text"), col("_c2").alias("created_at"), col("_c5").alias("user"), col("_c6").alias("screen_name"))

# Czyszczenie danych
tweets_cleaned = tweets.withColumn("text", clean_text("text"))  # To jest sparkowa ramka danych z wyczyszczonymi tweetami
tweets_date_format = "EEE MMM d hh:mm:ss '+0000' yyyy"
tweets_cleaned = tweets_cleaned.withColumn("created_at", to_timestamp(tweets_cleaned.created_at, tweets_date_format))

# Ewaluacja sieci
tweets_evaluated = tweets_cleaned.withColumn("evaluation", evaluate("text"))
tweets_evaluated.createOrReplaceTempView("Tweets")
tweets_evaluated.show()


# Wczytanie danych z cen
prices_path = "hdfs://sandbox.hortonworks.com:8020/user/flume/prices/FlumeData.1558870162486"
prices = spark.read.csv(prices_path, header=True)
prices.createOrReplaceTempView("Prices")
prices = prices.withColumn("timestamp", to_timestamp(prices.timestamp))
