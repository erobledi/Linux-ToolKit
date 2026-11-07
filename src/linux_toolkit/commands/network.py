
"""
Información y diagnóstico de interfaces de red.
"""

import platform
import socket
import subprocess

import psutil

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from linux_toolkit.core.utils import (
    formatear_bytes,
    obtener_codificacion_sistema
)


console = Console()


def obtener_tipo_familia(familia) -> str:
    """Identifica el tipo de dirección de red."""

    if familia == socket.AF_INET:
        return "IPv4"

    if familia == socket.AF_INET6:
        return "IPv6"

    if hasattr(psutil, "AF_LINK") and familia == psutil.AF_LINK:
        return "MAC"

    if hasattr(socket, "AF_PACKET") and familia == socket.AF_PACKET:
        return "MAC"

    return "OTRA"


def show_ip() -> None:
    """Muestra información de las interfaces de red."""

    interfaces = psutil.net_if_addrs()
    estados = psutil.net_if_stats()
    trafico = psutil.net_io_counters(pernic=True)

    tabla = Table(
        title="Interfaces de red",
        border_style="cyan",
        show_lines=True
    )

    tabla.add_column("Interfaz", style="bold cyan")
    tabla.add_column("Estado")
    tabla.add_column("IPv4")
    tabla.add_column("IPv6")
    tabla.add_column("Máscara")
    tabla.add_column("MAC")
    tabla.add_column("Velocidad", justify="right")

    for nombre, direcciones in interfaces.items():
        ipv4 = "-"
        ipv6 = "-"
        mascara = "-"
        mac = "-"

        for direccion in direcciones:
            tipo = obtener_tipo_familia(direccion.family)

            if tipo == "IPv4":
                ipv4 = direccion.address
                mascara = direccion.netmask or "-"

            elif tipo == "IPv6":
                ipv6 = direccion.address.split("%")[0]

            elif tipo == "MAC":
                mac = direccion.address

        estado = estados.get(nombre)
        activa = estado.isup if estado else False
        velocidad = estado.speed if estado else 0

        texto_estado = (
            "[green]ACTIVA[/green]"
            if activa
            else "[red]INACTIVA[/red]"
        )

        texto_velocidad = (
            f"{velocidad} Mbps"
            if velocidad > 0
            else "-"
        )

        tabla.add_row(
            nombre,
            texto_estado,
            ipv4,
            ipv6,
            mascara,
            mac,
            texto_velocidad
        )

    console.print(
        Panel(
            tabla,
            title="[bold white]Linux-ToolKit | NETWORK[/bold white]",
            border_style="cyan"
        )
    )

    tabla_trafico = Table(
        title="Estadísticas de tráfico",
        border_style="cyan",
        show_lines=True
    )

    tabla_trafico.add_column("Interfaz", style="bold cyan")
    tabla_trafico.add_column("Bytes enviados", justify="right")
    tabla_trafico.add_column("Bytes recibidos", justify="right")

    for nombre, datos in trafico.items():
        tabla_trafico.add_row(
            nombre,
            formatear_bytes(datos.bytes_sent),
            formatear_bytes(datos.bytes_recv)
        )

    console.print(tabla_trafico)


def ping_host(host: str, count: str = "4") -> None:
    """Comprueba la conectividad con otro equipo."""

    if not host or not host.strip():
        console.print("[red]Debes indicar una IP o un dominio.[/red]")
        return

    host = host.strip()

    if host.startswith("-") or any(caracter.isspace() for caracter in host):
        console.print("[red]El destino indicado no es válido.[/red]")
        return

    try:
        cantidad = int(count)
    except ValueError:
        console.print("[red]El número de paquetes debe ser un entero.[/red]")
        return

    if not 1 <= cantidad <= 20:
        console.print(
            "[red]El número de paquetes debe estar entre 1 y 20.[/red]"
        )
        return

    if platform.system() == "Windows":
        comando = ["ping", "-n", str(cantidad), host]
    elif platform.system() == "Linux":
        comando = ["ping", "-c", str(cantidad), host]
    else:
        console.print("[red]Sistema operativo no compatible.[/red]")
        return

    console.print(
        Panel(
            f"[bold cyan]Destino:[/bold cyan] {host}\n"
            f"[bold cyan]Paquetes:[/bold cyan] {cantidad}",
            title="Diagnóstico de conectividad",
            border_style="cyan"
        )
    )

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding=obtener_codificacion_sistema(),
            errors="replace",
            timeout=max(10, cantidad * 3 + 5)
        )

        salida = resultado.stdout.strip()
        errores = resultado.stderr.strip()

        if salida:
            console.print(
                Panel(salida, title="Resultado de ping"),
                markup=False
            )

        if errores:
            console.print(errores, style="yellow", markup=False)

        if resultado.returncode == 0:
            console.print("[bold green]Conectividad correcta.[/bold green]")
        else:
            console.print(
                "[bold red]No se ha podido completar el ping correctamente.[/bold red]"
            )

    except subprocess.TimeoutExpired:
        console.print("[bold red]Tiempo de espera agotado.[/bold red]")

    except FileNotFoundError:
        console.print(
            "[bold red]No se encuentra la herramienta ping del sistema.[/bold red]"
        )

    except OSError as error:
        console.print(
            f"[bold red]Error al ejecutar ping: {error}[/bold red]",
            markup=False
        )


def show_routes() -> None:
    """Muestra la tabla de rutas del sistema."""

    sistema = platform.system()

    if sistema == "Windows":
        comando = ["route", "print", "-4"]
    elif sistema == "Linux":
        comando = ["ip", "-4", "route", "show"]
    else:
        console.print(
            "[red]Sistema operativo no compatible con esta función.[/red]"
        )
        return

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding=obtener_codificacion_sistema(),
            errors="replace",
            timeout=10
        )

        if resultado.returncode != 0:
            console.print(
                f"[red]No se pudo obtener la tabla de rutas: "
                f"{resultado.stderr.strip()}[/red]",
                markup=False
            )
            return

        salida = resultado.stdout.strip()

        if not salida:
            console.print("[yellow]No se encontraron rutas.[/yellow]")
            return

        console.print(
            Panel(
                salida,
                title="[bold white]Linux-ToolKit | ROUTE[/bold white]",
                border_style="cyan"
            ),
            markup=False
        )

    except FileNotFoundError:
        console.print(
            "[red]No se encuentra la herramienta de consulta de rutas.[/red]"
        )

    except subprocess.TimeoutExpired:
        console.print("[red]Tiempo de espera agotado.[/red]")

    except OSError as error:
        console.print(
            f"[red]Error al consultar las rutas: {error}[/red]",
            markup=False
        )


def lookup_dns(host: str) -> None:
    """Consulta la resolución DNS de un dominio."""

    if not host or not host.strip():
        console.print(
            "[red]Debes indicar un dominio o nombre de equipo.[/red]"
        )
        return

    host = host.strip()

    if host.startswith("-") or any(caracter.isspace() for caracter in host):
        console.print("[red]El destino indicado no es válido.[/red]")
        return

    if platform.system() not in ("Windows", "Linux"):
        console.print("[red]Sistema operativo no compatible.[/red]")
        return

    comando = ["nslookup", host]

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding=obtener_codificacion_sistema(),
            errors="replace",
            timeout=10
        )

        if resultado.returncode != 0:
            console.print(
                f"[red]Error en la consulta DNS: "
                f"{resultado.stderr.strip()}[/red]",
                markup=False
            )
            return

        salida = resultado.stdout.strip()

        if not salida:
            console.print(
                "[yellow]La consulta no devolvió resultados.[/yellow]"
            )
            return

        console.print(
            Panel(
                salida,
                title="[bold white]Linux-ToolKit | DNS[/bold white]",
                border_style="cyan"
            ),
            markup=False
        )

    except FileNotFoundError:
        console.print(
            "[red]No se encuentra la herramienta nslookup.[/red]"
        )

    except subprocess.TimeoutExpired:
        console.print(
            "[red]Tiempo de espera agotado en la consulta DNS.[/red]"
        )

    except OSError as error:
        console.print(
            f"[red]Error al consultar DNS: {error}[/red]",
            markup=False
        )
