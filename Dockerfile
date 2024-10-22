# Установка Python из официального базового образа
FROM python:3.10.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip list

COPY . .

EXPOSE 8000

CMD ["python3", "src/main.py"]