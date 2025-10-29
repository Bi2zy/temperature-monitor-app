"""
Página de Streamlit: Histórico
Permite ver lecturas históricas y descargar los datos como CSV.
"""

import os

import pandas as pd
import streamlit as st

from utils.database import SupabaseClient
from utils.helpers import to_csv_bytes

st.set_page_config(page_title="Histórico", layout="wide")
st.title("📈 Histórico de Temperaturas")

days = st.sidebar.selectbox(
    "Periodo (días)",
    [1, 7, 30, 90],
    index=1,
    help="Filtrar lecturas de los últimos N días",
)
_ = st.sidebar.button("🔄 Refrescar datos")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if supabase_url and supabase_key:
    client = SupabaseClient(supabase_url, supabase_key)
    data = client.get_temperature_readings_by_days(days)
    if data:
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(
            columns=["sensor_id", "location", "temperature_c", "humidity", "timestamp"]
        )
else:
    st.info("Supabase no configurado. Mostrando datos de ejemplo.")
    sample = [
        {
            "sensor_id": "sensor_001",
            "location": "Sala Principal",
            "temperature_c": 22.5,
            "humidity": 45,
            "timestamp": "2025-10-28T12:00:00Z",
        },
        {
            "sensor_id": "sensor_002",
            "location": "Cocina",
            "temperature_c": 24.3,
            "humidity": 55,
            "timestamp": "2025-10-27T18:30:00Z",
        },
    ]
    df = pd.DataFrame(sample)


st.dataframe(df)

try:
    csv_bytes = to_csv_bytes(df)
    st.download_button(
        "📥 Descargar CSV",
        data=csv_bytes,
        file_name=f"temperature_history_{days}d.csv",
        mime="text/csv",
    )
except Exception as e:
    st.error(f"Error preparando CSV: {e}")
