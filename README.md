🌡️ Temperature Monitor App
Sistema de monitoreo de temperatura en tiempo real construido con Streamlit y Supabase, desplegado en Railway.

🚀 Live Demo
URL de la aplicación: https://temperature-monitor-app.up.railway.app

📋 Características
✅ Monitoreo en tiempo real de temperatura y humedad

📊 Dashboard interactivo con gráficos y métricas

🌡️ Múltiples sensores y ubicaciones

📈 Visualizaciones con Plotly

☁️ Base de datos en la nube con Supabase

🚀 Despliegue automático con Railway

🔐 Configuración segura con variables de entorno

🛠️ Tecnologías
Frontend: Streamlit

Backend: Python

Base de datos: Supabase (PostgreSQL)

Despliegue: Railway

Visualización: Plotly, Pandas

Control de versiones: Git/GitHub

📁 Estructura del Proyecto

temperature-monitor-app/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── src/
│   ├── app.py
│   ├── pages/
│   │   ├── 1_📊_Dashboard_Temperatura.py
│   │   └── 2_📈_Histórico.py
│   └── utils/
│       ├── database.py
│       └── helpers.py
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── railway.toml
├── LICENSE
└── README.md


🚀 Instalación Local
Prerrequisitos
Python 3.9 o superior

Git

GitHub

Cuenta en Supabase

Cuenta en Railway (para despliegue)

1. Clonar el Repositorio
bash

# Clonar el repositorio
git clone https://github.com/tu-usuario/temperature-monitor-app.git

# Navegar al directorio
cd temperature-monitor-app
2. Crear Entorno Virtual
Windows:

bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
Linux/Mac:

bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
Nota: Debería ver (venv) al inicio de tu línea de comandos.

3. Instalar Dependencias
bash
# Instalar las librerías requeridas
pip install -r requirements.txt
4. Configurar Variables de Entorno
bash
# Copiar el archivo de ejemplo
cp .env.example .env
Editar el archivo .env con tu editor favorito:

*env*
SUPABASE_URL=tu_url_de_supabase_aqui
SUPABASE_KEY=tu_clave_anon_public_aqui
STREAMLIT_SERVER_PORT=8501
5. Configurar Supabase
5.1 Crear Proyecto en Supabase
Ve a supabase.com

Crea una cuenta o inicia sesión

Haz clic en "New Project"

Completa la información del proyecto

5.2 Configurar la Base de Datos
Ve al SQL Editor en Supabase y ejecuta este script:

**sql**
*Ejemplo*
-- Tabla para lecturas de temperatura
CREATE TABLE temperature_readings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sensor_id VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity INTEGER CHECK (humidity >= 0 AND humidity <= 100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Índices para mejor performance
CREATE INDEX idx_temperature_timestamp ON temperature_readings(timestamp DESC);
CREATE INDEX idx_temperature_location ON temperature_readings(location);
CREATE INDEX idx_temperature_sensor ON temperature_readings(sensor_id);

-- Habilitar RLS (Row Level Security)
ALTER TABLE temperature_readings ENABLE ROW LEVEL SECURITY;

-- Políticas de seguridad
CREATE POLICY "Allow public read access" ON temperature_readings
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert" ON temperature_readings
    FOR INSERT WITH CHECK (true);

-- Insertar datos de ejemplo
INSERT INTO temperature_readings (sensor_id, location, temperature_c, humidity) VALUES
('sensor_001', 'Sala Principal', 22.5, 45),
('sensor_002', 'Cocina', 24.3, 55),
('sensor_003', 'Dormitorio', 21.8, 50),
('sensor_004', 'Exterior', 18.2, 60),
('sensor_001', 'Sala Principal', 23.1, 44);
*fin del sql*

5.3 Obtener Credenciales de Supabase
Ve a Settings > API en tu proyecto de Supabase

Copia:

URL → SUPABASE_URL

anon public → SUPABASE_KEY

Actualiza tu archivo .env con estas credenciales.

6. Ejecutar la Aplicación Localmente
bash

# Ejecutar Streamlit
streamlit run src/app.py
La aplicación estará disponible en: http://localhost:8501

🚀 Despliegue en Railway
1. Preparar el Repositorio
bash
# Asegúrate de que todos los archivos estén commitados
git add .
git commit -m "feat: initial temperature monitor app"

# Subir a GitHub
git push origin main
2. Configurar Railway
Ve a railway.app

Inicia sesión con GitHub

Crea un New Project > Deploy from GitHub repo

Conecta tu repositorio

3. Configurar Variables en Railway
En tu proyecto de Railway, ve a Variables y agrega:

SUPABASE_URL = tu_url_de_supabase

SUPABASE_KEY = tu_clave_anon_public

4. Configuración Automática
Railway detectará automáticamente que es una app de Streamlit y realizará el despliegue.

5. Despliegue Automático
Cada push a main desplegará automáticamente.

📊 Uso de la Aplicación
Página Principal
Visualización de temperatura actual

Métricas en tiempo real

Formulario para agregar nuevas lecturas

Dashboard
Gráficos interactivos de temperatura y humedad

Filtros por ubicación y período de tiempo

Métricas estadísticas

Tabla de datos detallados

🔧 Desarrollo
Instalar Dependencias de Desarrollo
bash
pip install ruff black pytest
Comandos de Desarrollo
bash
# Ejecutar la aplicación
streamlit run src/app.py

# Verificar código con Ruff
ruff check src/

# Formatear código
ruff format src/

# Ejecutar tests
pytest tests/
Estructura de Código
src/app.py - Aplicación principal

src/pages/ - Páginas adicionales de Streamlit

src/utils/database.py - Cliente de Supabase

src/utils/helpers.py - Funciones auxiliares

🐛 Solución de Problemas
Error: "Streamlit no se reconoce"
bash
# Usar Python -m en lugar del comando directo
python -m streamlit run src/app.py
Error: "No se encontraron secrets"
Verificar que las variables estén en Railway Variables (no en Secrets)

Usar os.getenv() en lugar de st.secrets.get()

Error de conexión a Supabase
Verificar que SUPABASE_URL y SUPABASE_KEY sean correctos

Asegurar que la tabla temperature_readings exista

Verificar políticas RLS en Supabase

📈 Próximas Características
Alertas automáticas por temperatura

Exportación de datos

Autenticación de usuarios

API REST para sensores IoT

Notificaciones en tiempo real

👥 Integrantes
Bryan Aponte - Desarrollo full-stack

Gustavo Batista - Base de datos y DevOps

Carlos Sánchez - Frontend y UX