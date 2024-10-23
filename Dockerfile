FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "src/main.py"]