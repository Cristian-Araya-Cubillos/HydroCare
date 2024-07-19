# Usar una imagen base con TensorFlow y Flask
FROM python:3.12.4-alpine3.20

# Crear el directorio de la aplicación
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . .

# Instalar Flask
RUN pip install --upgrade pip
RUN pip install flask
RUN pip install flask-cors
RUN pip install requests 
RUN pip install openai
RUN pip install Pillow
RUN pip install langchain pymongo bs4 openai tiktoken gradio requests lxml argparse
RUN pip install -U langchain-community

# Exponer el puerto en el que correrá la aplicación
EXPOSE 5000


# Ejecutar la aplicación
CMD ["python", "app.py"]
