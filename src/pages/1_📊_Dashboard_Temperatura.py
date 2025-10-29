"""
Dashboard Avanzado de Monitoreo de Temperatura
Visualizaciones en tiempo real y análisis térmico
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import SupabaseClient

def main():
    """Dashboard principal de temperatura"""
    st.title("📊 Dashboard de Temperatura en Tiempo Real")
    
    # Inicializar cliente de Supabase
    supabase_url = st.secrets.get(https://vhycvnxspssqbwriyewb.supabase.co)
    supabase_key = st.secrets.get(eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoeWN2bnhzcHNzcWJ3cml5ZXdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1MzMwNTksImV4cCI6MjA3NzEwOTA1OX0.FtavudySUkebI8MPfQDE0uV5CK0efEbP2l_n6SXxZrc)
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
        return
    
    df = pd.DataFrame(readings)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['temperature_f'] = df['temperature_c'] * 9/5 + 32
    
    # Aplicar filtro de ubicación
    if location_filter != "Todas":
        df = df[df['location'] == location_filter]
    
    # Métricas principales
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
    
    # Gráficos
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
        
        fig_heatmap = px.imshow(
            heatmap_data,
            title="Temperatura Promedio por Ubicación y Hora",
            labels=dict(x="Hora del Día", y="Ubicación", color="Temperatura (°C)")
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Datos Detallados")
    display_df = df[['timestamp', 'location', 'sensor_id', 'temperature_c', 'humidity']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['temperature_c'] = display_df['temperature_c'].round(1)
    
    st.dataframe(display_df, use_container_width=True)

if __name__ == "__main__":
    main()