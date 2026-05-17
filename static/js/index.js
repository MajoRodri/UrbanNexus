/**
 * LÓGICA DE LANZAMIENTO (Showcase 8000 -> Redirección a la raíz intermedia de 5000)
 */
async function triggerLaunch(btnElement) {
    const originalText = btnElement.innerHTML;
    btnElement.disabled = true;
    btnElement.innerHTML = `<span class="w-2 h-2 bg-black rounded-full animate-ping"></span> EXECUTING...`;

    try {
        const response = await fetch('/launch', { method: 'POST' });
        const data = await response.json();

        if (data.status === "success") {
            btnElement.innerHTML = "SYSTEM_ONLINE";
            btnElement.style.background = "#fff";

            setTimeout(() => {
                // Apuntamos a la raíz. El backend se encarga de redirigir a Login o a la App según la sesión
                window.open("http://127.0.0.1:5000/", "_blank");
                
                btnElement.innerHTML = originalText;
                btnElement.disabled = false;
                btnElement.style.background = "";
            }, 1500);
        }
    } catch (error) {
        btnElement.innerHTML = "ERR_KERNEL";
        btnElement.disabled = false;
        setTimeout(() => { btnElement.innerHTML = originalText; }, 3000);
    }
}

/**
 * ACTUALIZACIÓN DE INTERFAZ (Protección contra NaN)
 */
function actualizarUI(data) {
    const temperature = document.getElementById("temperature");
    const heroTemp = document.getElementById("hero-temp");

    const tempValue = (data.temperatura != null) ? Math.round(data.temperatura) : 0;
    const humValue = (data.humedad != null) ? data.humedad : 0;

    if (temperature) temperature.textContent = `${tempValue}°`;
    if (heroTemp) heroTemp.textContent = `${tempValue}°C`;

    const humText = document.getElementById("humidity");
    if (humText) humText.textContent = `${humValue}%`;
    
    const windValue = (data.viento != null) ? data.viento : "--";
    const rainValue = (data.lluvia != null) ? data.lluvia : "--";

    const windText = document.getElementById("wind");
    if (windText) windText.textContent = `${windValue} km/h`;

const rainText = document.getElementById("rain");
if (rainText) rainText.textContent = `${rainValue} mm`;


    const cityText = document.getElementById("cityName");
    if (cityText) cityText.textContent = data.ciudad || "Desconocido";

    const mainTitle = document.getElementById("mainTitle");
    if (mainTitle) mainTitle.textContent = data.ciudad || 'Ubicación';

    const stationName = document.getElementById("stationName");
    if (stationName) stationName.textContent = "";

    const updatedAt = document.getElementById("updatedAt");
    if (updatedAt) {
        const now = new Date();
        updatedAt.textContent = `Actualizado ${now.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" })}`;
    }

    const hBar = document.getElementById("humidity-bar");
    if (hBar) hBar.style.width = `${humValue}%`;
}

/**
 * CONSULTAR POR ZONA 
 */
async function consultarPorZona(zonaNombre) {
    const port = window.location.port;
    const API_BASE = port === "8000" ? "http://127.0.0.1:5000" : "";

    try {
        const response = await fetch(`${API_BASE}/api/clima/municipio?nombre=${encodeURIComponent(zonaNombre)}`);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

        const data = await response.json();
        actualizarUI(data);
    } catch (e) {
        console.error("Error en consulta de zona:", e);
    }
}

/**
 * ACTUALIZACIÓN POR GPS
 */
async function actualizarClimaGPS() {
    const updatedAt = document.getElementById("updatedAt");
    if (updatedAt) updatedAt.textContent = "Buscando distrito...";

    if (!navigator.geolocation) {
        if (updatedAt) updatedAt.textContent = "GPS no soportado";
        return;
    }

    const port = window.location.port;
    const API_BASE = port === "8000" ? "http://127.0.0.1:5000" : "";

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude } = position.coords;
            try {
                const zonaSelect = document.getElementById("zonaSelect");
                if (zonaSelect && zonaSelect.value !== "") return;

                const response = await fetch(`${API_BASE}/api/clima?lat=${latitude}&lon=${longitude}`);
                const data = await response.json();
                actualizarUI(data);
            } catch (e) {
                if (updatedAt) updatedAt.textContent = "Error de conexión con el servidor";
            }
        },
        () => {
            if (updatedAt) updatedAt.textContent = "GPS bloqueado. Selecciona un distrito.";
        },
        { timeout: 8000, enableHighAccuracy: true }
    );
}

/**
 * INICIALIZADOR PRINCIPAL
 */
document.addEventListener("DOMContentLoaded", () => {
    const port = window.location.port;
    const API_BASE = port === "8000" ? "http://127.0.0.1:5000" : "";

    // Botón Launch
    const launchBtn = document.getElementById("btn-launch");
    if (launchBtn) launchBtn.addEventListener("click", () => triggerLaunch(launchBtn));

    // Selector de Zonas
    const zonaSelect = document.getElementById("zonaSelect");
    if (zonaSelect) {
        fetch(`${API_BASE}/api/distritos`)
            .then(r => r.json())
            .then(distritos => {
                zonaSelect.innerHTML = '<option value="" disabled selected>Seleccione zona...</option>';
                distritos.forEach(item => {
                    const opt = document.createElement("option");
                    opt.value = item.municipio;
                    opt.textContent = item.municipio;
                    zonaSelect.appendChild(opt);
                });
            })
            .catch(err => console.error("Error cargando distritos:", err));

        zonaSelect.addEventListener("change", (e) => {
            if (e.target.value === "") {
                actualizarClimaGPS();
            } else {
                consultarPorZona(e.target.value);
            }
        });
    }

    actualizarClimaGPS();
});

/**
 * EFECTO CURSOR
 */
(function() {
    const dot = document.getElementById("cursor-dot");
    if (!dot) return;
    document.addEventListener("mousemove", (e) => {
        dot.style.left = e.clientX + "px";
        dot.style.top = e.clientY + "px";
    });
})();