FROM python:3.7.4-slim
WORKDIR /app
copy requirements.txt .
RUN pip install  --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
copy . .
#
CMD ["nohup", "streamlit", "run", "app.py"]
#或者 CMD ["streamlit", "run", "app.py"]

#CMD ["python", "app_2.py"]

