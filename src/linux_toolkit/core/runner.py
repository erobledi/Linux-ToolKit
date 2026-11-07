
"""
Ejecutor de comandos de Linux-ToolKit.
"""

import importlib
import keyword
from types import ModuleType, FunctionType

from linux_toolkit.core.registry import CommandRegistry


class CommandRunner:
    """Localiza y ejecuta las funciones asociadas a los comandos."""

    def __init__(self, registry: CommandRegistry):
        self.registry = registry

    def execute(self, name: str, *args, **kwargs):
        """
        Ejecuta un comando registrado.

        Args:
            name: Nombre del comando.
            *args: Argumentos posicionales para la función.
            **kwargs: Argumentos con nombre para la función.

        Returns:
            El resultado de la función ejecutada.
        """

        # Comprobar que el comando existe.
        command = self.registry.get(name)

        if command is None:
            raise ValueError(
                f"El comando '{name}' no existe."
            )

        # Comprobar que está habilitado.
        if not command.enabled:
            raise RuntimeError(
                f"El comando '{name}' está deshabilitado."
            )

        # Validar los nombres del módulo y de la función.
        for campo, valor in (
            ("módulo", command.module),
            ("función", command.function)
        ):
            if not valor.isidentifier() or keyword.iskeyword(valor):
                raise ValueError(
                    f"Nombre de {campo} no válido: '{valor}'."
                )

        # Importar el módulo correspondiente.
        ruta_modulo = f"linux_toolkit.commands.{command.module}"

        try:
            modulo: ModuleType = importlib.import_module(ruta_modulo)

        except ModuleNotFoundError as error:
            raise ImportError(
                f"No se encuentra el módulo del comando "
                f"'{name}': {ruta_modulo}"
            ) from error

        # Localizar la función.
        funcion = getattr(modulo, command.function, None)

        if not isinstance(funcion, FunctionType):
            raise AttributeError(
                f"No se encuentra una función válida llamada "
                f"'{command.function}' en el módulo '{ruta_modulo}'."
            )

        # Ejecutar la función.
        return funcion(*args, **kwargs)
