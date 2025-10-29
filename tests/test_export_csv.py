import sys
from pathlib import Path

# Asegurar que `src/` esté en sys.path para importar utils
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd

from utils.helpers import to_csv_bytes


def test_to_csv_bytes_basic():
    df = pd.DataFrame([
        {
            "sensor_id": "sensor_1",
            "location": "Sala",
            "temperature_c": 22.5,
            "humidity": 45,
            "timestamp": "2025-10-28T12:00:00Z",
        }
    ])

    b = to_csv_bytes(df)
    s = b.decode("utf-8")

    assert "sensor_id" in s
    assert "sensor_1" in s


def test_to_csv_bytes_empty_dataframe():
    df = pd.DataFrame(columns=["sensor_id", "location", "temperature_c", "humidity", "timestamp"])
    b = to_csv_bytes(df)
    s = b.decode("utf-8")

    # debe contener solo cabeceras
    assert "sensor_id" in s
    # no hay filas además de la cabecera
    assert s.strip().count("\n") == 0 or s.strip().endswith("sensor_id,location,temperature_c,humidity,timestamp")
