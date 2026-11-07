
"""
Registro central de comandos de Linux-ToolKit.
"""

from dataclasses import dataclass


@dataclass
class CommandDefinition:
    """Representa la definición de un comando."""

    name: str
    description: str
    module: str
    function: str
    enabled: bool = True


class CommandRegistry:
    """Gestiona los comandos disponibles en Linux-ToolKit."""

    def __init__(self):
        self._commands: dict[str, CommandDefinition] = {}

    def register(self, command: CommandDefinition) -> None:
        """Registra un nuevo comando."""

        if command.name in self._commands:
            raise ValueError(
                f"El comando '{command.name}' ya está registrado."
            )

        self._commands[command.name] = command

    def get(self, name: str) -> CommandDefinition | None:
        """Obtiene un comando por su nombre."""

        return self._commands.get(name)

    def get_all(self) -> list[CommandDefinition]:
        """Devuelve todos los comandos registrados."""

        return list(self._commands.values())

    def get_enabled(self) -> list[CommandDefinition]:
        """Devuelve únicamente los comandos habilitados."""

        return [
            command
            for command in self._commands.values()
            if command.enabled
        ]

    def exists(self, name: str) -> bool:
        """Comprueba si existe un comando."""

        return name in self._commands
