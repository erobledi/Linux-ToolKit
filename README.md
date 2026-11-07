# Linux-ToolKit

**Kit de herramientas visual para la administración de sistemas Linux desde la terminal.**

Linux-ToolKit (`ltk`) reúne diferentes herramientas de consulta y diagnóstico del sistema en una interfaz de terminal clara y organizada.

Su objetivo es facilitar las tareas habituales de administración, mostrando información del equipo, almacenamiento, red y servicios del sistema.

## Características

- Interfaz de terminal mediante [Rich](https://github.com/Textualize/rich).
- Consulta de información del sistema.
- Monitorización de CPU, memoria y procesos.
- Información de discos y particiones.
- Diagnóstico y consulta de red.
- Consulta de servicios del sistema.
- Arquitectura modular basada en definiciones JSON.
- Instalación global mediante un único comando: `ltk`.

## Requisitos

- Linux.
- Python 3.11 o superior.
- Módulo `venv` de Python.
- Conexión a Internet durante la instalación para descargar las dependencias.

## Instalación

Clona el repositorio:

    git clone https://github.com/erobledi/Linux-ToolKit.git

Accede al directorio:

    cd Linux-ToolKit

Ejecuta el instalador:

    sudo bash install.sh

El instalador prepara la aplicación en `/opt/linux-toolkit`, crea un entorno virtual independiente, instala las dependencias y registra el comando global `ltk`.

## Uso

Para iniciar Linux-ToolKit:

    ltk

Mostrar la ayuda:

    ltk --ayuda

Mostrar la versión:

    ltk --version

Mostrar los comandos disponibles:

    ltk --comandos

## Comandos disponibles

| Comando | Descripción |
|---|---|
| `system` | Información general del sistema. |
| `disk` | Información de discos y particiones. |
| `ip` | Información de interfaces de red. |
| `ping` | Comprobación de conectividad. |
| `route` | Consulta de la tabla de rutas. |
| `dns` | Consulta de resolución DNS. |
| `cpu` | Información y monitorización del procesador. |
| `ram` | Información de memoria RAM y Swap. |
| `processes` | Consulta de procesos en ejecución. |
| `services` | Consulta de servicios del sistema. |

Para consultar los comandos disponibles en tu instalación:

    ltk --comandos

## Desinstalación

Desde el directorio del repositorio, ejecuta:

    sudo bash uninstall.sh

La desinstalación elimina:

- `/opt/linux-toolkit`
- `/usr/local/bin/ltk`

No elimina Python ni las dependencias instaladas fuera del entorno virtual de la aplicación.

## Desarrollo

Para trabajar en el proyecto, clona el repositorio y crea un entorno virtual:

    python3 -m venv .venv

Activa el entorno virtual:

    source .venv/bin/activate

Instala el proyecto en modo desarrollo:

    python -m pip install -e .

Instala las herramientas de pruebas:

    python -m pip install pytest

Ejecuta las pruebas:

    python -m pytest -v

## Estructura del proyecto

    Linux-ToolKit/
    ├── src/
    │   └── linux_toolkit/
    │       ├── commands/
    │       ├── core/
    │       └── definitions/
    ├── tests/
    ├── install.sh
    ├── uninstall.sh
    ├── pyproject.toml
    ├── README.md
    └── LICENSE

## Dependencias

- [Rich](https://github.com/Textualize/rich): interfaz visual de terminal.
- [psutil](https://github.com/giampaolo/psutil): información y monitorización de recursos del sistema.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para conocer sus condiciones.

## Autor

**erobledi**

Repositorio: https://github.com/erobledi/Linux-ToolKit