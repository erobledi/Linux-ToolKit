import pytest

from linux_toolkit.core.registry import CommandDefinition, CommandRegistry


def crear_comando(nombre="system", enabled=True):
    return CommandDefinition(
        name=nombre,
        description="Comando de prueba",
        module="system",
        function="show_system",
        enabled=enabled
    )


def test_registrar_comando():
    registro = CommandRegistry()
    comando = crear_comando()

    registro.register(comando)

    assert registro.exists("system")
    assert registro.get("system") == comando


def test_obtener_comando_inexistente():
    registro = CommandRegistry()

    assert registro.get("inexistente") is None


def test_rechazar_comandos_duplicados():
    registro = CommandRegistry()

    registro.register(crear_comando())

    with pytest.raises(ValueError):
        registro.register(crear_comando())


def test_obtener_comandos_habilitados():
    registro = CommandRegistry()

    registro.register(crear_comando("system", True))
    registro.register(crear_comando("disk", False))

    habilitados = registro.get_enabled()

    assert len(habilitados) == 1
    assert habilitados[0].name == "system"