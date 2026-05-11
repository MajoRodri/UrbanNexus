/**
 * Actualiza los elementos visuales del icono (Sol/Luna/Nubes/Lluvia)
 */
function actualizarIconoVisual(data) {
    const container = document.getElementById("weather-icon-container");
    const sun = document.getElementById("sun-icon");

    if (!container || !sun) return;

    // Limpiar iconos anteriores
    container.querySelectorAll('.cloud, .rain-drops').forEach(el => el.remove());

    // Resetear clases
    sun.className = "sun";

    // Noche o día
    if (data.es_noche) {
        sun.classList.add("is-night");
    }

    // Color por temperatura
    const temp = Math.round(data.temperatura);
    if (temp <= 12) {
        sun.classList.add("temp-cold");
    } else if (temp >= 28) {
        sun.classList.add("temp-hot");
    }

    // Nubes o lluvia
    if (data.lluvia > 0) {
        crearNube(container, true);
    } else if (data.humedad > 75) {
        crearNube(container, false);
    }
}

/**
 * Crea nube y lluvia opcional
 */
function crearNube(parent, conLluvia) {
    const cloud = document.createElement("div");
    cloud.className = "cloud";

    if (conLluvia) {
        const drops = document.createElement("div");
        drops.className = "rain-drops";

        for (let i = 0; i < 3; i++) {
            const d = document.createElement("div");
            d.className = "drop";
            d.style.left = (20 + i * 25) + "px";
            d.style.animationDelay = (i * 0.2) + "s";
            drops.appendChild(d);
        }

        cloud.appendChild(drops);
    }

    parent.appendChild(cloud);
}

/**
 * Función principal
 */
async function actualizarClima() {
    const temperature = document.getElementById("temperature");
    const humidity = document.getElementById("humidity");
    const wind = document.getElementById("wind");
    const rain = document.getElementById("rain");
    const stationName = document.getElementById("stationName");
    const cityName = document.getElementById("cityName");
    const mainTitle = document.getElementById("mainTitle");
    const updatedAt = document.getElementById("updatedAt");
    const statusDot = document.getElementById("statusDot");

    if (!navigator.geolocation) {
        updatedAt.textContent = "GPS no soportado";
        return;
    }

    updatedAt.textContent = "Localizando...";

    navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;

        try {
            const response = await fetch(`/api/clima?lat=${latitude}&lon=${longitude}`);
            const data = await response.json();

            if (!response.ok) throw new Error(data.error || "Error al obtener datos");

            if (data.temperatura === undefined || data.temperatura === null) {
                throw new Error("Datos incompletos de la API");
            }

            // Rellenar datos
            temperature.textContent = `${Math.round(data.temperatura)}°`;
            humidity.textContent = `${data.humedad}%`;
            wind.textContent = `${data.viento} km/h`;
            rain.textContent = `${data.lluvia} mm`;
            stationName.textContent = data.estacion;
            cityName.textContent = data.ciudad;
            mainTitle.textContent = `${data.ciudad} · Tiempo Real`;

            // 🔥 SOLUCIÓN: usar hora local SIEMPRE
            const horaActual = new Date().toLocaleTimeString("es-ES", {
                hour: "2-digit",
                minute: "2-digit"
            });

            updatedAt.textContent = `Hora de última actualización: ${horaActual}`;

            // Barras de progreso
            document.getElementById("humidity-bar").style.width = `${Math.min(data.humedad, 100)}%`;
            document.getElementById("wind-bar").style.width = `${Math.min((data.viento / 120) * 100, 100)}%`;
            document.getElementById("rain-bar").style.width = `${Math.min((data.lluvia / 50) * 100, 100)}%`;

            // Icono
            actualizarIconoVisual(data);

            // Estado OK
            statusDot.style.background = "#22c55e";
            statusDot.style.boxShadow = "0 0 12px rgba(34, 197, 94, 0.45)";

        } catch (error) {
            console.error(error);
            updatedAt.textContent = `Error: ${error.message}`;
            statusDot.style.background = "#ef4444";
            statusDot.style.boxShadow = "0 0 12px rgba(239, 68, 68, 0.45)";
        }

    }, () => {
        updatedAt.textContent = "Permiso de ubicación denegado";
    });
}

// --- CURSOR RADAR ---
(function () {
    const dot  = document.getElementById("cursor-dot");
    const ring = document.getElementById("cursor-ring");
    if (!dot || !ring) return;

    let ringX = 0, ringY = 0;

    document.addEventListener("mousemove", (e) => {
        dot.style.left  = e.clientX + "px";
        dot.style.top   = e.clientY + "px";
        ringX += (e.clientX - ringX) * 0.12;
        ringY += (e.clientY - ringY) * 0.12;
        ring.style.left = ringX + "px";
        ring.style.top  = ringY + "px";
    });

    document.addEventListener("mousedown", () => ring.classList.add("clicking"));
    document.addEventListener("mouseup",   () => ring.classList.remove("clicking"));

    document.addEventListener("click", (e) => {
        const ping = document.createElement("div");
        ping.className = "cursor-ping";
        ping.style.left = e.clientX + "px";
        ping.style.top  = e.clientY + "px";
        document.body.appendChild(ping);
        ping.addEventListener("animationend", () => ping.remove());
    });
})();

// Inicio
document.addEventListener("DOMContentLoaded", () => {
    actualizarClima();

    const refreshBtn = document.getElementById("refreshBtn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", actualizarClima);
    }
});