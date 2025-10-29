"""
Sistema de Monitoreo de Temperatura en Tiempo Real
Módulo: Lectura y visualización de datos térmicos
"""
import streamlit as st
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.database import SupabaseClient
from utils.helpers import validate_temperature, celsius_to_fahrenheit, format_timestamp

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Monitoreo de Temperatura",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno
load_dotenv()

class TemperatureMonitorApp:
    """Clase principal de la aplicación de monitoreo de temperatura"""
    
    def __init__(self):
        """Inicializar la aplicación y conexión a Supabase"""
        self.supabase = self._init_supabase()
        self.sensor_locations = ["Sala Principal", "Cocina", "Dormitorio", "Exterior", "Laboratorio"]
    
    def _init_supabase(self):
        """Inicializar cliente de Supabase"""
        try:
            supabase_url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
            supabase_key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
            
            if not supabase_url or not supabase_key:
                st.error("❌ Configura las variables de entorno SUPABASE_URL y SUPABASE_KEY")
                st.stop()
            
            return SupabaseClient(supabase_url, supabase_key)
        except Exception as e:
            st.error(f"Error conectando a Supabase: {e}")
            st.stop()
    
    def sidebar_controls(self):
        """Controles de la barra lateral para configuración"""
        st.sidebar.title("🌡️ Controles de Sensor")
        
        with st.sidebar.form("temperature_form"):
            st.subheader("Registrar Nueva Lectura")
            
            location = st.selectbox("📍 Ubicación del Sensor", self.sensor_locations)
            temperature = st.number_input(
                "🌡️ Temperatura (°C)", 
                min_value=-50.0, 
                max_value=100.0, 
                value=25.0,
                step=0.1
            )
            humidity = st.slider("💧 Humedad Relativa (%)", 0, 100, 50)
            sensor_id = st.text_input("🔧 ID del Sensor", value="sensor_001")
            
            submitted = st.form_submit_button("📊 Registrar Lectura")
            
            if submitted:
                if validate_temperature(temperature):
                    new_reading = {
                        "sensor_id": sensor_id,
                        "location": location,
                        "temperature_c": temperature,
                        "humidity": humidity,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    result = self.supabase.insert_temperature_reading(new_reading)
                    if result:
                        st.sidebar.success("✅ Lectura registrada exitosamente!")
                    else:
                        st.sidebar.error("❌ Error al registrar lectura")
                else:
                    st.sidebar.error("⚠️ Temperatura fuera de rango válido")
        
        # Conversor de temperatura
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔄 Conversor de Temperatura")
        temp_c = st.sidebar.number_input("Temperatura en °C", value=25.0)
        temp_f = celsius_to_fahrenheit(temp_c)
        st.sidebar.metric("Temperatura en °F", f"{temp_f:.1f}")
    
    def main_dashboard(self):
        """Dashboard principal de monitoreo"""
        st.title("🌡️ Sistema de Monitoreo de Temperatura")
        st.markdown("---")
        
        # Obtener lecturas recientes
        recent_readings = self.supabase.get_recent_temperature_readings(limit=10)
        
        # Métricas en tiempo real
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if recent_readings:
                current_temp = recent_readings[0]['temperature_c']
                st.metric(
                    "🌡️ Temperatura Actual", 
                    f"{current_temp:.1f}°C",
                    delta=f"{celsius_to_fahrenheit(current_temp):.1f}°F"
                )
        
        with col2:
            if recent_readings:
                current_humidity = recent_readings[0]['humidity']
                st.metric("💧 Humedad Actual", f"{current_humidity}%")
        
        with col3:
            total_readings = len(recent_readings)
            st.metric("📊 Total de Lecturas", total_readings)
        
        with col4:
            if recent_readings:
                avg_temp = sum(r['temperature_c'] for r in recent_readings) / len(recent_readings)
                st.metric("📈 Promedio", f"{avg_temp:.1f}°C")
        
        st.markdown("---")
        
        # Mostrar lecturas recientes
        st.subheader("📋 Lecturas Recientes")
        
        if recent_readings:
            for reading in recent_readings:
                self._display_reading_card(reading)
        else:
            st.info("📝 No hay lecturas registradas. Usa el formulario de la barra lateral para agregar datos.")
    
    def _display_reading_card(self, reading):
        """Mostrar tarjeta individual de lectura"""
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                # Indicador de temperatura con color
                temp = reading['temperature_c']
                if temp < 10:
                    temp_icon = "❄️"
                    color = "#87CEEB"
                elif temp > 30:
                    temp_icon = "🔥"
                    color = "#FF6B6B"
                else:
                    temp_icon = "🌡️"
                    color = "#4ECDC4"
                
                st.markdown(
                    f"<h3 style='color: {color};'>{temp_icon} {reading['location']}</h3>",
                    unsafe_allow_html=True
                )
                st.caption(f"Sensor: {reading['sensor_id']}")
            
            with col2:
                st.metric("Temperatura", f"{temp:.1f}°C")
            
            with col3:
                st.metric("Humedad", f"{reading['humidity']}%")
            
            with col4:
                st.caption(f"🕒 {format_timestamp(reading['timestamp'])}")
            
            st.markdown("---")
    
    def alert_system(self):
        """Sistema de alertas de temperatura"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("🚨 Sistema de Alertas")
        
        # Configuración de umbrales
        min_temp = st.sidebar.number_input("Temperatura Mínima (°C)", value=10.0)
        max_temp = st.sidebar.number_input("Temperatura Máxima (°C)", value=35.0)
        
        # Verificar alertas
        recent_readings = self.supabase.get_recent_temperature_readings(limit=5)
        if recent_readings:
            current_temp = recent_readings[0]['temperature_c']
            
            if current_temp < min_temp:
                st.sidebar.error(f"🚨 ALERTA: Temperatura baja ({current_temp}°C)")
            elif current_temp > max_temp:
                st.sidebar.error(f"🚨 ALERTA: Temperatura alta ({current_temp}°C)")
            else:
                st.sidebar.success("✅ Temperatura dentro de rangos normales")

def main():
    """Función principal de la aplicación"""
    app = TemperatureMonitorApp()
    
    # Barra lateral con controles
    app.sidebar_controls()
    
    # Sistema de alertas
    app.alert_system()
    
    # Dashboard principal
    app.main_dashboard()

if __name__ == "__main__":
    main()