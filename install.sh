
#!/usr/bin/env bash

set -Eeuo pipefail

# ==========================================
# CONFIGURACIÓN
# ==========================================

APP_NAME="Linux-ToolKit"
INSTALL_DIR="/opt/linux-toolkit"
VENV_DIR="$INSTALL_DIR/.venv"
BIN_DIR="/usr/local/bin"
COMMAND_NAME="ltk"

# ==========================================
# FUNCIONES
# ==========================================

error() {
    echo "[ERROR] $1" >&2
    exit 1
}

info() {
    echo "[INFO] $1"
}

success() {
    echo "[OK] $1"
}

# ==========================================
# COMPROBACIONES
# ==========================================

if [[ "$EUID" -ne 0 ]]; then
    error "Ejecuta el instalador con sudo: sudo ./install.sh"
fi

if [[ "$(uname -s)" != "Linux" ]]; then
    error "Este instalador solo es compatible con Linux."
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$SCRIPT_DIR" == "$INSTALL_DIR" ]]; then
    error "Ejecuta el instalador desde una copia externa del proyecto."
fi

if [[ ! -f "$SCRIPT_DIR/pyproject.toml" ]]; then
    error "No se encuentra pyproject.toml. Descarga el repositorio completo."
fi

if [[ ! -f "$SCRIPT_DIR/src/linux_toolkit/cli.py" ]]; then
    error "No se encuentra el código fuente de Linux-ToolKit."
fi

# ==========================================
# COMPROBAR PYTHON
# ==========================================

PYTHON=""

for candidato in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidato" >/dev/null 2>&1; then
        if "$candidato" -c \
            'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
            PYTHON="$candidato"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    error "Se necesita Python 3.11 o superior. Instálalo antes de continuar."
fi

VERSION=$("$PYTHON" -c \
    'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

info "Python seleccionado: $PYTHON ($VERSION)"

# ==========================================
# COMPROBAR ENTORNO VIRTUAL
# ==========================================

if ! "$PYTHON" -c "import venv" >/dev/null 2>&1; then
    error "Falta el módulo venv. En Ubuntu/Debian instala el paquete python3-venv o el paquete correspondiente a tu versión de Python."
fi

# ==========================================
# PREPARAR INSTALACIÓN
# ==========================================

info "Preparando directorio de instalación..."

rm -rf -- "$INSTALL_DIR"
install -d -o root -g root -m 755 "$INSTALL_DIR"

# ==========================================
# COPIAR PROYECTO
# ==========================================

info "Copiando archivos..."

cp -a "$SCRIPT_DIR/." "$INSTALL_DIR/"

rm -rf \
    "$INSTALL_DIR/.git" \
    "$INSTALL_DIR/.venv" \
    "$INSTALL_DIR/.idea" \
    "$INSTALL_DIR/.pytest_cache" \
    "$INSTALL_DIR/build" \
    "$INSTALL_DIR/dist"

find "$INSTALL_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +

chown -R root:root "$INSTALL_DIR"
chmod -R a+rX,go-w "$INSTALL_DIR"

# ==========================================
# CREAR ENTORNO VIRTUAL
# ==========================================

info "Creando entorno virtual..."

"$PYTHON" -m venv "$VENV_DIR"

# ==========================================
# INSTALAR DEPENDENCIAS
# ==========================================

info "Instalando Linux-ToolKit y sus dependencias..."

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install "$INSTALL_DIR"

# ==========================================
# CREAR COMANDO GLOBAL
# ==========================================

info "Registrando comando global..."

cat > "$BIN_DIR/$COMMAND_NAME" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/ltk" "\$@"
EOF

chmod 755 "$BIN_DIR/$COMMAND_NAME"
chown root:root "$BIN_DIR/$COMMAND_NAME"

# ==========================================
# FINALIZAR
# ==========================================

success "$APP_NAME se ha instalado correctamente."

echo
echo "Puedes ejecutar la aplicación con:"
echo
echo "    ltk"
echo
echo "Otros comandos:"
echo
echo "    ltk --ayuda"
echo "    ltk --version"
echo "    ltk --comandos"
echo
