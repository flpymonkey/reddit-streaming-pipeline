# This is a helper script to build and publish docker images
# used in the repository to docker hub
echo "=> Logging into docker hub"
docker login -u bencj96

echo "=> Building and pushing docker images"
echo "=> Reddit Producer"
cd reddit_producer
docker build -t bencj96/reddit_producer:latest .
docker push bencj96/reddit_producer:latest

echo "=> Spark Stream Processor"
cd ../spark
docker build -t bencj96/spark_stream_processor:latest .
docker push bencj96/spark_stream_processor:latest

echo "=> Cassandra"
cd ../cassandra
docker build -t bencj96/cassandra:latest .
docker push bencj96/cassandra:latest

echo "=> Grafana"
cd ../grafana
docker build -t bencj96/grafana:latest .
docker push bencj96/grafana:latest