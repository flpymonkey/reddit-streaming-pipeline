# from nltk.sentiment import SentimentIntensityAnalyzer
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import udf, from_json, col, from_unixtime, avg, current_timestamp
# from pyspark.sql.types import StringType, StructType, StructField, IntegerType, BooleanType, FloatType
# import uuid

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext 
from pyspark.streaming.kafka import KafkaUtils 
from pyspark.sql.types import StringType, StructType, StructField, IntegerType, BooleanType, FloatType


# Add debugging logs
import logging

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

def log_df(batch_df, batch_id):
    logging.info(f"Batch ID: {batch_id}")
    batch_df.show(truncate=False)



sc = SparkContext(appName="KafkaStreamProcessor") 
ssc = StreamingContext(sc, 10)

spark: SparkSession = SparkSession.builder \
    .appName("StreamProcessor") \
    .config('spark.cassandra.connection.host', 'cassandra') \
    .config('spark.cassandra.connection.port', '9042') \
    .config('spark.cassandra.output.consistency.level','ONE') \
    .getOrCreate()

spark.sparkContext.setLogLevel('ERROR')

# Kafka configurations
kafka_bootstrap_servers = "kafkaservice:9092"
kafka_topic = "redditcomments"

kafka_stream = KafkaUtils.createDirectStream(ssc, [kafka_topic], {"metadata.broker.list": kafka_bootstrap_servers})


comment_schema = StructType([
    StructField("id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("author", StringType(), True),
    StructField("body", StringType(), True),
    StructField("subreddit", StringType(), True),
    StructField("upvotes", IntegerType(), True), #int
    StructField("downvotes", IntegerType(), True), #int
    StructField("over_18", BooleanType(), True), #bool
    StructField("timestamp", FloatType(), True), #timestamp
    StructField("permalink", StringType(), True),
])


def process_message(message): 
    logger.info(f"Received message: {message}")
    if not message.isEmpty():
        df = spark.read.json(message.map(lambda x: x[1]), comment_schema)

        # Write DataFrame to Cassandra 
        df.write.format("org.apache.spark.sql.cassandra").mode('append').options(table="comments", keyspace="reddit").save()

kafka_stream.foreachRDD(lambda rdd: rdd.foreach(process_message))
ssc.start()
ssc.awaitTermination()


spark.streams.awaitAnyTermination()