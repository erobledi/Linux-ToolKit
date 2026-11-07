
"""
Funciones auxiliares comunes de Linux-ToolKit.
"""

import platform
from datetime import timedelta


def formatear_bytes(valor: int | float) -> str:
    """Convierte bytes a una unidad legible."""

    unidades = ["B", "KB", "MB", "GB", "TB"]

    for unidad in unidades:
        if valor < 1024:
            return f"{valor:.2f} {unidad}"

        valor /= 1024

    return f"{valor:.2f} PB"


def formatear_tiempo(segundos: float) -> str:
    """Convierte segundos en días, horas y minutos."""

    tiempo = timedelta(seconds=int(segundos))
    dias = tiempo.days
    horas, resto = divmod(tiempo.seconds, 3600)
    minutos = resto // 60

    return f"{dias} días, {horas} horas y {minutos} minutos"


def obtener_codificacion_sistema() -> str:
    """Detecta la codificación utilizada por el sistema."""

    if platform.system() == "Windows":
        import ctypes

        codigo = ctypes.windll.kernel32.GetOEMCP()
        return f"cp{codigo}"

    return "utf-8"
