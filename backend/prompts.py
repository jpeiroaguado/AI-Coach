def construir_prompt(datos):
    modo = datos.get("modo", "personal")

    if modo == "personal":
        edad = datos.get("edad")
        peso = datos.get("peso")
        altura = datos.get("altura")
        objetivo = datos.get("objetivo")
        nivel = datos.get("nivel")
        dias = datos.get("dias")
        equipamiento = datos.get("equipamiento", "Sin especificar")
        observaciones = datos.get("observaciones") or "Ninguna"

        return f"""Eres un entrenador personal experto. Crea un plan de entrenamiento semanal personalizado.

PERFIL DEL USUARIO:
- Edad: {edad} años
- Peso: {peso} kg
- Altura: {altura} cm
- Objetivo: {objetivo}
- Nivel: {nivel}
- Días de entrenamiento por semana: {dias}
- Equipamiento disponible: {equipamiento}
- Observaciones: {observaciones}

INSTRUCCIONES:
Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta, sin texto adicional:

{{
"plan_nombre": "Nombre descriptivo del plan",
"dias": [
{{
"dia": "Día 1",
"grupo_muscular": "Pecho y Tríceps",
"ejercicios": [
{{
"nombre": "Press de banca",
"series": 4,
"repeticiones": "8-10",
"descanso": "90s"
}}
]
}}
],
"consejos": [
"Consejo 1",
"Consejo 2",
"Consejo 3"
]
}}

Genera exactamente {dias} días de entrenamiento.
Adapta los ejercicios al equipamiento disponible y al nivel del usuario.

IMPORTANTE:
- El JSON debe estar completo y correctamente cerrado.
- No escribas explicaciones fuera del JSON.
- No uses markdown.
- Genera máximo 5 ejercicios por día para evitar respuestas demasiado largas."""

    elif modo == "preparador":
        deporte = datos.get("deporte")
        categoria = datos.get("categoria")
        objetivo_fisico = datos.get("objetivo_fisico")
        fase = datos.get("fase")
        duracion = datos.get("duracion")
        observaciones = datos.get("observaciones") or "Ninguna"

        return f"""Eres un preparador físico profesional experto en deportes de alto rendimiento. Diseña una sesión de entrenamiento completa.

DETALLES DE LA SESIÓN:
- Deporte / Disciplina: {deporte}
- Categoría: {categoria}
- Objetivo físico: {objetivo_fisico}
- Fase de temporada: {fase}
- Duración total: {duracion} minutos
- Observaciones: {observaciones}

INSTRUCCIONES:
Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta, sin texto adicional:
{{
"plan_nombre": "Nombre descriptivo de la sesión",
"dias": [
{{
"dia": "Sesión",
"capacidad": "{objetivo_fisico}",
"ejercicios": [
{{
"nombre": "Nombre del ejercicio",
"series": 3,
"repeticiones": "10-12",
"descanso": "60s"
}}
]
}}
],
"consejos": [
"Consejo específico para {deporte}",
"Consejo sobre la fase {fase}",
"Consejo de recuperación"
]
}}

Adapta los ejercicios al deporte, la categoría y la fase de temporada.

IMPORTANTE:
- Usa los nombres técnicos estándar de los ejercicios (Sentadilla, Burpee, Sprint...).
- El objetivo físico "{objetivo_fisico}" define la SELECCIÓN e INTENSIDAD, NO el nombre del ejercicio.
- NUNCA añadas el objetivo físico como adjetivo en el nombre del ejercicio.
- MAL: "Sentadillas con salto explosivo", "Burpees explosivos", "Sprint explosivo"
- BIEN: "Sentadillas con salto", "Burpees", "Sprint 10m"
- Los ejercicios deben ser apropiados para {objetivo_fisico}, pero con nombres técnicos limpios.

La sesión debe durar aproximadamente {duracion} minutos.."""

    else:
        return "Genera un plan de entrenamiento genérico en formato JSON."


def construir_prompt_imagen_portada(datos):
    modo = datos.get("modo", "personal")
    deporte = datos.get("deporte") or "entrenamiento físico"
    objetivo = datos.get("objetivo") or datos.get("objetivo_fisico") or "mejora del rendimiento"
    fase = datos.get("fase") or "temporada general"
    nivel = datos.get("nivel") or datos.get("categoria") or "intermedio"
    dias = datos.get("dias") or datos.get("duracion") or 3
    equipamiento = datos.get("equipamiento") or "material deportivo básico"

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

    return (
        "Wide cinematic illustration, modern sports environment. "
        f"Main theme: {descripcion}. "
        "Show athletes training or preparing in a setting related to the sport "
        f"({deporte}), not necessarily a classic gym: it can be a court, track, pool "
        "or outdoor field depending on the sport. "
        "Dynamic but clean composition, soft gradients, warm lighting, "
        "no text, no logos, no UI elements, semi-realistic but stylized."
    )


def construir_prompt_imagen_dia(datos):
    dia = datos.get("dia", "Día 1")
    ejercicios = datos.get("ejercicios", [])
    grupo = datos.get("grupo_muscular", "")
    objetivo_global = datos.get("objetivo", "")

    ejercicios_limpios = [e for e in ejercicios if e]
    base_musculos = grupo or ", ".join(ejercicios_limpios[:2]) or "full body"
    concepto_objetivo = objetivo_global or "general fitness"

    return (
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
