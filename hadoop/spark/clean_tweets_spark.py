from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import udf, col, to_timestamp
from pyspark.sql.types import FloatType, ArrayType, StringType
import pandas as pd
import numpy as np
from typing import List
from subprocess import Popen

from clean_tweets import clean_text


def clean_tweets(hdfs_tweets_path, save_hdfs_path="hdfs://sandbox.hortonworks.com:8020/user/flume/cleaned_tweets"):
    """
    Reads tweet from hdfs_tweets_path, cleans them and saves in save_hdfs_path.
    """

    clean_text = udf(clean_text, returnType=ArrayType(StringType()))

    spark = SparkSession\
        .builder\
        .appName("Transforming data frame and evaluation")\
        .getOrCreate()

    sql_context = SQLContext(spark)

    tweets_path = "hdfs://sandbox.hortonworks.com:8020/user/flume/tweets/FlumeData.1558869963212"  # example file path
    tweets = spark.read.csv(hdfs_tweets_path)\
        .select(col("_c0").alias("id"), col("_c1").alias("text"), col("_c2").alias("created_at"), col("_c5").alias("user"), col("_c6").alias("screen_name"))

    # Czyszczenie danych
    tweets_cleaned = tweets.withColumn("text", clean_text("text"))  # To jest sparkowa ramka danych z wyczyszczonymi tweetami
    tweets_cleaned = tweets_cleaned.withColumn("text)
    tweets_date_format = "EEE MMM d hh:mm:ss '+0000' yyyy"
    tweets_cleaned = tweets_cleaned.withColumn("created_at", to_timestamp(tweets_cleaned.created_at, tweets_date_format))
    tweets_cleaned.write.json(save_hdfs_path)
    

if __name__ == "__main__":



    