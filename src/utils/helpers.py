"""
Utilidades específicas para el sistema de monitoreo de temperatura
"""
from datetime import datetime
from typing import Union, Optional
import io
import pandas as pd

def validate_temperature(temperature: float) -> bool:
    """
    Validar que la temperatura esté en un rango razonable
    
    Args:
        temperature: Temperatura en Celsius
        
    Returns:
        True si es válida, False en caso contrario
    """
    return -50 <= temperature <= 100

def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convertir Celsius a Fahrenheit
    
    Args:
        celsius: Temperatura en Celsius
        
    Returns:
        Temperatura en Fahrenheit
    """
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Convertir Fahrenheit a Celsius
    
    Args:
        fahrenheit: Temperatura en Fahrenheit
        
    Returns:
        Temperatura en Celsius
    """
    return (fahrenheit - 32) * 5/9

def format_timestamp(timestamp: str) -> str:
    """
    Formatear timestamp para visualización
    
    Args:
        timestamp: Timestamp en formato ISO
        
    Returns:
        Timestamp formateado
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return timestamp

def get_temperature_status(temperature: float) -> dict:
    """
    Obtener estado de la temperatura con colores e iconos
    
    Args:
        temperature: Temperatura en Celsius
        
    Returns:
        Diccionario con estado, color e icono
    """
    if temperature < 0:
        return {"status": "Congelación", "color": "#1E90FF", "icon": "🧊"}
    elif temperature < 10:
        return {"status": "Muy Frío", "color": "#87CEEB", "icon": "❄️"}
    elif temperature < 20:
        return {"status": "Fresco", "color": "#98FB98", "icon": "🌤️"}
    elif temperature < 27:
        return {"status": "Confortable", "color": "#32CD32", "icon": "😊"}
    elif temperature < 35:
        return {"status": "Cálido", "color": "#FFA500", "icon": "☀️"}
    else:
        return {"status": "Caluroso", "color": "#FF4500", "icon": "🔥"}

def calculate_heat_index(temperature: float, humidity: float) -> float:
    """
    Calcular índice de calor (sensación térmica)
    
    Args:
        temperature: Temperatura en Celsius
        humidity: Humedad relativa en porcentaje
        
    Returns:
        Índice de calor en Celsius
    """
    # Fórmula simplificada del índice de calor
    temp_f = celsius_to_fahrenheit(temperature)
    
    # Cálculo del heat index en Fahrenheit
    hi_f = -42.379 + (2.04901523 * temp_f) + (10.14333127 * humidity) - \
           (0.22475541 * temp_f * humidity) - (6.83783 * 10**-3 * temp_f**2) - \
           (5.481717 * 10**-2 * humidity**2) + (1.22874 * 10**-3 * temp_f**2 * humidity) + \
           (8.5282 * 10**-4 * temp_f * humidity**2) - (1.99 * 10**-6 * temp_f**2 * humidity**2)
    
    return fahrenheit_to_celsius(hi_f)


def to_csv_bytes(df: pd.DataFrame, expected_columns: Optional[list] = None) -> bytes:
    """
    Convertir un DataFrame a bytes CSV (UTF-8) listos para descarga.

    - Si `expected_columns` se proporciona, verificará que las columnas estén presentes
      y lanzará ValueError si falta alguna.
    - Convierte valores datetime a ISO strings para garantizar serialización.
    - Si el DataFrame está vacío, devolverá un CSV con solo cabeceras.

    Args:
        df: DataFrame a exportar.
        expected_columns: Lista opcional de columnas esperadas.

    Returns:
        Bytes en codificación utf-8 del CSV generado.
    """
    if expected_columns:
        missing = [c for c in expected_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing expected columns: {missing}")

    # Hacemos una copia para no mutar el original
    df_copy = df.copy()

    # Convertir columnas datetime a ISO strings para evitar problemas de serialización
    for col in df_copy.columns:
        try:
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = df_copy[col].dt.tz_convert(None).dt.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                # Intentar convertir objetos que puedan ser datetimes
                df_copy[col] = df_copy[col].apply(lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)
        except Exception:
            # Si falla la conversión, la dejamos tal cual
            pass

    buffer = io.StringIO()
    df_copy.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")