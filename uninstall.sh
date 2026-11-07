
#!/usr/bin/env bash

set -Eeuo pipefail

# ==========================================
# CONFIGURACIÓN
# ==========================================

APP_NAME="Linux-ToolKit"
INSTALL_DIR="/opt/linux-toolkit"
COMMAND_PATH="/usr/local/bin/ltk"

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
    error "Ejecuta el desinstalador con sudo: sudo ./uninstall.sh"
fi

if [[ ! -d "$INSTALL_DIR" && ! -e "$COMMAND_PATH" ]]; then
    error "$APP_NAME no parece estar instalado."
fi

# ==========================================
# CONFIRMACIÓN
# ==========================================

echo
echo "Se va a desinstalar $APP_NAME."
echo
echo "Se eliminarán:"
echo "  - $INSTALL_DIR"
echo "  - $COMMAND_PATH"
echo
read -r -p "¿Deseas continuar? [s/N]: " respuesta

case "$respuesta" in
    [sS]|[sS][iI])
        ;;
    *)
        info "Desinstalación cancelada."
        exit 0
        ;;
esac

# ==========================================
# ELIMINAR INSTALACIÓN
# ==========================================

if [[ -d "$INSTALL_DIR" ]]; then
    info "Eliminando archivos de instalación..."
    rm -rf -- "$INSTALL_DIR"
fi

if [[ -e "$COMMAND_PATH" || -L "$COMMAND_PATH" ]]; then
    info "Eliminando comando global..."
    rm -f -- "$COMMAND_PATH"
fi

# ==========================================
# FINALIZAR
# ==========================================

success "$APP_NAME se ha desinstalado correctamente."
