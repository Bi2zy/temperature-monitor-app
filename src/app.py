"""
Sistema de Monitoreo de Temperatura - Versión Corregida para Railway
"""
import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Monitoreo de Temperatura",
    page_icon="🌡️",
    layout="wide"
)

def get_supabase_config():
    """
    Obtener configuración de Supabase - Versión Railway
    """
    # EN RAILWAY: Las variables de entorno están en os.environ, NO en st.secrets
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    return supabase_url, supabase_key

def main():
    st.title("🌡️ Sistema de Monitoreo de Temperatura")
    st.markdown("---")
    
    # Verificar configuración
    supabase_url, supabase_key = get_supabase_config()
    
    # Debug: Mostrar qué está pasando
    st.sidebar.subheader("🔍 Debug Info")
    st.sidebar.write(f"SUPABASE_URL: {'✅ Configurada' if supabase_url else '❌ No configurada'}")
    st.sidebar.write(f"SUPABASE_KEY: {'✅ Configurada' if supabase_key else '❌ No configurada'}")
    
    if not supabase_url or not supabase_key:
        st.error("""
        🔧 **Configuración Requerida en Railway**
        
        Las variables de entorno NO se están detectando. Verifica:
        
        1. **En Railway → Variables** asegúrate de tener:
           - `SUPABASE_URL = https://vhycvnxspssqbwriyewb.supabase.co`
           - `SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
        
        2. **Reinicia el deploy** después de agregar las variables
        
        3. **Verifica que no haya espacios** extras en los valores
        """)
        
        # Mostrar valores actuales (sin revelar la key completa)
        if supabase_url:
            st.info(f"URL detectada: {supabase_url[:20]}...")
        if supabase_key:
            st.info(f"KEY detectada: {supabase_key[:20]}...")
        
        show_demo_interface()
        return
    
    # Si tenemos credenciales, intentar conectar
    try:
        from utils.database import SupabaseClient
        supabase = SupabaseClient(supabase_url, supabase_key)
        st.success("✅ Conectado a Supabase correctamente!")
        
        # Aquí iría la lógica normal con Supabase
        show_real_data_interface(supabase)
        
    except Exception as e:
        st.error(f"❌ Error conectando con Supabase: {str(e)}")
        st.info("Mostrando datos de ejemplo mientras se soluciona la conexión...")
        show_demo_interface()

def show_real_data_interface(supabase):
    """Interfaz cuando hay conexión real a Supabase"""
    st.success("🎉 **CONEXIÓN EXITOSA CON SUPABASE**")
    
    # Obtener datos reales
    try:
        readings = supabase.get_temperature_readings_by_days(7)
        
        if readings:
            df = pd.DataFrame(readings)
            st.metric("📊 Datos Reales", f"{len(df)} lecturas")
            
            # Mostrar algunos datos
            st.subheader("📋 Últimas Lecturas Reales")
            st.dataframe(df.head()[['timestamp', 'location', 'temperature_c', 'humidity']])
        else:
            st.warning("No hay datos en Supabase. Agrega algunos datos desde la aplicación.")
            show_demo_interface()
            
    except Exception as e:
        st.error(f"Error obteniendo datos: {e}")
        show_demo_interface()

def show_demo_interface():
    """Mostrar interfaz de demostración"""
    st.warning("📊 Modo Demostración - Usando datos de ejemplo")
    
    # Datos de ejemplo
    dates = [datetime.now() - timedelta(hours=i) for i in range(24)]
    sample_data = {
        'timestamp': dates,
        'location': ['Sala Principal', 'Cocina', 'Dormitorio'] * 8,
        'temperature_c': [22 + (i % 3) * 0.5 for i in range(24)],
        'humidity': [45 + (i % 15) for i in range(24)],
        'sensor_id': ['sensor_001', 'sensor_002', 'sensor_003'] * 8
    }
    
    df = pd.DataFrame(sample_data)
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ Temperatura Actual", "23.5°C", "0.5°C")
    with col2:
        st.metric("💧 Humedad", "47%", "-2%")
    with col3:
        st.metric("📍 Ubicaciones", "3 sensores")
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Temperatura por Ubicación")
        chart_data = df.groupby('location')['temperature_c'].mean()
        st.bar_chart(chart_data)
    
    with col2:
        st.subheader("📊 Evolución Temporal")
        st.line_chart(df.set_index('timestamp')['temperature_c'])
    
    # Formulario de ejemplo
    st.subheader("➕ Agregar Nueva Lectura (Demo)")
    with st.form("demo_form"):
        col1, col2 = st.columns(2)
        with col1:
            location = st.selectbox("Ubicación", ["Sala Principal", "Cocina", "Dormitorio"])
            temp = st.slider("Temperatura (°C)", 15.0, 35.0, 23.0)
        with col2:
            humidity = st.slider("Humedad (%)", 30, 80, 50)
            
        if st.form_submit_button("📊 Simular Lectura"):
            st.success(f"✅ Lectura simulada: {temp}°C en {location}")

if __name__ == "__main__":
    main()