
"""
Cargador de definiciones JSON de Linux-ToolKit.
"""

import json
import keyword
from pathlib import Path

from linux_toolkit.core.registry import CommandDefinition, CommandRegistry


class CommandLoader:
    """Carga las definiciones JSON y las registra."""

    def __init__(
        self,
        registry: CommandRegistry,
        definitions_dir: Path | None = None
    ):
        self.registry = registry

        self.definitions_dir = definitions_dir or (
            Path(__file__).resolve().parent.parent / "definitions"
        )

    def load_commands(self) -> int:
        """Carga todos los archivos JSON disponibles."""

        if not self.definitions_dir.exists():
            raise FileNotFoundError(
                f"No se encuentra la carpeta de definiciones: "
                f"{self.definitions_dir}"
            )

        if not self.definitions_dir.is_dir():
            raise NotADirectoryError(
                f"La ruta de definiciones no es una carpeta: "
                f"{self.definitions_dir}"
            )

        archivos = sorted(self.definitions_dir.glob("*.json"))

        if not archivos:
            return 0

        comandos = []

        for archivo in archivos:
            try:
                with archivo.open("r", encoding="utf-8-sig") as fichero:
                    datos = json.load(fichero)

                if not isinstance(datos, dict):
                    raise ValueError(
                        "La definición debe ser un objeto JSON."
                    )

                campos_obligatorios = (
                    "name",
                    "description",
                    "module",
                    "function"
                )

                for campo in campos_obligatorios:
                    if (
                        not isinstance(datos.get(campo), str)
                        or not datos[campo].strip()
                    ):
                        raise ValueError(
                            f"El campo '{campo}' es obligatorio "
                            "y debe ser texto."
                        )

                for campo in ("module", "function"):
                    valor = datos[campo]

                    if not valor.isidentifier() or keyword.iskeyword(valor):
                        raise ValueError(
                            f"El campo '{campo}' debe ser un "
                            "identificador Python válido."
                        )

                enabled = datos.get("enabled", True)

                if not isinstance(enabled, bool):
                    raise ValueError(
                        "El campo 'enabled' debe ser verdadero o falso."
                    )

                comando = CommandDefinition(
                    name=datos["name"],
                    description=datos["description"],
                    module=datos["module"],
                    function=datos["function"],
                    enabled=enabled
                )

                comandos.append(comando)

            except (json.JSONDecodeError, ValueError, KeyError) as error:
                raise ValueError(
                    f"Error en el archivo '{archivo.name}': {error}"
                ) from error

        # Comprobar duplicados antes de modificar el registro.
        nombres = [comando.name for comando in comandos]

        if len(nombres) != len(set(nombres)):
            raise ValueError(
                "Hay nombres de comandos duplicados en las definiciones."
            )

        for comando in comandos:
            if self.registry.exists(comando.name):
                raise ValueError(
                    f"El comando '{comando.name}' ya está registrado."
                )

        # Registrar únicamente cuando todas las definiciones son válidas.
        for comando in comandos:
            self.registry.register(comando)

        return len(comandos)
