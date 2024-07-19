from flask import Flask, request, jsonify, render_template
import os
import json
import csv
import openai
from PIL import Image
from io import BytesIO
import base64
app = Flask(__name__, static_url_path='/static', static_folder='static')

# Configura tu clave API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Nombre del archivo donde se guardará el historial
HISTORIAL_FILE = 'historial.json'



# Función para cargar el historial desde el archivo
def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

# Función para guardar el historial en el archivo
def guardar_historial(historial):
    with open(HISTORIAL_FILE, 'w') as file:
        json.dump(historial, file)

def cargar_prompts(filename='agronomo_prompt.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            prompts = json.load(file)
            for prompt in prompts:
                historial.append({"role": prompt["role"], "content": prompt["content"]})


# Inicializar el historial de la conversación
historial = cargar_historial()
cargar_prompts()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preguntas-frecuentes')
def preguntasFrecuentes():
    return render_template('preguntas-frecuentes.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/alerta')
def alerta():
    return render_template('alerta.html')


@app.route('/chat-principal')
def chatPrincipal():
    return render_template('chat-principal.html', historial=historial)

@app.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html')

@app.route('/chat_imagen')
def chat_imagen():
    return render_template('chat_imagen.html')


@app.route('/chat', methods=['POST'])
def chat():
    global historial
    mensaje = request.json['mensaje']
    
    # Añadir el mensaje del usuario al historial
    historial.append({"role": "user", "content": mensaje})
    
    # Enviar el historial a la API
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historial
    )
    
    # Obtener la respuesta y añadirla al historial
    respuesta = response.choices[0].message.content
    historial.append({"role": "assistant", "content": respuesta})
    
    # Guardar el historial actualizado
    guardar_historial(historial)
    
    return jsonify({"respuesta": respuesta})

@app.route('/chat_frecuente', methods=['POST'])
def chat_frecuente():
    print("mensaje")
    historial_temp = []
    mensaje = request.json['mensaje']
    print("mensaje")
    # Añadir el mensaje del usuario al historial
    historial_temp.append({"role": "user", "content": mensaje})
    
    # Enviar el historial a la API
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historial_temp
    )
    
    # Obtener la respuesta y añadirla al historial
    respuesta = response.choices[0].message.content
    historial_temp.append({"role": "assistant", "content": respuesta})
    
    return jsonify({"respuesta": respuesta})

# Ruta para obtener los datos del gráfico
@app.route('/get_chart_data')
def get_chart_data():
    csv_file_path = os.path.join(app.root_path, 'data', 'Crop_recommendation.csv')#os.path.join(app.root_path, 'data', 'iris.csv')
    json_file_path = os.path.join(app.root_path, 'data', 'crop_json.json')#os.path.join(app.root_path, 'data', 'iris_chart_data.json')
    
    #sepal_length = []
    #sepal_width = []
    #petal_length = []
    #petal_width = []
    #label = []
    temperature = []
    humidity = []
    ph = []
    rainfall = []
    label = []
    # Procesar el archivo CSV
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            temperature.append(float(row['temperature']))
            humidity.append(float(row['humidity']))
            ph.append(float(row['ph']))
            rainfall.append(float(row['rainfall']))
            label.append(row['label'])
    
    # Estructurar los datos para los gráficos
    data = {
        "tempData": {
            "labels": label,
            "datasets": [{
                "label": 'Temperature',
                "data": temperature,
                "backgroundColor": 'rgba(75, 192, 192, 0.2)',
                "borderColor": 'rgba(75, 192, 192, 1)',
                "borderWidth": 1
            }]
        },
        "humidityData": {
            "labels": label,
            "datasets": [{
                "label": 'Humidity',
                "data": humidity,
                "backgroundColor": 'rgba(153, 102, 255, 0.2)',
                "borderColor": 'rgba(153, 102, 255, 1)',
                "borderWidth": 1
            }]
        },
        "phData": {
            "labels": label,
            "datasets": [{
                "label": 'ph',
                "data": ph,
                "backgroundColor": 'rgba(255, 206, 86, 0.2)',
                "borderColor": 'rgba(255, 206, 86, 1)',
                "borderWidth": 1
            }]
        },
        "rainfallhData": {
            "labels": label,
            "datasets": [{
                "label": 'Lluvia Caida',
                "data": rainfall,
                "backgroundColor": 'rgba(255, 99, 132, 0.2)',
                "borderColor": 'rgba(255, 99, 132, 1)',
                "borderWidth": 1
            }]
        }
    }
    
    # Guardar los datos en un archivo JSON
    with open(json_file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    return jsonify(data)


# Ruta para manejar la subida de imágenes y las preguntas sobre ellas
@app.route('/upload_image', methods=['POST'])
def upload_image():
    # Obtén el archivo de la imagen y la pregunta desde la solicitud
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            # Lee el archivo y conviértelo a base64
            image_data = file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # Obtén la pregunta desde la solicitud
            question = request.form.get('question', "What’s in this image?")

            # Llama a la API de OpenAI
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            # Devuelve la respuesta del modelo
            return jsonify({"response": response.choices[0].message.content})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')