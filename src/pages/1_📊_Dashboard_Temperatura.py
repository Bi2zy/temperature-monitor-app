"""
Dashboard Avanzado de Monitoreo de Temperatura
Visualizaciones en tiempo real y análisis térmico
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
from utils.database import SupabaseClient

def get_supabase_credentials():
    """Obtener credenciales de manera segura - VERSIÓN CORREGIDA"""
    # PRIMERO: Variables de entorno (funciona en Railway)
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    # SEGUNDO: Secrets de Streamlit (funciona localmente)
    if not supabase_url or not supabase_key:
        try:
            supabase_url = st.secrets.get("SUPABASE_URL")
            supabase_key = st.secrets.get("SUPABASE_KEY")
        except:
            pass  # Ignorar error si no hay secrets
    
    return supabase_url, supabase_key

def main():
    """Dashboard principal de temperatura"""
    st.title("📊 Dashboard de Temperatura en Tiempo Real")
    
    # Obtener credenciales
    supabase_url, supabase_key = get_supabase_credentials()
    
    # Verificar que tenemos las credenciales
    if not supabase_url or not supabase_key:
        st.error("""
        ❌ No se encontraron las credenciales de Supabase.
        
        **Configura en Railway:**
        - SUPABASE_URL = https://vhycvnxspssqbwriyewb.supabase.co
        - SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        """)
        
        # Mostrar datos de ejemplo
        show_sample_data()
        return
    
    try:
        # Inicializar cliente de Supabase
        supabase = SupabaseClient(supabase_url, supabase_key)
        
        # Filtros de fecha
        col1, col2, col3 = st.columns(3)
        with col1:
            days_back = st.selectbox("Período de análisis", [1, 7, 30, 90], index=1)
        
        with col2:
            location_filter = st.selectbox("Filtrar por ubicación", ["Todas", "Sala Principal", "Cocina", "Dormitorio", "Exterior", "Laboratorio"])
        
        # Obtener datos
        readings = supabase.get_temperature_readings_by_days(days_back)
        
        if not readings:
            st.warning("No hay datos de temperatura para el período seleccionado")
            show_sample_data()
            return
        
        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['temperature_f'] = df['temperature_c'] * 9/5 + 32
        
        # Aplicar filtro de ubicación
        if location_filter != "Todas":
            df = df[df['location'] == location_filter]
        
        # Mostrar métricas y gráficos
        display_metrics(df)
        display_charts(df, days_back)
        display_data_table(df)
        
    except Exception as e:
        st.error(f"Error conectando con Supabase: {e}")
        st.info("Mostrando datos de ejemplo...")
        show_sample_data()

# [El resto del código se mantiene igual...]
def display_metrics(df):
    """Mostrar métricas principales"""
    st.subheader("📈 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_temp = df.iloc[0]['temperature_c'] if not df.empty else 0
        st.metric("🌡️ Temp. Actual", f"{current_temp:.1f}°C", f"{current_temp * 9/5 + 32:.1f}°F")
    
    with col2:
        avg_temp = df['temperature_c'].mean()
        st.metric("📊 Promedio", f"{avg_temp:.1f}°C")
    
    with col3:
        max_temp = df['temperature_c'].max()
        st.metric("🔥 Máxima", f"{max_temp:.1f}°C")
    
    with col4:
        min_temp = df['temperature_c'].min()
        st.metric("❄️ Mínima", f"{min_temp:.1f}°C")
    
    st.markdown("---")

def display_charts(df, days_back):
    """Mostrar gráficos"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de línea de temperatura
        st.subheader("📈 Evolución de Temperatura")
        fig_temp = px.line(
            df, 
            x='timestamp', 
            y='temperature_c',
            color='location',
            title=f"Temperatura (°C) - Últimos {days_back} días",
            labels={'temperature_c': 'Temperatura (°C)', 'timestamp': 'Fecha/Hora'}
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Gráfico de humedad
        st.subheader("💧 Niveles de Humedad")
        fig_humidity = px.line(
            df, 
            x='timestamp', 
            y='humidity',
            color='location',
            title=f"Humedad (%) - Últimos {days_back} días",
            labels={'humidity': 'Humedad (%)', 'timestamp': 'Fecha/Hora'}
        )
        st.plotly_chart(fig_humidity, use_container_width=True)
    
    # Distribución de temperaturas
    st.subheader("📊 Distribución de Temperaturas")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(
            df, 
            x='temperature_c',
            nbins=20,
            title="Distribución de Temperaturas",
            labels={'temperature_c': 'Temperatura (°C)'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Mapa de calor por ubicación y hora
        df['hour'] = df['timestamp'].dt.hour
        heatmap_data = df.pivot_table(
            values='temperature_c', 
            index='location', 
            columns='hour', 
            aggfunc='mean'
        ).fillna(0)
        
        if not heatmap_data.empty:
            fig_heatmap = px.imshow(
                heatmap_data,
                title="Temperatura Promedio por Ubicación y Hora",
                labels=dict(x="Hora del Día", y="Ubicación", color="Temperatura (°C)")
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

def display_data_table(df):
    """Mostrar tabla de datos"""
    st.subheader("📋 Datos Detallados")
    display_df = df[['timestamp', 'location', 'sensor_id', 'temperature_c', 'humidity']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['temperature_c'] = display_df['temperature_c'].round(1)
    
    st.dataframe(display_df, use_container_width=True)

def show_sample_data():
    """Mostrar datos de ejemplo cuando no hay conexión"""
    st.warning("📊 Modo demostración - Datos de ejemplo")
    
    # Generar datos de ejemplo
    dates = [datetime.now() - timedelta(hours=i) for i in range(24)]
    sample_data = {
        'timestamp': dates,
        'location': ['Sala Principal', 'Cocina', 'Dormitorio'] * 8,
        'temperature_c': [22 + (i % 3) * 0.5 for i in range(24)],
        'humidity': [45 + (i % 15) for i in range(24)],
        'sensor_id': ['sensor_001', 'sensor_002', 'sensor_003'] * 8
    }
    
    df = pd.DataFrame(sample_data)
    display_metrics(df)
    display_charts(df, 1)
    display_data_table(df)

if __name__ == "__main__":
    main()