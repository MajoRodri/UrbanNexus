<div align="center">

# ☁️ Climate Intelligence Platform ☁️

![Logo del Proyecto](static/img/Logo.png)

<br>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-FF5733?style=for-the-badge&logo=databricks&logoColor=white)
![APScheduler](https://img.shields.io/badge/APScheduler-Scheduler-FF6B35?style=for-the-badge&logo=clockify&logoColor=white)
![WeatherAPI](https://img.shields.io/badge/WeatherAPI-F5A623?style=for-the-badge&logo=icloud&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Testing-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

<br>

![Madrid](https://img.shields.io/badge/Madrid-1D3557?style=for-the-badge&logo=googlemaps&logoColor=white)
![Status](https://img.shields.io/badge/Estado-Activo-2DC6B4?style=for-the-badge)
![Version](https://img.shields.io/badge/Versión-1.0.0-1D3557?style=for-the-badge)

<br>

</div>

---

## 📋 Tabla de Contenidos

- [📖 Descripción General](#-descripción-general)
- [🎬 Demo](#-demo)
- [🛠️ Instalación y Configuración](#️-instalación-y-configuración)
- [✨ Características Principales](#-características-principales)
- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema-capas)
- [📐 Reglas de Negocio](#-reglas-de-negocio-golden-rules)
- [📡 Rutas Principales](#-rutas-principales-api--web)
- [🔧 Solución de Problemas](#-solución-de-problemas)
- [👩‍💻 Autores](#-autores)

---

## 📖 Descripción General

**UrbanNexus** es una plataforma integral de monitorización climática diseñada para la Comunidad de Madrid. El sistema se lanza con `python run.py`, lo que arranca simultáneamente el servidor web **Flask** (puerto 5000) y la **API REST con FastAPI** (puerto 8000), activando la configuración de logs, la base de datos SQLite y el sistema de autenticación por roles.

La plataforma centraliza la captura, validación, análisis y visualización de datos meteorológicos mediante una arquitectura de capas limpia: **Controllers → Services → Repositories → Models**, con un pipeline ETL independiente y persistencia robusta.

---

## 🎬 Demos

<details>
<summary>🔧 &nbsp;<strong>Admin</strong></summary>
<br>

| Paso | 🔄 Acción |
|:---:|:---|
| 1️⃣ | 🔐 **Autenticación**: Inicia sesión con email y contraseña. |
| 2️⃣ | 👥 **Gestión de Usuarios**: Crea, edita y desactiva cuentas. Envía invitaciones por email con códigos de un solo uso. |
| 3️⃣ | ⏱️ **Scheduler**: Configura y activa la captura automática de datos. |
| 4️⃣ | 🔍 **Consulta**: Busca el histórico por zona y fecha. Visualiza parámetros y alertas activadas. |
| 5️⃣ | 👀 **CRUD**: Disponible CRUD visual a la hora de revisar registros. |
| 6️⃣ | 📊 **Estadísticas**: Visualización y descarga de media por registro de distrito en: Temperatura, Viento y Humedad. |

> Gestión de cambio de contraseña en el apartado "Mi perfil"


</details>

<details>
<summary>🛠️ &nbsp;<strong>Técnico</strong></summary>
<br>

| Paso | 🔄 Acción |
|:---:|:---|
| 1️⃣ | 🔐 **Autenticación**: Inicia sesión con email y contraseña. Recibe un email con credenciales necesarias para registrarse en el sistema. |
| 2️⃣ | 📥 **Carga de Datos**: Activa el scheduler automático, registra mediciones manualmente o ejecuta el pipeline ETL. |
| 3️⃣ | 🔍 **Consulta y Edición**: Busca el histórico por zona y fecha. Visualiza y edita registros existentes. |
| 4️⃣ | 📊 **Estadísticas**: Visualizacióny descarga de media por registro de distrito en: Temperatura, Viento y Humedad. |
| 5️⃣ | ⏱️ **Scheduler**: Configura y activa la captura automática de datos. |

> Gestión de cambio de contraseña en el apartado "Mi perfil"



</details>

<details>
<summary>👁️ &nbsp;<strong>Visualizador</strong></summary>
<br>

| Paso | 🔄 Acción |
|:---:|:---|
| 1️⃣ | 🔐 **Autenticación**: Inicia sesión con email y contraseña. Recibe un email con credenciales necesarias para registrarse en el sistema.
| 2️⃣ | 🔍 **Consulta**: Busca el histórico climático por zona y fecha. Visualiza parámetros meteorológicos. |
| 3️⃣ | 📊 **Estadísticas**: Visualización de media por registro de distrito en: Temperatura, Viento y Humedad. |

> Gestión de cambio de contraseña en el apartado "Mi perfil"


</details>

---

## 🛠️ Instalación y Configuración

<div align="center">

| | Paso | Descripción |
|:---:|:---:|:---|
| 📋 | **Requisitos** | Python 3.11+ instalado en tu sistema |
| 1️⃣ | **Clonar** | Descarga el repositorio en tu máquina |
| 2️⃣ | **Entorno virtual** | Aísla las dependencias del proyecto |
| 3️⃣ | **Dependencias** | Instala las librerías con pip |
| 4️⃣ | **Variables de entorno** | Configura tus API keys y secretos |
| 5️⃣ | **Ejecutar** | Lanza los servidores Flask + FastAPI |
| 6️⃣ | **Tests** | Verifica que todo funciona correctamente |

</div>

<br>

<details>
<summary>📋 &nbsp;<strong>Requisitos Previos</strong></summary>
<br>

Antes de comenzar, asegúrate de tener instalado lo siguiente:

| Herramienta | Versión mínima | Descarga |
|:---:|:---:|:---:|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |

</details>

<details>
<summary>1️⃣ &nbsp;<strong>Clonar el Repositorio</strong></summary>
<br>

Abre una terminal y ejecuta:

```bash
git clone https://github.com/MajoRodri/UrbanNexus.git
```

Luego entra en la carpeta del proyecto:

```bash
cd UrbanNexus
```

</details>

<details>
<summary>2️⃣ &nbsp;<strong>Crear un Entorno Virtual</strong></summary>
<br>

```bash
# Crear el entorno virtual
python -m venv venv
```

Activa el entorno según tu sistema operativo:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

> Sabrás que está activo cuando veas `(venv)` al inicio de tu terminal.

</details>

<details>
<summary>3️⃣ &nbsp;<strong>Instalar las Dependencias</strong></summary>
<br>

Con el entorno virtual activo:

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary>4️⃣ &nbsp;<strong>Configurar las Variables de Entorno</strong></summary>
<br>

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
WEATHERAPI_KEY=tu_api_key_aquí
GMAIL_USER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=tu_app_password_aquí
```

> Cómo obtener cada clave: [WeatherAPI](#weatherapi-key) · [Gmail App Password](#gmail-smtp)

> **Importante:** el archivo `.env` nunca debe subirse a Git (ya está en `.gitignore`).

</details>

<details>
<summary>5️⃣ &nbsp;<strong>Ejecutar la Aplicación</strong></summary>
<br>

Lanza ambos servidores simultáneamente con:

```bash
python run.py
```

O individualmente:

```bash
# Solo el servidor web Flask (puerto 5000)
python app.py

# Solo la API REST FastAPI (puerto 8000)
python main_api.py
```

| Servidor | URL | Descripción |
|:---:|:---:|:---|
| **Flask** | `http://localhost:5000` | Interfaz web con dashboards y formularios |
| **FastAPI** | `http://localhost:8000` | API REST — docs en `/docs` |

</details>

<details>
<summary>6️⃣ &nbsp;<strong>Ejecutar los Tests</strong></summary>
<br>

El proyecto incluye una suite de **10 archivos de test** con Pytest. Con el entorno activo, ejecútalos desde la raíz:

**Ejecutar todos los tests a la vez:**

```bash
pytest tests/ -v
```

**Ejecutar módulos de forma individual:**

```bash
# Validadores de datos climáticos
pytest tests/test_validators.py -v

# Disparadores del sistema de alertas
pytest tests/test_alert_triggers.py -v

# Rutas de la API FastAPI
pytest tests/test_api_routes.py -v

# Pipeline ETL completo
pytest tests/test_etl_pipeline.py -v

# Repositorios SQLite y JSON
pytest tests/test_sqlite_repository.py -v
pytest tests/test_json_repository.py -v
```

**¿Qué cubre cada archivo de test?**

| Archivo | Módulo que verifica |
|:---|:---|
| `test_validators.py` | Validación de rangos: temperatura, humedad, viento y lluvia. |
| `test_alert_triggers.py` | Evaluación de umbrales RED / ORANGE / GREEN. |
| `test_api_routes.py` | Endpoints FastAPI: zonas, registros, login e invitaciones. |
| `test_api_service.py` | Conexión a WeatherAPI, manejo de errores y reintentos. |
| `test_etl_pipeline.py` | Ciclo Extract → Transform → Load y estadísticas de ejecución. |
| `test_json_repository.py` | Lectura/escritura de archivos JSON en `/data`. |
| `test_sqlite_repository.py` | Operaciones CRUD sobre `clima.db`. |
| `test_normalizer.py` | Estandarización de respuestas externas al modelo interno. |
| `test_services.py` | Lógica de negocio en la capa de servicios. |
| `test_transform.py` | Transformación y limpieza de datos en el ETL. |

> Si todos los tests pasan verás una línea final con `X passed` en verde.

</details>

---

## ✨ Características Principales

<details>
<summary>🔐 <strong>Seguridad y Autenticación</strong></summary>
<br>

Sistema completo de gestión de usuarios con control de acceso por roles.

**Admin** — Acceso total al sistema:

| Sección | Acceso |
|:---|:---|
| Dashboard | Estadísticas generales ✅ |
| Consulta | Ver, editar y eliminar registros históricos ✅ |
| Registro | Ingresar datos manualmente ✅ |
| Scheduler | Activar/desactivar y configurar la ingesta automática ✅ |
| Usuarios | Ver, cambiar rol, activar/desactivar y eliminar usuarios ✅ |
| Invitaciones | Crear y enviar invitaciones por email ✅ |
| Perfil | Ver y editar perfil propio ✅ |

**Técnico** — Acceso operacional (sin gestión de usuarios):

| Sección | Acceso |
|:---|:---|
| Dashboard | Estadísticas generales ✅ |
| Consulta | Ver, editar y eliminar registros históricos ✅ |
| Registro | Ingresar datos manualmente ✅ |
| Scheduler | Activar/desactivar y configurar la ingesta automática ✅ |
| Usuarios | ❌ Sin acceso |
| Invitaciones | ❌ Sin acceso |
| Perfil | Ver y editar perfil propio ✅ |

**Visualizador** — Solo lectura:

| Sección | Acceso |
|:---|:---|
| Dashboard | Estadísticas generales ✅ |
| Consulta | Ver registros históricos (sin editar ni eliminar) ✅ |
| Registro | ❌ Sin acceso |
| Scheduler | ❌ Sin acceso |
| Usuarios | ❌ Sin acceso |
| Invitaciones | ❌ Sin acceso |
| Perfil | Ver y editar perfil propio ✅ |

- Autenticación por JWT (python-jose) con expiración configurable.
- Contraseñas cifradas con bcrypt sin almacenamiento en texto plano.
- Sistema de **invitaciones por email** con códigos de acceso de un solo uso.
- Generación automática de ID de empleado único.

</details>

<details>
<summary>⏱️ <strong>Ingesta de Datos Multimodal</strong></summary>
<br>

| Modo | 📋 Descripción |
| :---: | :--- |
| 🤖 **Automática** | Un programador (`APScheduler`) captura datos en tiempo real en horarios configurables desde el panel de administración. |
| 🖱️ **Manual** | Formulario web para registrar mediciones propias por zona y fecha con validación científica estricta. |

</details>

<details>
<summary>🔄 <strong>Pipeline ETL</strong></summary>
<br>

El módulo `/etl` expone las funciones de transformación y carga que son utilizadas por dos flujos distintos:

**Flujo automático (Scheduler):** es el flujo principal. El scheduler llama directamente a WeatherAPI, normaliza la respuesta y persiste en SQLite usando `transform.py` y `load.py` — sin pasar por ningún archivo intermedio.

```
WeatherAPI → normalizar_datos_clima() → transform() → load_measurements() → SQLite
```

**Flujo manual (`pipeline.py`):** pensado para ejecución puntual. Lee registros desde `registros_climaticos.json` si este archivo ha sido poblado manualmente, y los migra a SQLite.

```
registros_climaticos.json → extract() → transform() → load_measurements() → SQLite
```

| Archivo | Responsabilidad |
|:---|:---|
| `extract.py` | Lee registros desde `registros_climaticos.json` y el catálogo de `municipios.json`. |
| `transform.py` | Normaliza tipos, parsea fechas, elimina duplicados y filtra zonas inválidas. |
| `load.py` | Inserta en SQLite, sincroniza el catálogo de zonas y registra la ejecución. |
| `pipeline.py` | Orquesta las tres etapas del flujo manual, gestiona errores y devuelve estadísticas. |

**Métricas registradas por ejecución:** filas leídas, insertadas, modificadas, descartadas, duplicados eliminados y estado final (OK / ERROR).

</details>

<details>
<summary>📊 <strong>Analítica y Consulta Histórica</strong></summary>
<br>

- Filtrado del histórico por zona y fecha desde `/consulta`.
- Presentación en tabla dinámica con parámetros meteorológicos y alertas activadas.
- Comparación de mediciones manuales frente a datos oficiales.
- Documentación interactiva de la API REST en `http://localhost:8000/docs`.

</details>

<details>
<summary>⚠️ <strong>Sistema de Alertas</strong></summary>
<br>

Monitoreo automático de umbrales en cada registro persistido:

| Alerta | Condición |
| :--- | :--- |
| **🔴 ROJA — Calor extremo** | Temperatura ≥ 40 °C |
| **🟠 NARANJA — Calor intenso** | Temperatura ≥ 35 °C |
| **🔴 ROJA — Frío extremo** | Temperatura ≤ −5 °C |
| **🟠 NARANJA — Helada** | Temperatura ≤ 0 °C |
| **🔴 ROJA — Viento extremo** | Viento > 70 km/h |
| **🟠 NARANJA — Viento fuerte** | Viento > 40 km/h |
| **🔴 ROJA — Lluvia torrencial** | Lluvia > 30 mm |
| **🟠 NARANJA — Lluvia intensa** | Lluvia > 10 mm |
| **🟠 NARANJA — Humedad alta** | Humedad ≥ 90 % |
| **🟢 VERDE** | Sin alertas activas |

</details>

<details>
<summary>💾 <strong>Persistencia Robusta</strong></summary>
<br>

Doble capa de persistencia para máxima resiliencia:

| Almacén | Tecnología | Uso |
|:---:|:---:|:---|
| **Relacional** | SQLite (`clima.db`) + SQLAlchemy 2.0 | Fuente de verdad principal: mediciones, usuarios, zonas, logs ETL, invitaciones. |
| **Plano** | JSON (`/data`) | Portabilidad e interoperabilidad con el pipeline ETL. |

Restricciones de integridad: clave única compuesta `(zona_id, fecha)` para evitar duplicados.

</details>

---

## 🏗️ Arquitectura del Sistema (Capas)

| 🏷️ Módulo | ⚙️ Responsabilidad |
| :---: | :--- |
| 🚪 **`run.py`** | Punto de entrada dual: lanza Flask (5000) y FastAPI (8000) en paralelo. |
| 🖥️ **`app.py`** | Servidor Flask: rutas web, renderizado Jinja2, scheduler y sesiones. |
| ⚡ **`main_api.py`** | Servidor FastAPI: endpoints REST, CORS, validación Pydantic y JWT. |
| 🎮 **`controllers/`** | Reciben las peticiones HTTP, coordinan servicios y devuelven respuestas. |
| ⚙️ **`services/`** | Lógica de negocio: WeatherAPI, alertas, normalización, email, reintentos. |
| 🗄️ **`repositories/`** | Abstracción de datos: `SQLiteRepository` y `JSONRepository`. |
| 📦 **`models/` + `schemas/`** | Entidades de datos (Python classes) y validación de entrada/salida (Pydantic). |
| 🔄 **`etl/`** | Pipeline Extract → Transform → Load con logging de estadísticas. |
| 🛠️ **`utils/`** | Validadores, seguridad, JWT y generación de IDs de empleado. |
| 🎨 **`templates/` + `static/`** | Vistas HTML con Jinja2, estilos CSS y JavaScript para geolocalización. |

---

## 📐 Reglas de Negocio "Golden Rules"

<details>
<summary>📜 <strong>Ver las Golden Rules</strong> — Para garantizar la integridad y calidad del dato (Data Integrity)</summary>
<br>

| # | 📏 Regla | 📋 Descripción |
|:---:|:---|:---|
| 1️⃣ | **Validación Científica** | Todos los datos pasan por `validators.py` antes de persistir: temperatura entre -50 °C y 60 °C, humedad 0–100 %, viento y lluvia ≥ 0. |
| 2️⃣ | **Control de Acceso por Rol** | Cada operación valida el rol del usuario autenticado (admin / tecnico / consultor) antes de ejecutarse. |
| 3️⃣ | **Escritura en Lote** | El pipeline ETL realiza una sola operación de escritura por ciclo de ejecución, registrando métricas en `ETL_logs`. |
| 4️⃣ | **Resiliencia de Red** | El `RetryService` gestiona automáticamente los reintentos ante errores HTTP (429, 500, timeout) al consumir WeatherAPI. |

</details>

---

## 📡 Rutas Principales (API & Web)

### 🖥️ Flask — Interfaz Web (`http://localhost:5000`)

| Método | Ruta | Rol mínimo | Descripción |
| :--- | :--- | :---: | :--- |
| `GET` | `/` | cualquiera | Dashboard principal con resumen climatológico. |
| `GET` | `/dashboard` | cualquiera | Dashboard analítico con gráficos de tendencias. |
| `GET` | `/login` | — | Formulario de acceso. |
| `POST` | `/login` | — | Autenticación y creación de sesión. |
| `GET` | `/logout` | cualquiera | Cierre de sesión. |
| `GET` | `/registro_usuario` | — | Formulario de registro con código de invitación. |
| `POST` | `/registro_usuario` | — | Envío del formulario de registro. |
| `GET` | `/perfil` | cualquiera | Perfil del usuario autenticado. |
| `POST` | `/cambiar_password` | cualquiera | Cambio de contraseña desde el perfil. |
| `GET/POST` | `/consulta` | cualquiera | Visualización y filtrado del histórico de registros. |
| `GET` | `/registro` | admin / tecnico | Formulario de entrada manual de mediciones. |
| `POST` | `/registro/<id>/actualizar` | admin / tecnico | Actualizar una medición existente. |
| `POST` | `/registro/<id>/eliminar` | admin / tecnico | Eliminar una medición. |
| `GET` | `/admin/scheduler` | admin / tecnico | Panel de control del scheduler automático. |
| `POST` | `/admin/scheduler/toggle` | admin / tecnico | Activar o desactivar la ingesta automática. |
| `POST` | `/admin/scheduler/config` | admin / tecnico | Configurar los horarios del scheduler. |
| `GET` | `/admin/scheduler/status` | admin / tecnico | Estado actual del scheduler (JSON). |
| `GET` | `/admin/invitaciones` | admin | Panel de gestión de invitaciones. |
| `POST` | `/crear_invitacion` | admin | Crear y enviar una invitación por email. |
| `GET` | `/admin/usuarios` | admin | Lista y gestión de usuarios del sistema. |
| `POST` | `/admin/usuarios/<id>/rol` | admin | Cambiar el rol de un usuario. |
| `POST` | `/admin/usuarios/<id>/estado` | admin | Activar o desactivar un usuario. |
| `POST` | `/admin/usuarios/<id>/delete` | admin | Eliminar un usuario del sistema. |

### ⚡ FastAPI — API REST (`http://localhost:8000`)

| Método | Ruta | Rol mínimo | Descripción |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/v1/auth/register` | — | Registro de usuario con código de invitación. |
| `POST` | `/api/v1/auth/login` | — | Autenticación y emisión de JWT. |
| `PUT` | `/api/v1/auth/change-password` | cualquiera | Cambio de contraseña. |
| `GET` | `/api/v1/zones/` | cualquiera | Listar todas las zonas geográficas. |
| `GET` | `/api/v1/zones/{id}` | cualquiera | Detalle de una zona por ID. |
| `POST` | `/api/v1/zones/` | admin | Crear una nueva zona. |
| `PUT` | `/api/v1/zones/{id}` | admin / tecnico | Actualizar datos de una zona. |
| `DELETE` | `/api/v1/zones/{id}` | admin | Eliminar una zona. |
| `GET` | `/api/v1/records/` | cualquiera | Listar registros de mediciones. |
| `GET` | `/api/v1/records/{id}` | cualquiera | Detalle de un registro por ID. |
| `GET` | `/api/v1/records/zone/{id}` | cualquiera | Registros filtrados por zona. |
| `POST` | `/api/v1/records/` | admin / tecnico | Crear un nuevo registro de medición. |
| `PUT` | `/api/v1/records/{id}` | admin / tecnico | Actualizar un registro existente. |
| `DELETE` | `/api/v1/records/{id}` | admin / tecnico | Eliminar un registro. |
| `GET` | `/api/v1/users/` | admin | Listar todos los usuarios. |
| `PUT` | `/api/v1/users/{id}/role` | admin | Cambiar el rol de un usuario. |
| `PUT` | `/api/v1/users/{id}/state` | admin | Activar o desactivar un usuario. |
| `DELETE` | `/api/v1/users/{id}` | admin | Eliminar un usuario. |
| `POST` | `/api/v1/invitations/create` | admin | Crear y enviar una invitación por email. |

---

## 🔧 Solución de Problemas

<details>
<summary>👤 &nbsp;<strong>Credenciales de acceso por defecto (Admin)</strong></summary>
<br>

Al arrancar la aplicación por primera vez, el sistema crea automáticamente un usuario administrador con las siguientes credenciales:

| Campo | Valor |
|:---:|:---:|
| **ID de empleado** | `E0000P` |
| **Contraseña** | `Admin1234` |

> Utiliza estas credenciales para el primer acceso. Se recomienda cambiar la contraseña desde el panel de administración una vez dentro.

</details>

<a id="weatherapi-key"></a>
<details>
<summary>🔑 &nbsp;<strong>Cómo obtener tu API Key de WeatherAPI</strong></summary>
<br>

| Paso | Acción |
|:---:|:---|
| 1️⃣ | Regístrate en [weatherapi.com](https://www.weatherapi.com/) con tu email. |
| 2️⃣ | Confirma tu cuenta desde el correo de verificación. |
| 3️⃣ | Accede al **Dashboard** → copia el valor de **API Key**. |
| 4️⃣ | Pégala en tu archivo `.env`: `WEATHERAPI_KEY=tu_clave_aquí` |

> La clave gratuita incluye 1 millón de llamadas/mes.

</details>

<a id="gmail-smtp"></a>
<details>
<summary>📧 &nbsp;<strong>Configurar Gmail SMTP para envío de correos</strong></summary>
<br>

UrbanNexus envía correos de invitación usando tu cuenta de Gmail. Solo necesitas hacer esto una vez:

| Paso | Acción |
|:---:|:---|
| 1️⃣ | Inicia sesión en [myaccount.google.com](https://myaccount.google.com) con la cuenta Gmail que usarás. |
| 2️⃣ | Ve a **Seguridad** → activa la **Verificación en 2 pasos** si no la tienes. |
| 3️⃣ | En la misma sección busca **Contraseñas de aplicaciones** y crea una nueva (nombre: `UrbanNexus`). |
| 4️⃣ | Google te generará una clave de 16 caracteres. Cópiala. |
| 5️⃣ | Añádela a tu `.env`: |

```env
GMAIL_USER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

> La App Password no es tu contraseña de Gmail — es una clave separada y revocable en cualquier momento.

> Límite gratuito: ~500 correos/día, más que suficiente para uso académico o de equipo.


</details>

<details>
<summary>🖥️ &nbsp;<strong>Variables de entorno no cargadas en la terminal de VS Code</strong></summary>
<br>

Si los valores de tu `.env` no se inyectan al abrir la terminal integrada de VS Code, activa la opción correspondiente:

| Paso | Acción |
|:---:|:---|
| 1️⃣ | Abre la configuración con `Ctrl + ,` (Windows/Linux) o `Cmd + ,` (Mac). |
| 2️⃣ | Busca **`python.terminal.useEnvFile`** en la barra de búsqueda. |
| 3️⃣ | Marca la casilla ✅ **Python › Terminal: Use Env File**. |
| 4️⃣ | Cierra y vuelve a abrir la terminal integrada para aplicar los cambios. |

Verifica que las variables se cargaron correctamente:

```bash
# Windows (PowerShell)
echo $env:WEATHERAPI_KEY

# macOS / Linux
echo $WEATHERAPI_KEY
```

> Asegúrate de que el archivo `.env` esté en la raíz del proyecto y sin espacios en los nombres de variable.

</details>

---

## 👩‍💻 Autores

| Miembro | Rol | Contacto |
| :--- | :--- | :--- |
| **Mariajose Alvarez** | Scrum Master | [@MajoRodri](https://github.com/MajoRodri) |
| **Isabela Tellez** | Product Manager | [@Isabela-Tellez](https://github.com/Isabela-Tellez) |
| **Joel Ibarra** | Desarrollador | [@jowel2701](https://github.com/jowel2701) |
| **Vanessa Garcia** | Desarrolladora | [@garciaguadalupevanessa-bit](https://github.com/garciaguadalupevanessa-bit) |
| **Yohanna S.Perez** | Desarrolladora | [@yohperez](https://github.com/yohperez) |

---

<div align="center">

Desarrollado con pasión por el equipo de **UrbanNexus**. ☁️🌡️

<br>

![Made with love](https://img.shields.io/badge/Hecho_con-Passion_y_Datos-E63946?style=for-the-badge)
![Team](https://img.shields.io/badge/Team-UrbanNexus-1D3557?style=for-the-badge&logo=github&logoColor=white)

</div>
