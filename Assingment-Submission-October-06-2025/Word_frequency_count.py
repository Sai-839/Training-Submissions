# rdd_wordcount.py (minimal)
from pyspark.sql import SparkSession
import re

spark = SparkSession.builder.appName("RDDWordCount").getOrCreate()
sc = spark.sparkContext

path = r"C:\Users\saisu\Desktop\KeyPixel\Training-Submissions\Assingment-Submission-October-06-2025\Objectives and Goals.txt"
rdd = sc.textFile(path)
words = (rdd
         .map(lambda s: re.sub(r"[^A-Za-z0-9']+", " ", s).lower())
         .flatMap(lambda s: s.split())
         .filter(lambda w: len(w) >= 2))
counts = (words
          .map(lambda w: (w, 1))
          .reduceByKey(lambda a, b: a + b)
          .sortBy(lambda x: (-x[1], x[0])))

for w, c in counts.take(50):
    print(w, c)

spark.stop()
