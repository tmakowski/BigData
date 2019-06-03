from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import udf, col, to_timestamp
from pyspark.sql.types import FloatType, ArrayType, StringType

import pandas as pd
import numpy as np
from typing import List
from subprocess import Popen, PIPE
import logging
import argparse
import time
import os

from evaluate_tweets_model import evaluate_tweet
from clean_tweets import clean_text


def hadoop_listdir(path: str) -> List[str]:
    """
    Lists all files in path 'path' in hdfs.
    """
    process = Popen("hadoop fs -ls {}".format(path), shell=True, stdout=PIPE, stderr=PIPE)
    std_out, std_err = process.communicate()
    logging.debug(std_err)
    file_strings = [string for string in std_out.split(b"\n") if len(string) > 0][1:]
    files = [string.split(b" ")[-1].decode("UTF-8") for string in file_strings]
    return files

def clean_evaluate_save_tweets(path: str, save_file_path: str, verbose: bool=False, save_locally: bool=False) -> None:
    """
    Clean and evaluates tweets in path 'path' of hdfs and saves them in 'save_file_path' in hdfs.
    If save_locally is set to True, save_file_path must be a local path.
    """
    hdfs_root = "hdfs://sandbox.hortonworks.com:8020"
    tweets_path = hdfs_root + path
    tweets = spark.read.csv(tweets_path)\
        .select(col("_c0").alias("id"), col("_c1").alias("text"), col("_c2").alias("created_at"), col("_c5").alias("user"), col("_c6").alias("screen_name"))

    # Data cleaning
    tweets_cleaned = tweets.withColumn("text_cleaned", clean_text("text"))  # To jest sparkowa ramka danych z wyczyszczonymi tweetami
    tweets_date_format = "EEE MMM d hh:mm:ss '+0000' yyyy"
    tweets_cleaned = tweets_cleaned.withColumn("created_at", to_timestamp(tweets_cleaned.created_at, tweets_date_format))

    # Neural net evaluation
    tweets_evaluated = tweets_cleaned.withColumn("evaluation", evaluate("text"))
    tweets_evaluated.createOrReplaceTempView("Tweets")

    if verbose:
        tweets_evaluated.show()
    if not save_locally:
        save_file_path = hdfs_root + save_file_path
    tweets_evaluated.select("id", "created_at", "evaluation").write.csv(save_file_path, "append")
    logging.info("Appended evaluated tweets to csv at {}".format(save_file_path))


parser = argparse.ArgumentParser(description='Starts a script evaluating incoming tweets in a given directory')
parser.add_argument('--waiting_time', type=int, default=5,
                    help='Seconds to wait in each iteration')
parser.add_argument('--tweets_dir', type=str, default='/user/flume/tweets',
                    help='Directory in hdfs in which incoming tweets are stored')
parser.add_argument('--save_file_path', type=str, default='/user/spark/tweets_evaluated',
                    help='Directory in hdfs in which evaluated tweets are stored')
parser.add_argument('--save_locally', action='store_true',
                    help='Option to save files locally instead of in hdfs')
parser.add_argument('--log_file', type=str, required=False,
                    help="File in which to store logs")
parser.add_argument('-v', '--verbose', action='store_true',
                    help='If given, extra info is printed')
parser.add_argument('--exclude_files_path', type=str,
                    help="""Path to file with file names to exclude. Use list of file names to exclude from computations. 
                    Useful if data has been already preprocessed once. You can use preprocessed_files.txt which is automatically created
                    after running this script and containts all preprocessed files in the lust run.""")
args = parser.parse_args()

logging_level = logging.INFO if args.verbose else logging.WARN
if args.log_file:
    logging.basicConfig(filename='tweets_evaluation.log',level=logging.DEBUG)
else:
    logging.basicConfig(level=logging_level)

clean_text = udf(clean_text, returnType=ArrayType(StringType()))
evaluate = udf(evaluate_tweet)

spark = SparkSession\
    .builder\
    .appName("Transforming data frame and evaluation")\
    .getOrCreate()

sql_context = SQLContext(spark)

evaluated_files = set()

if args.exclude_files_path:
    with open(args.exclude_files_path) as exluded_files_file:
        for line in excluded_files_file.readlines():
            evaluated_files.add(line.strip())

preprocessed_files_path = "preprocessed_files.txt"
with open(preprocessed_files_path, "w") as preprocessed_files:
    pass

while True:
    files = hadoop_listdir(args.tweets_dir)
    for f in files:
        if not f in evaluated_files:
            logging.info("Evaluating (hdfs) file {}".format(os.path.join("/user/flume/tweets", f)))
            clean_evaluate_save_tweets(f, args.save_file_path, verbose=args.verbose, save_locally=args.save_locally)
            evaluated_files.add(f)
            with open(preprocessed_files_path, "a") as preprocessed_files:
                preprocessed_files.write(f + "\n")
            time.sleep(args.waiting_time)
