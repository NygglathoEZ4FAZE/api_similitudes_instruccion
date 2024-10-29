# Usa una imagen base de Python 3.11
FROM python:3.11

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos
COPY requirements.txt requirements.txt

# Instala las dependencias sin caché para reducir el tamaño de la imagen
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto 8000
EXPOSE 8000

# Ejecuta las migraciones y luego inicia el servidor con Gunicorn
CMD HOME=/root python3 manage.py migrate && gunicorn api_mejor_respuesta.wsgi:application --bind 0.0.0.0:$PORT

