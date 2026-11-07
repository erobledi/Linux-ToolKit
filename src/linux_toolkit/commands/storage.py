
"""
Información de discos y particiones del sistema.
"""

import psutil

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


# Sistemas de archivos virtuales que queremos ocultar
SISTEMAS_VIRTUALES = {
    "tmpfs",
    "devtmpfs",
    "squashfs",
    "overlay",
    "proc",
    "sysfs",
    "devpts",
    "cgroup",
    "cgroup2",
    "pstore",
    "securityfs",
    "debugfs",
    "tracefs",
    "configfs",
    "fusectl",
    "mqueue",
    "hugetlbfs",
    "autofs"
}


def formatear_bytes(valor: int) -> str:
    """Convierte bytes a una unidad legible."""

    unidades = ["B", "KB", "MB", "GB", "TB"]

    for unidad in unidades:
        if valor < 1024:
            return f"{valor:.2f} {unidad}"

        valor /= 1024

    return f"{valor:.2f} PB"


def obtener_particiones() -> list:
    """Obtiene las particiones físicas y sus puntos de montaje."""

    particiones = []

    for particion in psutil.disk_partitions(all=False):

        sistema_archivos = particion.fstype.lower()

        if sistema_archivos in SISTEMAS_VIRTUALES:
            continue

        try:
            uso = psutil.disk_usage(particion.mountpoint)

        except (PermissionError, OSError):
            continue

        particiones.append({
            "dispositivo": particion.device,
            "montaje": particion.mountpoint,
            "sistema_archivos": particion.fstype,
            "total": uso.total,
            "usado": uso.used,
            "libre": uso.free,
            "porcentaje": uso.percent
        })

    return particiones


def show_disk() -> None:
    """Muestra información de almacenamiento."""

    particiones = obtener_particiones()

    if not particiones:
        console.print(
            "[yellow]No se han encontrado particiones disponibles.[/yellow]"
        )
        return

    tabla = Table(
        title="Discos y particiones",
        border_style="cyan",
        show_lines=True
    )

    tabla.add_column("Dispositivo", style="bold cyan")
    tabla.add_column("Montaje", style="white")
    tabla.add_column("Sistema archivos", style="white")
    tabla.add_column("Capacidad", justify="right")
    tabla.add_column("Utilizado", justify="right")
    tabla.add_column("Disponible", justify="right")
    tabla.add_column("Ocupación", justify="right")

    for particion in particiones:

        porcentaje = particion["porcentaje"]

        if porcentaje >= 90:
            color = "red"
        elif porcentaje >= 75:
            color = "yellow"
        else:
            color = "green"

        tabla.add_row(
            particion["dispositivo"],
            particion["montaje"],
            particion["sistema_archivos"],
            formatear_bytes(particion["total"]),
            formatear_bytes(particion["usado"]),
            formatear_bytes(particion["libre"]),
            f"[{color}]{porcentaje:.1f}%[/{color}]"
        )

    console.print(
        Panel(
            tabla,
            title="[bold white]Linux-ToolKit | DISK[/bold white]",
            border_style="cyan"
        )
    )
