docker build -t yinjian-sensitiveword .
docker run -it -d --name=p1 -p 9500:8501 yinjian-sensitiveword
