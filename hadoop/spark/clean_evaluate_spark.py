from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import udf, col
from pyspark.sql.types import FloatType
import pandas as pd
import numpy as np
from typing import List


# TODO: Wsadzić tu funkcję Tomka
@udf
def clean_data(text: str) -> List[str]:
    words = text.split(" ")
    return [word.lower() for word in words]

# TODO: Tutaj wstawić rzeczywistą ewaluację sieci
@udf
def evaluate(words: List[str]) -> float:
    return len(words)

# example file_path
spark = SparkSession\
    .builder\
    .appName("Transforming data frame and evaluation")\
    .getOrCreate()

sql_context = SQLContext(spark)

file_path = "hdfs://sandbox.hortonworks.com:8020/user/flume/tweets/FlumeData.1558869963212"  # example file path
df = spark.read.csv(file_path)\
    .select(col("_c0").alias("id"), col("_c1").alias("text"), col("_c2").alias("created_at"), col("_c5").alias("user"), col("_c6").alias("screen_name"))

# Czyszczenie danych
cleaned_data = df.withColumn("text", clean_data("text"))  # To jest sparkowa ramka danych z wyczyszczonymi tweetami

# Ewaluacjia sieci
results_data = df.withColumn("evaluation", evaluate("text"))
print(results_data.show())

