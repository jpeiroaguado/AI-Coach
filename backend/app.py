from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import boto3
import json
import os

load_dotenv()

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app = Flask(__name__)
CORS(app)

client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION", "eu-south-2")
)

MODEL_ID = "eu.amazon.nova-2-lite-v1:0"

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

@app.route("/favicon.ico")
def favicon():
    return '', 204

@app.route("/generar-plan", methods=["POST"])
def generar_plan():
    try:
        datos = request.json
        historial = datos.get("historial", [])

        from prompts import construir_prompt
        prompt = construir_prompt(datos)

        mensajes = historial + [{"role": "user", "content": prompt}]

        response = client.converse(
            modelId=MODEL_ID,
            messages=[{"role": m["role"], "content": [{"text": m["content"]}]} for m in mensajes]
        )

        respuesta_texto = response["output"]["message"]["content"][0]["text"]

        # Limpiar bloques markdown si el modelo los añade
        if "```json" in respuesta_texto:
            respuesta_texto = respuesta_texto.split("```json")[1].split("```")[0].strip()
        elif "```" in respuesta_texto:
            respuesta_texto = respuesta_texto.split("```")[1].split("```")[0].strip()

        try:
            plan = json.loads(respuesta_texto)
        except json.JSONDecodeError:
            plan = {"texto": respuesta_texto}

        return jsonify({"ok": True, "plan": plan})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
