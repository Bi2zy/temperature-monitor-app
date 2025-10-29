"""
Sistema de Monitoreo de Temperatura - Con Simulador
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Monitoreo de Temperatura", page_icon="🌡️", layout="wide"
)


def get_supabase_config():
    """Obtener configuración de Supabase"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    return supabase_url, supabase_key


def simulate_temperature_data(supabase, num_readings=5):
    """Simular datos de temperatura"""
    try:
        locations = [
            "Sala Principal",
            "Cocina",
            "Dormitorio",
            "Exterior",
            "Laboratorio",
        ]
        sensors = ["sensor_001", "sensor_002", "sensor_003", "sensor_004"]

        for i in range(num_readings):
            reading = {
                "sensor_id": random.choice(sensors),
                "location": random.choice(locations),
                "temperature_c": round(random.uniform(18.0, 32.0), 1),
                "humidity": random.randint(35, 85),
                "timestamp": (
                    datetime.now() - timedelta(hours=random.randint(0, 24))
                ).isoformat(),
            }

            supabase.insert_temperature_reading(reading)

        return True
    except Exception as e:
        st.error(f"Error simulando datos: {e}")
        return False


def main():
    st.title("🌡️ Sistema de Monitoreo de Temperatura")
    st.markdown("---")

    # Verificar configuración
    supabase_url, supabase_key = get_supabase_config()

    if not supabase_url or not supabase_key:
        st.error("Configura las variables SUPABASE_URL y SUPABASE_KEY en Railway")
        show_demo_interface()
        return

    try:
        from utils.database import SupabaseClient

        supabase = SupabaseClient(supabase_url, supabase_key)
        st.success("✅ Conectado a Supabase correctamente!")

        # SIMULADOR EN SIDEBAR
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎮 Simulador de Datos")

        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🌡️ +5 Lecturas"):
                if simulate_temperature_data(supabase, 5):
                    st.sidebar.success("✅ 5 lecturas agregadas!")
                    st.rerun()

        with col2:
            if st.button("📊 +10 Lecturas"):
                if simulate_temperature_data(supabase, 10):
                    st.sidebar.success("✅ 10 lecturas agregadas!")
                    st.rerun()

        # Obtener y mostrar datos reales
        show_real_data_interface(supabase)

    except Exception as e:
        st.error(f"Error conectando con Supabase: {e}")
        show_demo_interface()


def show_real_data_interface(supabase):
    """Interfaz con datos reales de Supabase"""

    # Obtener datos reales
    try:
        readings = supabase.get_temperature_readings_by_days(7)

        if readings:
            df = pd.DataFrame(readings)

            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_readings = len(df)
                st.metric("📊 Total Lecturas", total_readings)

            with col2:
                avg_temp = df["temperature_c"].mean()
                st.metric("🌡️ Promedio", f"{avg_temp:.1f}°C")

            with col3:
                locations_count = df["location"].nunique()
                st.metric("📍 Ubicaciones", locations_count)

            with col4:
                sensors_count = df["sensor_id"].nunique()
                st.metric("🔧 Sensores", sensors_count)

            # Mostrar últimas lecturas
            st.subheader("📋 Últimas Lecturas")
            display_df = df.head(10)[
                ["timestamp", "location", "sensor_id", "temperature_c", "humidity"]
            ].copy()
            display_df["timestamp"] = pd.to_datetime(
                display_df["timestamp"]
            ).dt.strftime("%Y-%m-%d %H:%M")
            display_df["temperature_c"] = display_df["temperature_c"].round(1)

            st.dataframe(display_df, use_container_width=True)

        else:
            st.warning(
                "No hay datos en Supabase. Usa el simulador para agregar datos de prueba."
            )
            show_demo_interface()

    except Exception as e:
        st.error(f"Error obteniendo datos: {e}")


def show_demo_interface():
    """Mostrar interfaz de demostración"""
    st.warning("📊 Modo Demostración - Usando datos de ejemplo")

    # Datos de ejemplo mejorados
    dates = [datetime.now() - timedelta(hours=i) for i in range(24)]
    sample_data = {
        "timestamp": dates,
        "location": ["Sala Principal", "Cocina", "Dormitorio"] * 8,
        "temperature_c": [22 + (i % 3) * 0.5 for i in range(24)],
        "humidity": [45 + (i % 15) for i in range(24)],
        "sensor_id": ["sensor_001", "sensor_002", "sensor_003"] * 8,
    }

    df = pd.DataFrame(sample_data)

    # Métricas de ejemplo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ Temperatura Actual", "23.5°C", "0.5°C")
    with col2:
        st.metric("💧 Humedad", "47%", "-2%")
    with col3:
        st.metric("📍 Ubicaciones", "3 sensores")

    # Gráficos de ejemplo
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Temperatura por Ubicación")
        chart_data = df.groupby("location")["temperature_c"].mean()
        st.bar_chart(chart_data)

    with col2:
        st.subheader("📊 Evolución Temporal")
        st.line_chart(df.set_index("timestamp")["temperature_c"])


if __name__ == "__main__":
    main()
