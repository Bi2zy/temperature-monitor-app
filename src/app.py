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
    page_title="Sistema de Monitoreo de Temperatura",
    page_icon="🌡️",
    layout="wide"
)


def get_supabase_config():
    """Obtener configuración de Supabase - Compatible con NEXT_PUBLIC_"""
    # Intentar primero con los nombres normales
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    # Si no existen, intentar con NEXT_PUBLIC_ (para compatibilidad)
    if not supabase_url:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    if not supabase_key:
        supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

    return supabase_url, supabase_key


def debug_environment():
    """Mostrar información de debug"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Debug Info")

    supabase_url, supabase_key = get_supabase_config()

    st.sidebar.write("**Variables encontradas:**")
    st.sidebar.write(f"🔗 URL: {'✅' if supabase_url else '❌'}")
    st.sidebar.write(f"🔑 KEY: {'✅' if supabase_key else '❌'}")

    if supabase_url:
        st.sidebar.code(f"URL: {supabase_url[:30]}...")
    if supabase_key:
        st.sidebar.code(f"KEY: {supabase_key[:20]}...")


def initialize_supabase_client():
    """Inicializar cliente Supabase"""
    supabase_url, supabase_key = get_supabase_config()

    if not supabase_url or not supabase_key:
        st.error("""
        ❌ **Variables no configuradas correctamente**

        Se necesitan estas variables:
        - `SUPABASE_URL` o `NEXT_PUBLIC_SUPABASE_URL`
        - `SUPABASE_KEY` o `NEXT_PUBLIC_SUPABASE_ANON_KEY`
        """)
        return None

    try:
        from utils.database import SupabaseClient
        supabase = SupabaseClient(supabase_url, supabase_key)

        # Test de conexión
        test_result = supabase.get_temperature_readings_by_days(1)
        msg = f"✅ ¡Conectado a Supabase! ({len(test_result)} registros)"
        st.success(msg)
        return supabase

    except Exception as e:
        st.error(f"❌ Error conectando con Supabase: {str(e)}")
        return None


def simulate_temperature_data(supabase, num_readings=5):
    """Simular datos de temperatura"""
    try:
        locations = [
            "Sala Principal", "Cocina", "Dormitorio", "Exterior", "Oficina"
        ]
        sensors = [f"sensor_{i:03d}" for i in range(1, 4)]

        new_readings = []
        for _ in range(num_readings):
            reading = {
                "sensor_id": random.choice(sensors),
                "location": random.choice(locations),
                "temperature_c": round(random.uniform(18.0, 32.0), 1),
                "humidity": random.randint(35, 85),
                "timestamp": (
                    datetime.now() - timedelta(hours=random.randint(0, 24))
                ).isoformat(),
            }
            new_readings.append(reading)
            supabase.insert_temperature_reading(reading)

        return True, new_readings
    except Exception as e:
        st.error(f"❌ Error simulando datos: {e}")
        return False, []


def main():
    st.title("🌡️ Sistema de Monitoreo de Temperatura")
    st.markdown("---")

    # Debug info
    debug_environment()

    # Inicializar Supabase
    supabase = initialize_supabase_client()

    if supabase:
        # ===== INTERFAZ PRINCIPAL CON SUPABASE =====
        st.success("## ✅ Modo Conectado - Base de Datos Real")

        # Simulador en sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎮 Simulador de Datos")

        num_readings = st.sidebar.slider("Lecturas a generar", 1, 20, 5)
        if st.sidebar.button("🚀 Generar Datos", type="primary"):
            success, new_readings = simulate_temperature_data(supabase, num_readings)
            if success:
                st.sidebar.success(f"✅ {num_readings} lecturas agregadas!")
                st.rerun()

        # Obtener y mostrar datos reales
        try:
            readings = supabase.get_temperature_readings_by_days(7)

            if readings:
                df = pd.DataFrame(readings)

                # Métricas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Lecturas", len(df))
                with col2:
                    avg_temp = df['temperature_c'].mean()
                    st.metric("🌡️ Temp. Promedio", f"{avg_temp:.1f}°C")
                with col3:
                    st.metric("📍 Ubicaciones", df['location'].nunique())
                with col4:
                    st.metric("🔧 Sensores", df['sensor_id'].nunique())

                # Últimas lecturas
                st.subheader("📋 Últimas Lecturas")
                display_df = df.head(10).copy()
                display_df['timestamp'] = pd.to_datetime(
                    display_df['timestamp']
                ).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(display_df, use_container_width=True)

            else:
                warning_msg = "📭 No hay datos en la base de datos."
                warning_msg += " Usa el simulador para agregar datos."
                st.warning(warning_msg)

        except Exception as e:
            st.error(f"❌ Error obteniendo datos: {e}")

    else:
        # ===== MODO DEMOSTRACIÓN =====
        st.warning("## 🎯 Modo Demostración - Datos de Ejemplo")

        # Datos de ejemplo
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

        st.dataframe(df.head(10), use_container_width=True)


if __name__ == "__main__":
    main()
