FROM python:3.10.12

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY . .
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y gcc
RUN rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

CMD ["python3", "src/main.py"]