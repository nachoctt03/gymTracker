from datetime import datetime
from typing import Optional


class Ejercicio:
    def __init__(self, nombre: str, peso: float, repeticiones: int, series: int, notas: str = ""):
        self.id: Optional[str] = None
        self.nombre = nombre
        self.peso = peso
        self.repeticiones = repeticiones
        self.series = series
        self.fecha = datetime.now().strftime("%Y-%m-%d")
        self.notas = notas

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'peso': self.peso,
            'repeticiones': self.repeticiones,
            'series': self.series,
            'fecha': self.fecha,
            'notas': self.notas
        }

    @classmethod
    def from_dict(cls, data: dict, ejercicio_id: str = None):
        ejercicio = cls(
            nombre=data.get('nombre', ''),
            peso=data.get('peso', 0.0),
            repeticiones=data.get('repeticiones', 0),
            series=data.get('series', 0),
            notas=data.get('notas', '')
        )
        ejercicio.id = ejercicio_id or data.get('id')
        ejercicio.fecha = data.get('fecha', datetime.now().strftime("%Y-%m-%d"))
        return ejercicio

    def __str__(self):
        return f"{self.nombre} - {self.peso} kg x {self.repeticiones} reps x {self.series} series ({self.fecha})"
