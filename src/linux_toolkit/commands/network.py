
"""
Información general del sistema operativo y del equipo.
"""

import json
import platform
import socket
import subprocess
import time

from linux_toolkit.core.utils import (
    formatear_bytes,
    formatear_tiempo,
    obtener_codificacion_sistema
)

import psutil

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def obtener_modelo_cpu() -> str:
    """Obtiene el modelo del procesador."""

    modelo = platform.processor()

    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    if linea.startswith("model name"):
                        modelo = linea.split(":", 1)[1].strip()
                        break

        except OSError:
            pass

    return modelo or "No disponible"


def show_system() -> None:
    """Muestra información general del sistema."""

    sistema = platform.system()
    version = platform.version()
    arquitectura = platform.machine()
    procesador = obtener_modelo_cpu()

    nombre_equipo = socket.gethostname()

    nucleos_fisicos = psutil.cpu_count(logical=False) or 0
    nucleos_logicos = psutil.cpu_count(logical=True) or 0

    memoria = psutil.virtual_memory()

    tiempo_encendido = time.time() - psutil.boot_time()

    tabla = Table(
        title="Información del sistema",
        border_style="cyan",
        show_lines=True
    )

    tabla.add_column("Propiedad", style="bold cyan")
    tabla.add_column("Valor", style="white")

    tabla.add_row("Equipo", nombre_equipo)
    tabla.add_row("Sistema operativo", sistema)
    tabla.add_row("Versión", version)
    tabla.add_row("Arquitectura", arquitectura)
    tabla.add_row("Procesador", procesador)
    tabla.add_row("Núcleos físicos", str(nucleos_fisicos))
    tabla.add_row("Hilos lógicos", str(nucleos_logicos))
    tabla.add_row("Memoria RAM total", formatear_bytes(memoria.total))
    tabla.add_row("Memoria RAM disponible", formatear_bytes(memoria.available))
    tabla.add_row("Memoria RAM utilizada", f"{memoria.percent:.1f}%")
    tabla.add_row("Tiempo encendido", formatear_tiempo(tiempo_encendido))

    console.print(
        Panel(
            tabla,
            title="[bold white]Linux-ToolKit | SYSTEM[/bold white]",
            border_style="cyan"
        )
    )


def show_cpu() -> None:
    """Muestra información y monitorización del procesador."""

    from rich.text import Text

    modelo = obtener_modelo_cpu()
    nucleos_fisicos = psutil.cpu_count(logical=False) or 0
    nucleos_logicos = psutil.cpu_count(logical=True) or 0
    frecuencia = psutil.cpu_freq()

    console.print("[dim]Midiendo actividad del procesador...[/dim]")

    uso = psutil.cpu_percent(interval=1, percpu=True)

    uso_total = sum(uso) / len(uso) if uso else 0

    tabla = Table(
        title="Información del procesador",
        border_style="cyan",
        show_lines=True
    )

    tabla.add_column("Propiedad", style="bold cyan")
    tabla.add_column("Valor")

    tabla.add_row("Modelo", modelo)
    tabla.add_row("Núcleos físicos", str(nucleos_fisicos))
    tabla.add_row("Hilos lógicos", str(nucleos_logicos))

    if frecuencia:
        tabla.add_row("Frecuencia actual", f"{frecuencia.current:.0f} MHz")

        if frecuencia.max:
            tabla.add_row("Frecuencia máxima", f"{frecuencia.max:.0f} MHz")

    tabla.add_row("Uso total", f"{uso_total:.1f}%")

    console.print(
        Panel(
            tabla,
            title="[bold white]Linux-ToolKit | CPU[/bold white]",
            border_style="cyan"
        )
    )

    tabla_nucleos = Table(
        title="Actividad por núcleo lógico",
        border_style="cyan"
    )

    tabla_nucleos.add_column("Núcleo", style="bold cyan")
    tabla_nucleos.add_column("Uso", justify="right")
    tabla_nucleos.add_column("Actividad")

    for numero, porcentaje in enumerate(uso):

        if porcentaje >= 80:
            color = "red"

        elif porcentaje >= 50:
            color = "yellow"

        else:
            color = "green"

        bloques = min(20, max(0, int(porcentaje / 5)))

        barra = "█" * bloques + "░" * (20 - bloques)

        tabla_nucleos.add_row(
            str(numero),
            f"{porcentaje:.1f}%",
            f"[{color}]{barra}[/{color}]"
        )

    console.print(tabla_nucleos)

    temperaturas = {}

    if hasattr(psutil, "sensors_temperatures"):
        try:
            temperaturas = psutil.sensors_temperatures()

        except (OSError, RuntimeError):
            temperaturas = {}

    if temperaturas:

        tabla_temp = Table(
            title="Temperaturas",
            border_style="cyan"
        )

        tabla_temp.add_column("Sensor", style="bold cyan")
        tabla_temp.add_column("Temperatura", justify="right")

        for sensor, lecturas in temperaturas.items():
            for lectura in lecturas:
                tabla_temp.add_row(
                    lectura.label or sensor,
                    f"{lectura.current:.1f} °C"
                )

        console.print(tabla_temp)

    else:
        console.print(
            "[yellow]No hay sensores de temperatura disponibles.[/yellow]"
        )


def show_ram() -> None:
    """Muestra información de memoria RAM y memoria Swap."""

    memoria = psutil.virtual_memory()
    swap = psutil.swap_memory()

    tabla = Table(
        title="Memoria RAM",
        border_style="cyan",
        show_lines=True
    )

    tabla.add_column("Propiedad", style="bold cyan")
    tabla.add_column("Valor", justify="right")

    tabla.add_row("Total", formatear_bytes(memoria.total))
    tabla.add_row("Utilizada", formatear_bytes(memoria.used))
    tabla.add_row("Disponible", formatear_bytes(memoria.available))
    tabla.add_row("Libre", formatear_bytes(memoria.free))
    tabla.add_row("Ocupación", f"{memoria.percent:.1f}%")

    console.print(
        Panel(
            tabla,
            title="[bold white]Linux-ToolKit | RAM[/bold white]",
            border_style="cyan"
        )
    )

    porcentaje = memoria.percent
    bloques = min(20, max(0, int(porcentaje / 5)))

    color = (
        "red" if porcentaje >= 90
        else "yellow" if porcentaje >= 75
        else "green"
    )

    barra = "█" * bloques + "░" * (20 - bloques)

    console.print(
        f"RAM: [{color}]{barra}[/{color}] {porcentaje:.1f}%\n"
    )

    tabla_swap = Table(
        title="Memoria Swap",
        border_style="cyan",
        show_lines=True
    )

    tabla_swap.add_column("Propiedad", style="bold cyan")
    tabla_swap.add_column("Valor", justify="right")

    tabla_swap.add_row("Total", formatear_bytes(swap.total))
    tabla_swap.add_row("Utilizada", formatear_bytes(swap.used))
    tabla_swap.add_row("Disponible", formatear_bytes(swap.free))
    tabla_swap.add_row("Ocupación", f"{swap.percent:.1f}%")

    console.print(tabla_swap)


def show_processes() -> None:
    """Muestra los procesos activos y su consumo de recursos."""

    procesos = []

    # Primera lectura para inicializar las métricas de CPU.
    for proceso in psutil.process_iter():
        try:
            proceso.cpu_percent(interval=None)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(1)

    # Recopilar información de los procesos.
    for proceso in psutil.process_iter(
        ["pid", "name", "username", "status", "memory_info", "create_time"]
    ):
        try:
            datos = proceso.info

            memoria = (
                datos["memory_info"].rss
                if datos["memory_info"]
                else 0
            )

            procesos.append({
                "pid": datos["pid"],
                "nombre": datos["name"] or "Desconocido",
                "usuario": datos["username"] or "Desconocido",
                "cpu": proceso.cpu_percent(interval=None),
                "memoria": memoria,
                "estado": datos["status"] or "Desconocido"
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    procesos.sort(
        key=lambda elemento: elemento["cpu"],
        reverse=True
    )

    tabla = Table(
        title="Procesos activos (Top 20 por CPU)",
        border_style="cyan",
        show_lines=True
    )

    tabla.add_column("PID", justify="right", style="bold cyan")
    tabla.add_column("Proceso")
    tabla.add_column("Usuario")
    tabla.add_column("CPU", justify="right")
    tabla.add_column("RAM", justify="right")
    tabla.add_column("Estado")

    for proceso in procesos[:20]:

        cpu = proceso["cpu"]

        color = (
            "red" if cpu >= 80
            else "yellow" if cpu >= 40
            else "green"
        )

        tabla.add_row(
            str(proceso["pid"]),
            proceso["nombre"],
            proceso["usuario"],
            f"[{color}]{cpu:.1f}%[/{color}]",
            formatear_bytes(proceso["memoria"]),
            proceso["estado"]
        )

    console.print(
        Panel(
            tabla,
            title="[bold white]Linux-ToolKit | PROCESSES[/bold white]",
            border_style="cyan"
        )
    )

    console.print(
        f"[dim]Procesos detectados: {len(procesos)}[/dim]"
    )


def show_services(filtro: str = "", activos: bool = False) -> None:
    """Muestra los servicios del sistema operativo."""

    sistema = platform.system()

    try:
        if sistema == "Windows":

            comando = [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "[Console]::OutputEncoding = "
                    "New-Object System.Text.UTF8Encoding($false); "
                    "$OutputEncoding = [Console]::OutputEncoding; "
                    "Get-CimInstance Win32_Service | "
                    "Select-Object Name,DisplayName,State,StartMode,Description | "
                    "ConvertTo-Json -Compress"
                )
            ]

        elif sistema == "Linux":

            comando = [
                "systemctl",
                "list-units",
                "--type=service",
                "--all",
                "--no-legend",
                "--no-pager"
            ]

        else:
            console.print("[red]Sistema operativo no compatible.[/red]")
            return

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding=obtener_codificacion_sistema(),
            errors="replace",
            timeout=30
        )

        if resultado.returncode != 0:
            console.print(
                f"[red]Error al consultar servicios: "
                f"{resultado.stderr.strip()}[/red]",
                markup=False
            )
            return

        tabla = Table(
            title="Servicios del sistema",
            border_style="cyan",
            show_lines=True
        )

        tabla.add_column("Nombre", style="bold cyan")
        tabla.add_column("Descripción")
        tabla.add_column("Estado")
        tabla.add_column("Inicio")

        if sistema == "Windows":

            datos = json.loads(resultado.stdout or "[]")

            if isinstance(datos, dict):
                datos = [datos]

            for servicio in datos:

                nombre = servicio.get("Name") or ""
                descripcion = servicio.get("Description") or "-"
                estado = servicio.get("State") or "Desconocido"
                inicio = servicio.get("StartMode") or "-"

                if filtro and filtro.lower() not in nombre.lower():
                    continue

                if activos and estado.lower() != "running":
                    continue

                color = "green" if estado.lower() == "running" else "red"

                tabla.add_row(
                    nombre,
                    descripcion,
                    f"[{color}]{estado}[/{color}]",
                    inicio
                )

        else:

            for linea in resultado.stdout.splitlines():

                partes = linea.split(None, 4)

                if len(partes) < 3:
                    continue

                nombre = partes[0]
                estado = partes[2]
                descripcion = partes[3] if len(partes) > 3 else "-"

                if filtro and filtro.lower() not in nombre.lower():
                    continue

                if activos and estado != "active":
                    continue

                color = "green" if estado == "active" else "red"

                tabla.add_row(
                    nombre,
                    descripcion,
                    f"[{color}]{estado}[/{color}]",
                    "-"
                )

        if not tabla.row_count:
            console.print("[yellow]No se encontraron servicios.[/yellow]")
            return

        console.print(
            Panel(
                tabla,
                title="[bold white]Linux-ToolKit | SERVICES[/bold white]",
                border_style="cyan"
            )
        )

    except subprocess.TimeoutExpired:
        console.print("[red]Tiempo de espera agotado.[/red]")

    except FileNotFoundError:
        console.print("[red]No se encuentra la herramienta necesaria.[/red]")

    except (OSError, ValueError) as error:
        console.print(
            f"[red]Error al consultar servicios: {error}[/red]",
            markup=False
        )
