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

Genera exactamente {dias} días de entrenamiento. Adapta los ejercicios al equipamiento disponible y al nivel del usuario."""

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

Adapta los ejercicios al deporte, la categoría y la fase de temporada. La sesión debe durar aproximadamente {duracion} minutos."""

    else:
        return "Genera un plan de entrenamiento genérico en formato JSON."
