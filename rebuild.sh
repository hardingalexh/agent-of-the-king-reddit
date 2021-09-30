docker kill agent-of-the-king-reddit
docker rm agent-of-the-king-reddit
docker build ./ -t agent-of-the-king-reddit
docker run --name agent-of-the-king-reddit --restart always -d agent-of-the-king-reddit