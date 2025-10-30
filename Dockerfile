FROM python:3.13.9-alpine3.22

WORKDIR /app

# Instala netcat para que el script de espera (entrypoint.sh) pueda verificar el puerto 5432 de la DB
RUN apk update && \
    apk add --no-cache netcat-openbsd

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip list

COPY . .

# Copia el script de inicialización y dale permisos de ejecución
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Define el nuevo ENTRYPOINT: ejecuta el script de espera
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# El CMD se convierte en el comando final a ejecutar DESPUÉS de que la DB esté lista.
CMD ["python", "main.py"]