#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="diabolik-archive"
SERVICE_FILE="diabolik-archive.service"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_PATH="${SCRIPT_DIR}/${SERVICE_FILE}"
SYSTEMD_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    cat <<EOF
Utilizzo: $0 {install|uninstall|start|stop|restart|status}

  install    Installa e avvia il servizio
  uninstall  Ferma e rimuove il servizio
  start      Avvia il servizio
  stop       Ferma il servizio
  restart    Riavvia il servizio
  status     Mostra lo stato del servizio
EOF
    exit 1
}

check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo -e "${RED}Questo comando richiede privilegi di root.${NC}"
        exit 1
    fi
}

do_install() {
    check_root
    echo -e "${YELLOW}Installazione servizio ${SERVICE_NAME}...${NC}"

    if [ ! -f "${SERVICE_PATH}" ]; then
        echo -e "${RED}File servizio non trovato: ${SERVICE_PATH}${NC}"
        exit 1
    fi

    cp "${SERVICE_PATH}" "${SYSTEMD_PATH}"
    systemctl daemon-reload
    systemctl enable "${SERVICE_NAME}"
    systemctl start "${SERVICE_NAME}"

    echo -e "${GREEN}Servizio installato e avviato.${NC}"
    systemctl status "${SERVICE_NAME}" --no-pager || true
}

do_uninstall() {
    check_root
    echo -e "${YELLOW}Rimozione servizio ${SERVICE_NAME}...${NC}"

    systemctl stop "${SERVICE_NAME}" 2>/dev/null || true
    systemctl disable "${SERVICE_NAME}" 2>/dev/null || true

    if [ -f "${SYSTEMD_PATH}" ]; then
        rm -f "${SYSTEMD_PATH}"
        systemctl daemon-reload
        echo -e "${GREEN}Servizio rimosso.${NC}"
    else
        echo -e "${YELLOW}Servizio non installato.${NC}"
    fi
}

do_start() {
    check_root
    echo -e "${YELLOW}Avvio ${SERVICE_NAME}...${NC}"
    systemctl start "${SERVICE_NAME}"
    echo -e "${GREEN}Servizio avviato.${NC}"
}

do_stop() {
    check_root
    echo -e "${YELLOW}Arresto ${SERVICE_NAME}...${NC}"
    systemctl stop "${SERVICE_NAME}"
    echo -e "${GREEN}Servizio fermato.${NC}"
}

do_restart() {
    check_root
    echo -e "${YELLOW}Riavvio ${SERVICE_NAME}...${NC}"
    systemctl restart "${SERVICE_NAME}"
    echo -e "${GREEN}Servizio riavviato.${NC}"
}

do_status() {
    echo -e "${YELLOW}Stato ${SERVICE_NAME}:${NC}"
    systemctl status "${SERVICE_NAME}" --no-pager || true
}

case "${1:-}" in
    install)   do_install ;;
    uninstall) do_uninstall ;;
    start)     do_start ;;
    stop)      do_stop ;;
    restart)   do_restart ;;
    status)    do_status ;;
    *)         usage ;;
esac
