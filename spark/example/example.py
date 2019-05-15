from pyspark import SparkConf
from pyspark import SparkContext as sc
from pyspark.sql import SparkSession
import pandas as pd
from operator import add
import sys

spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

lines = spark.read.text(sys.argv[1]).rdd.map(lambda r: r[0])
counts = lines.flatMap(lambda x: x.split(' ')) \
              .map(lambda x: (x, 1)) \
              .reduceByKey(add)
output = counts.collect()
for (word, count) in output:
    print("{}: {}".format(word, count))

print(counts)