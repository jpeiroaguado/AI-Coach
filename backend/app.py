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

# Cliente texto — Nova 2 Lite (eu-south-2)
client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION", "eu-south-2")
)
MODEL_ID = "eu.amazon.nova-2-lite-v1:0"

# Cliente imágenes — Stable Diffusion 3.5 Large (us-west-2)
imagen_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2"
)
IMAGE_MODEL_ID = "stability.sd3-5-large-v1:0"


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)

@app.route("/favicon.ico")
def favicon():
    return "", 204


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
            messages=[{"role": m["role"], "content": [{"text": m["content"]}]} for m in mensajes],
            inferenceConfig={
                "maxTokens": 8000,
                "temperature": 0.3
            }
        )

        respuesta_texto = response["output"]["message"]["content"][0]["text"]

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
        import traceback
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/generar-imagen", methods=["POST"])
def generar_imagen():
    try:
        datos = request.json

        modo = datos.get("modo", "personal")
        deporte = datos.get("deporte") or "entrenamiento físico"
        objetivo = datos.get("objetivo") or datos.get("objetivo_fisico") or "mejora del rendimiento"
        fase = datos.get("fase") or "temporada general"
        nivel = datos.get("nivel") or datos.get("categoria") or "intermedio"
        dias = datos.get("dias") or datos.get("duracion") or 3
        equipamiento = datos.get("equipamiento") or "material deportivo básico"

        # Descripción base según modo
        if modo == "preparador":
            descripcion = (
                f"high performance {deporte} training session, "
                f"goal: {objetivo}, phase: {fase}, level: {nivel}, "
                f"session duration or frequency: {dias}"
            )
        else:
            descripcion = (
                f"personal training plan, goal: {objetivo}, "
                f"{dias} days per week, using {equipamiento}, "
                f"fitness level: {nivel}"
            )

        prompt = (
            "Wide cinematic illustration, modern sports environment. "
            f"Main theme: {descripcion}. "
            "Show athletes training or preparing in a setting related to the sport "
            f"({deporte}), not necessarily a classic gym: it can be a court, track, pool "
            "or outdoor field depending on the sport. "
            "Dynamic but clean composition, soft gradients, warm lighting, "
            "no text, no logos, no UI elements, semi-realistic but stylized."
        )

        body = json.dumps({
            "prompt": prompt,
            "mode": "text-to-image",
            "aspect_ratio": "16:9",
            "output_format": "jpeg"
        })

        response = imagen_client.invoke_model(
            modelId=IMAGE_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        imagen_base64 = result["images"][0]

        return jsonify({"ok": True, "imagen": imagen_base64})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": str(e)}), 500
    

@app.route("/generar-imagen-dia", methods=["POST"])
def generar_imagen_dia():
    try:
        datos = request.json
        dia = datos.get("dia", "Día 1")
        ejercicios = datos.get("ejercicios", [])      # lista de strings
        grupo = datos.get("grupo_muscular", "")       # ej. "Pecho y Tríceps"
        objetivo_global = datos.get("objetivo", "")   # ej. "pérdida de peso", "mejorar resistencia corriendo"

        ejercicios_limpios = [e for e in ejercicios if e]
        base_musculos = grupo or ", ".join(ejercicios_limpios[:2]) or "full body"

        concepto_objetivo = objetivo_global or "general fitness"

        prompt = (
            f"Minimalist fitness anatomy diagram for {dia}. "
            f"Target muscle groups: {base_musculos}. "
            f"Training goal: {concepto_objetivo}. "
            "Show a single human body silhouette in neutral grey tones, "
            "without any colored shading on most of the body one or two silhouettes, "
            "depending on how many parts are needed to show that muscle group. "
            "Only highlight the target muscle areas using bright color glow or gradients "
            "Exactly on chest, arms, legs or back according to the target muscle groups. "
            "The rest of the silhouette must remain grey and uncolored. "
            "Pure white background (#FFFFFF), flat semi-realistic style, "
            "no exercise sequence, no equipment, no text, no numbers, no labels, no UI elements."
        )

        body = json.dumps({
            "prompt": prompt,
            "mode": "text-to-image",
            "aspect_ratio": "16:9",
            "output_format": "jpeg"
        })

        response = imagen_client.invoke_model(
            modelId=IMAGE_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        imagen_base64 = result["images"][0]

        return jsonify({"ok": True, "imagen": imagen_base64})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
