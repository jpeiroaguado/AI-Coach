let modoActual = "personal";
let historial = [];
let equipamientoTags = [];

// ===== SELECTOR DE MODO =====
function seleccionarModo(modo) {
  modoActual = modo;
  document.getElementById("btn-personal").classList.toggle("active", modo === "personal");
  document.getElementById("btn-preparador").classList.toggle("active", modo === "preparador");
  document.getElementById("form-personal").classList.toggle("hidden", modo !== "personal");
  document.getElementById("form-preparador").classList.toggle("hidden", modo !== "preparador");
  ocultarResultado();
}

// ===== TAGS DE EQUIPAMIENTO =====
function addTag() {
  const input = document.getElementById("equipamiento-input");
  const valor = input.value.trim();
  if (!valor || equipamientoTags.includes(valor)) { input.value = ""; return; }
  equipamientoTags.push(valor);
  renderTags();
  input.value = "";
  input.focus();
}

function removeTag(index) {
  equipamientoTags.splice(index, 1);
  renderTags();
}

function renderTags() {
  const container = document.getElementById("equipamiento-tags");
  container.innerHTML = equipamientoTags.map((tag, i) => `
    <span class="tag">${tag} <button type="button" class="tag-remove" onclick="removeTag(${i})">×</button></span>
  `).join("");
}

// Añadir tag con Enter
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("equipamiento-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") { e.preventDefault(); addTag(); }
  });
});

// ===== SUBMIT PERSONAL =====
document.getElementById("form-personal-data").addEventListener("submit", function(e) {
  e.preventDefault();

  const equipamiento = equipamientoTags.length > 0
    ? equipamientoTags.join(", ")
    : document.getElementById("equipamiento-input").value.trim() || "Sin especificar";

  const datos = {
    modo: "personal",
    edad: parseInt(document.getElementById("edad").value),
    peso: parseFloat(document.getElementById("peso").value),
    altura: parseInt(document.getElementById("altura").value),
    objetivo: document.getElementById("objetivo").value,
    nivel: document.getElementById("nivel").value,
    dias: parseInt(document.getElementById("dias").value),
    equipamiento: equipamiento,
    observaciones: document.getElementById("observaciones").value.trim() || null
  };

  historial = [];
  generarPlan(datos);
});

// ===== SUBMIT PREPARADOR =====
document.getElementById("form-preparador-data").addEventListener("submit", function(e) {
  e.preventDefault();

  const datos = {
    modo: "preparador",
    deporte: document.getElementById("deporte").value,
    categoria: document.getElementById("categoria").value,
    objetivo_fisico: document.getElementById("objetivo-fisico").value,
    fase: document.getElementById("fase").value,
    duracion: parseInt(document.getElementById("duracion").value),
    observaciones: document.getElementById("observaciones-prep").value.trim() || null
  };

  historial = [];
  generarPlan(datos);
});

// ===== LLAMADA A FLASK =====
async function generarPlan(datos) {
  mostrarLoading(true);
  ocultarResultado();

  try {
    const response = await fetch("/generar-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...datos, historial })
    });

    const resultado = await response.json();
    console.log("Respuesta backend:", resultado);

    if (!response.ok || !resultado.ok) {
      throw new Error(resultado.error || "Error desconocido del servidor");
    }

    historial.push({ role: "user", content: JSON.stringify(datos) });
    historial.push({ role: "assistant", content: JSON.stringify(resultado.plan) });

    renderPlan(resultado.plan);

  } catch (err) {
    console.error("Error completo:", err);
    alert("Error al generar el plan: " + err.message);
  } finally {
    mostrarLoading(false);
  }
}

// ===== RENDERIZAR PLAN =====
function renderPlan(plan) {
  document.getElementById("plan-nombre").textContent = plan.plan_nombre || "Tu plan de entrenamiento";

  const container = document.getElementById("dias-container");
  container.innerHTML = "";

  if (plan.dias && plan.dias.length > 0) {
    plan.dias.forEach(dia => {
      const card = document.createElement("div");
      card.className = "dia-card";
      const ejerciciosHTML = (dia.ejercicios || []).map(ej => `
        <div class="ejercicio">
          <span class="ejercicio-nombre">${ej.nombre}</span>
          <span class="ejercicio-detalle">${ej.series} x ${ej.repeticiones}<br>⏱ ${ej.descanso}</span>
        </div>
      `).join("");
      card.innerHTML = `
        <h3>${dia.dia}</h3>
        <p class="grupo">${dia.grupo_muscular || dia.capacidad || ""}</p>
        ${ejerciciosHTML}
      `;
      container.appendChild(card);
    });
  }

  const consejosBox = document.getElementById("consejos-box");
  if (plan.consejos && plan.consejos.length > 0) {
    consejosBox.innerHTML = `<h3>💡 Consejos</h3><ul>${plan.consejos.map(c => `<li>${c}</li>`).join("")}</ul>`;
    consejosBox.classList.remove("hidden");
  } else {
    consejosBox.classList.add("hidden");
  }

  document.getElementById("resultado").classList.remove("hidden");
}

// ===== FEEDBACK =====
async function enviarFeedback() {
  const feedback = document.getElementById("feedback-input").value.trim();
  if (!feedback) return;

  historial.push({ role: "user", content: feedback });
  mostrarLoading(true);
  document.getElementById("resultado").classList.add("hidden");

  try {
    const response = await fetch("/generar-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modo: modoActual, historial })
    });
    const resultado = await response.json();
    if (!resultado.ok) throw new Error(resultado.error);
    historial.push({ role: "assistant", content: JSON.stringify(resultado.plan) });
    document.getElementById("feedback-input").value = "";
    renderPlan(resultado.plan);
  } catch (err) {
    alert("Error al ajustar el plan: " + err.message);
  } finally {
    mostrarLoading(false);
  }
}

function mostrarLoading(show) {
  document.getElementById("loading").classList.toggle("hidden", !show);
}
function ocultarResultado() {
  document.getElementById("resultado").classList.add("hidden");
}
function resetear() {
  historial = [];
  equipamientoTags = [];
  renderTags();
  ocultarResultado();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ===== AUTOCOMPLETE CUSTOM =====
function initAutocompletes() {
  document.querySelectorAll("input[data-options]").forEach(input => {
    const options = JSON.parse(input.getAttribute("data-options"));
    const dropId = "ac-" + input.id;
    const drop = document.getElementById(dropId);
    if (!drop) return;

    // Mostrar todas al hacer foco
    input.addEventListener("focus", () => showOptions(input, options, drop));

    // Filtrar mientras escribe
    input.addEventListener("input", () => {
      const q = input.value.toLowerCase();
      const filtered = q ? options.filter(o => o.toLowerCase().includes(q)) : options;
      showOptions(input, filtered, drop);
    });

    // Flecha abajo abre el dropdown
    input.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        const first = drop.querySelector(".ac-item");
        if (first) first.focus();
      }
      if (e.key === "Escape") closeDrop(drop);
    });
  });

  // Cerrar al hacer clic fuera
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".autocomplete-wrap")) {
      document.querySelectorAll(".ac-dropdown").forEach(d => closeDrop(d));
    }
  });
}

function showOptions(input, options, drop) {
  if (!options.length) { closeDrop(drop); return; }

  drop.innerHTML = options.map((o, i) => `
    <div class="ac-item" tabindex="0"
      onmousedown="selectOption(event, '${input.id}', '${o.replace(/'/g, "\'")}')"
      onkeydown="acKeyNav(event, '${input.id}', '${o.replace(/'/g, "\'")}')">
      ${o}
    </div>
  `).join("");

  drop.classList.add("open");
}

function selectOption(e, inputId, value) {
  e.preventDefault();
  const input = document.getElementById(inputId);
  input.value = value;
  const drop = document.getElementById("ac-" + inputId);
  closeDrop(drop);
  input.focus();
  // Si es el input de equipamiento, hacer add automático
  if (inputId === "equipamiento-input") { addTag(); }
}

function acKeyNav(e, inputId, value) {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectOption(e, inputId, value); }
  if (e.key === "ArrowDown") { e.preventDefault(); e.target.nextElementSibling?.focus(); }
  if (e.key === "ArrowUp") {
    e.preventDefault();
    const prev = e.target.previousElementSibling;
    if (prev) prev.focus();
    else document.getElementById(inputId).focus();
  }
  if (e.key === "Escape") closeDrop(document.getElementById("ac-" + inputId));
}

function closeDrop(drop) {
  if (drop) drop.classList.remove("open");
}

// Inicializar al cargar
document.addEventListener("DOMContentLoaded", initAutocompletes);
