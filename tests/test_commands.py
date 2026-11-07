from linux_toolkit.core.loader import CommandLoader
from linux_toolkit.core.registry import CommandRegistry


def test_cargar_definiciones():
    registro = CommandRegistry()
    loader = CommandLoader(registro)

    loader.load_commands()

    assert len(registro.get_all()) > 0


def test_comandos_principales_cargados():
    registro = CommandRegistry()
    loader = CommandLoader(registro)

    loader.load_commands()

    comandos_esperados = {
        "system",
        "disk",
        "ip",
        "ping",
        "route",
        "dns",
        "cpu",
        "ram",
        "processes",
        "services"
    }

    comandos_cargados = {
        comando.name for comando in registro.get_all()
    }

    assert comandos_esperados.issubset(comandos_cargados)


def test_todos_los_comandos_tienen_datos_validos():
    registro = CommandRegistry()
    loader = CommandLoader(registro)

    loader.load_commands()

    for comando in registro.get_all():
        assert comando.name
        assert comando.description
        assert comando.module
        assert comando.function