# 🏋️ AI-Coach — Asistente de Entrenamiento con Inteligencia Artificial

> Proyecto Final · Especialització IA + Big Data · AWS Bedrock  
> Equipo: **Javier Peiro** (Frontend + Flask + Docker) · **Santiago** (IA + AWS Bedrock)

---

## ¿Qué es AI-Coach?

AI-Coach es un asistente conversacional que genera **planes de entrenamiento personalizados** usando IA generativa. El usuario describe su condición física y objetivos, y el sistema crea un plan adaptado a su perfil en segundos.

El plan puede refinarse mediante **feedback conversacional**: si el resultado no convence, el usuario puede pedir ajustes ("hazlo menos intenso", "no tengo mancuernas") y la IA lo corrige manteniendo el contexto de la conversación.

**Dos modos disponibles:**
- 🏋️ **Modo Personal** — plan de fuerza, cardio o mixto según peso, objetivo y días disponibles
- 🏅 **Modo Preparador Físico** — sesiones adaptadas por deporte (fútbol, baloncesto, natación, atletismo...), categoría y fase de temporada

---

## 🤖 Tecnología IA utilizada

| Componente | Detalle |
|---|---|
| **Plataforma** | AWS Bedrock |
| **Modelo de texto** | Amazon Nova 2 Lite (`amazon.nova-2-lite-v1:0`) |
| **Modelo de imágenes** | Stable Diffusion 3.5 Large (`stability.sd3-5-large-v1:0`) |
| **Tipo de IA** | IA Generativa — consume modelos fundacionales ya entrenados |
| **Técnica principal** | Prompt Engineering dinámico parametrizado |
| **Ajuste de resultados** | Historial de conversación con feedback del usuario |
| **Backend** | Python 3 + Flask |
| **Infraestructura** | Docker + Docker Compose |
| **Formato de respuesta** | JSON estructurado renderizado en el frontend |

### ¿Por qué AWS Bedrock y no entrenar un modelo propio?

Bedrock permite **consumir modelos ya entrenados** sin necesidad de infraestructura propia ni datos de entrenamiento. La diferencia clave:

| ML Clásico | AWS Bedrock |
|---|---|
| Tú entrenas el modelo | Tú consumes un modelo ya entrenado |
| Necesitas datasets propios | Solo necesitas diseñar buenos prompts |
| Infraestructura compleja | Llamada a una API |

> **Modelo de texto:** Amazon Nova 2 Lite — ventana de contexto de 1M tokens, disponible en `eu-south-2` (España). Model ID: `amazon.nova-2-lite-v1:0`  
> **Modelo de imagen:** Stable Diffusion 3.5 Large — generación de imágenes de alta calidad a partir de texto. Model ID: `stability.sd3-5-large-v1:0`

---

## 🏗️ Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────┐
│                  USUARIO (Navegador)                    │
│       Rellena formulario en index.html                  │
└─────────────────────┬───────────────────────────────────┘
                      │  fetch() POST /generar-plan
                      │  fetch() POST /generar-imagen
                      │  fetch() POST /generar-imagen-dia
                      ▼
┌─────────────────────────────────────────────────────────┐
│             BACKEND — Flask (Python)                    │
│  app.py recibe datos + historial de conversación        │
│  prompts.py construye el prompt dinámico por modo       │
└──────────┬──────────────────────────┬───────────────────┘
           │ boto3 converse()          │ boto3 invoke_model()
           ▼                          ▼
┌─────────────────────┐  ┌───────────────────────────────┐
│   AWS BEDROCK       │  │        AWS BEDROCK            │
│  Nova 2 Lite        │  │  Stable Diffusion 3.5 Large   │
│  → Plan JSON        │  │  → Imagen portada / viñetas   │
└─────────────────────┘  └───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          FRONTEND — HTML + CSS + JavaScript             │
│  Muestra el plan, imágenes y permite dar feedback       │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del proyecto

```
AI-Coach/
├── .env                        ← Credenciales AWS (NO subir a GitHub)
├── .gitignore
├── Dockerfile                  ← Imagen del contenedor Python + Flask
├── docker-compose.yml          ← Orquestación del servicio
├── requirements.txt            ← Dependencias Python
├── README.md
│
├── backend/
│   ├── app.py                  ← Flask: /generar-plan, /generar-imagen, /generar-imagen-dia
│   └── prompts.py              ← Prompts dinámicos por modo y perfil
│
└── frontend/
    ├── index.html              ← Interfaz principal
    ├── css/
    │   └── style.css           ← Estilos, diseño responsive y @media print
    └── js/
        └── app.js              ← Lógica del formulario + fetch a Flask
```

---

## 🔌 Endpoints API

| Endpoint | Método | Descripción |
|---|---|---|
| `/generar-plan` | POST | Genera el plan de entrenamiento con Nova 2 Lite. Acepta historial conversacional para feedback |
| `/generar-imagen` | POST | Genera la imagen de portada con SD 3.5 basada en deporte, objetivo y nivel del usuario |
| `/generar-imagen-dia` | POST | Genera la ilustración anatómica de cada día basada en grupo muscular y objetivo |

### `.env` — nunca subir a GitHub
```
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=eu-south-2
```

### `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "backend/app.py"]
```

### `docker-compose.yml`
```yaml
version: '3.8'
services:
  ai-coach:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./frontend:/app/frontend
      - ./backend:/app/backend
    restart: unless-stopped
```

### `requirements.txt`
```
flask
flask-cors
boto3
python-dotenv
```

---

## 📥 Datos de entrada

**Modo Personal:**
- Edad, peso (kg), altura (cm)
- Objetivo: ganar músculo / perder peso / resistencia / flexibilidad
- Nivel: principiante / intermedio / avanzado
- Días disponibles por semana (1–7)
- Equipamiento disponible (tags: mancuernas, barra, bandas elásticas, etc.)
- Observaciones opcionales

**Modo Preparador Físico:**
- Deporte: fútbol, baloncesto, natación, atletismo, ciclismo, tenis...
- Categoría: benjamín / alevín / infantil / juvenil / amateur / profesional
- Objetivo físico: fuerza, resistencia, velocidad, explosividad
- Fase de temporada: pretemporada / competición / recuperación
- Duración de la sesión (minutos)
- Observaciones opcionales

## 📤 Salida generada por la IA

- **Imagen de portada** contextual al deporte/objetivo (Stable Diffusion 3.5)
- **Plan estructurado por días** con ejercicios, series, repeticiones y descanso (Nova 2 Lite)
- **Ilustración anatómica por día**: silueta humana con los grupos musculares del día resaltados (Stable Diffusion 3.5)
- Consejos de recuperación y nutrición básicos
- **Refinamiento conversacional**: el usuario puede ajustar el plan con lenguaje natural

---

## ▶️ Cómo ejecutar el proyecto

> Requiere únicamente tener **Docker** instalado.

```bash
# 1. Crear el .env con tus credenciales AWS

# 2. Primera vez — construir y arrancar
docker compose up --build

# 3. Las siguientes veces
docker compose up

# 4. Abrir en el navegador
# http://localhost:5000

# 5. Parar el servidor
docker compose down
```

---

## ⚠️ Reflexión crítica — Limitaciones de la IA

**1. Alucinaciones en el plan**  
Nova 2 Lite puede generar ejercicios inadecuados para el nivel indicado. El plan debe tratarse siempre como una sugerencia, nunca como prescripción médica.

**2. Calidad del prompt**  
Un prompt mal construido produce planes genéricos. Gran parte del trabajo está en diseñar prompts que generen respuestas consistentes y estructuradas en JSON válido.

**3. Limitaciones del modelo de imagen**  
Stable Diffusion 3.5 genera ilustraciones conceptuales de los grupos musculares trabajados, pero con precisión anatómica limitada. Pese a prompts detallados (silueta gris + zonas iluminadas), el modelo tiende a colorear áreas no objetivo. Esta limitación se acepta en el proyecto y se documenta como restricción del modelo.

**4. Throttling de Bedrock**  
Con múltiples llamadas consecutivas al modelo de imagen (una por día del plan), Bedrock puede devolver `ThrottlingException`. Las imágenes de día se generan de forma no bloqueante para no afectar la UX.

**5. Sesgos del modelo**  
Amazon Nova 2 Lite fue entrenado con datos de internet que pueden contener sesgos culturales en las recomendaciones de ejercicio.

**6. Privacidad**  
Los datos del usuario (peso, edad, condición física) se envían a servidores de AWS en `eu-south-2` (España). En un entorno productivo habría que revisar las políticas de privacidad y valorar la anonimización de datos.

**7. Supervisión humana obligatoria**  
La IA no sustituye a un preparador físico ni a un médico. El plan debe revisarse por un profesional, especialmente si el usuario tiene lesiones o condiciones de salud específicas.

---

## 🚀 Estado del proyecto

- [x] Definición del problema y arquitectura
- [x] README y documentación
- [x] Estructura del repositorio y `.gitignore`
- [x] Configuración AWS Bedrock — Nova 2 Lite + Stable Diffusion 3.5
- [x] `prompts.py` — prompts dinámicos modo personal + preparador físico
- [x] Historial de conversación con feedback conversacional
- [x] Interfaz HTML/CSS/JS responsive
- [x] `app.py` Flask — endpoints `/generar-plan`, `/generar-imagen`, `/generar-imagen-dia`
- [x] `Dockerfile` + `docker-compose.yml`
- [x] Integración frontend ↔ Flask ↔ Bedrock
- [x] Modo impresión PDF optimizado (`@media print`)
- [x] Pruebas y ajustes finales
- [ ] Presentación oral

---

## 👥 Equipo

| Miembro | Área | Responsabilidad |
|---------|------|-----------------|
| **Javier** | Frontend + Flask + Docker | HTML/CSS/JS, formulario, renderizado del plan e imágenes, `app.py` Flask, `Dockerfile`, `docker-compose.yml` |
| **Santiago** | IA + AWS Bedrock | Configuración AWS Bedrock, Nova 2 Lite + SD 3.5, `prompts.py`, persistencia del historial conversacional |

---

*Proyecto Final · Especialització IA + Big Data · AWS Bedrock*
