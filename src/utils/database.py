"""
Módulo para manejo de operaciones con Supabase - Específico para Temperatura
"""

from datetime import datetime, timedelta

import supabase


class SupabaseClient:
    """Cliente especializado para datos de temperatura"""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.client = supabase.create_client(supabase_url, supabase_key)

    def insert_temperature_reading(self, reading_data: dict) -> bool:
        """
        Insertar nueva lectura de temperatura

        Args:
            reading_data: Datos de la lectura de temperatura

        Returns:
            True si fue exitoso, False en caso contrario
        """
        try:
            response = (
                self.client.table("temperature_readings").insert(reading_data).execute()
            )
            return bool(response.data)
        except Exception as e:
            print(f"Error insertando lectura de temperatura: {e}")
            return False

    def get_recent_temperature_readings(self, limit: int = 10) -> list[dict]:
        """
        Obtener lecturas recientes de temperatura

        Args:
            limit: Número máximo de lecturas a obtener

        Returns:
            Lista de lecturas de temperatura
        """
        try:
            response = (
                self.client.table("temperature_readings")
                .select("*")
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error obteniendo lecturas recientes: {e}")
            return []

    def get_temperature_readings_by_days(self, days: int) -> list[dict]:
        """
        Obtener lecturas de los últimos N días

        Args:
            days: Número de días hacia atrás

        Returns:
            Lista de lecturas de temperatura
        """
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            response = (
                self.client.table("temperature_readings")
                .select("*")
                .gte("timestamp", start_date)
                .order("timestamp", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error obteniendo lecturas por días: {e}")
            return []

    def get_temperature_stats(self, location: str = None) -> dict:
        """
        Obtener estadísticas de temperatura

        Args:
            location: Filtrar por ubicación (opcional)

        Returns:
            Diccionario con estadísticas
        """
        try:
            query = self.client.table("temperature_readings").select("*")

            if location:
                query = query.eq("location", location)

            response = query.execute()
            data = response.data

            if not data:
                return {}

            temperatures = [r["temperature_c"] for r in data]
            humidities = [r["humidity"] for r in data]

            return {
                "avg_temperature": sum(temperatures) / len(temperatures),
                "max_temperature": max(temperatures),
                "min_temperature": min(temperatures),
                "avg_humidity": sum(humidities) / len(humidities),
                "total_readings": len(data),
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {}
