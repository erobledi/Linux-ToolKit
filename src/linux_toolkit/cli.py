
"""
Punto de entrada principal de Linux-ToolKit.
"""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from linux_toolkit.core.loader import CommandLoader
from linux_toolkit.core.registry import CommandRegistry
from linux_toolkit.core.runner import CommandRunner


VERSION = "1.0.1"

console = Console()


class ArgumentParserES(argparse.ArgumentParser):
    """Adaptación de argparse para mostrar los mensajes en español."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._positionals.title = "Argumentos"
        self._optionals.title = "Opciones"

    def error(self, message):
        """Muestra los errores de argumentos en español."""

        self.print_usage()
        self.exit(2, f"Error en los argumentos: {message}\n")


def mostrar_inicio() -> None:
    """Muestra la pantalla principal."""

    contenido = (
        "[bold cyan]Linux-ToolKit[/bold cyan]\n"
        "[dim]Kit de herramientas para administración de sistemas Linux[/dim]\n\n"
        "[green]Núcleo iniciado correctamente.[/green]"
    )

    console.print(
        Panel(
            contenido,
            title="[bold white]Bienvenido[/bold white]",
            border_style="cyan",
            padding=(1, 3)
        )
    )


def crear_registro() -> CommandRegistry:
    """Carga las definiciones y crea el registro de comandos."""

    registro = CommandRegistry()
    cargador = CommandLoader(registro)
    cargador.load_commands()

    return registro


def mostrar_comandos(registro: CommandRegistry) -> None:
    """Muestra los comandos disponibles."""

    comandos = registro.get_enabled()

    if not comandos:
        console.print(
            "[yellow]No hay comandos disponibles.[/yellow]"
        )
        return

    tabla = Table(
        title="Comandos disponibles",
        border_style="cyan",
        show_lines=True
    )

    tabla.add_column("Comando", style="bold cyan")
    tabla.add_column("Descripción", style="white")

    for comando in sorted(comandos, key=lambda item: item.name):
        tabla.add_row(comando.name, comando.description)

    console.print(tabla)


def crear_parser() -> ArgumentParserES:
    """Configura los argumentos de la aplicación."""

    parser = ArgumentParserES(
        prog="ltk",
        description="Kit de herramientas para administración de sistemas Linux",
        add_help=False,
        allow_abbrev=False
    )

    parser.add_argument(
        "-h", "--ayuda",
        action="help",
        help="Muestra este mensaje de ayuda y termina"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Linux-ToolKit versión {VERSION}",
        help="Muestra la versión instalada"
    )

    parser.add_argument(
        "--comandos",
        action="store_true",
        help="Muestra los comandos disponibles"
    )

    parser.add_argument(
        "comando",
        nargs="?",
        help="Comando que se desea ejecutar"
    )

    parser.add_argument(
        "argumentos",
        nargs=argparse.REMAINDER,
        help="Argumentos adicionales del comando"
    )

    return parser


def main() -> None:
    """Función principal de Linux-ToolKit."""

    parser = crear_parser()
    argumentos = parser.parse_args()

    # Cargar el registro de comandos.
    try:
        registro = crear_registro()

    except (OSError, ValueError) as error:
        console.print(
            f"[bold red]Error al cargar los comandos:[/bold red] {error}",
            markup=False
        )
        sys.exit(1)

    # Mostrar los comandos disponibles.
    if argumentos.comandos:
        mostrar_comandos(registro)
        return

    # Mostrar la pantalla principal.
    if argumentos.comando is None:
        mostrar_inicio()
        mostrar_comandos(registro)
        return

    # Ejecutar el comando solicitado.
    ejecutor = CommandRunner(registro)

    try:
        resultado = ejecutor.execute(
            argumentos.comando,
            *argumentos.argumentos
        )

        if resultado is not None:
            console.print(resultado)

    except (ValueError, RuntimeError, ImportError, AttributeError) as error:
        console.print(
            f"[bold red]Error:[/bold red] {error}",
            markup=False
        )
        sys.exit(1)


if __name__ == "__main__":
    main()