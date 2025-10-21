FROM python:3.13.9-alpine3.22


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip list

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
