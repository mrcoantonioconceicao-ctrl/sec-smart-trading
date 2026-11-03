#!/bin/bash

# Script de Controle da SEC Smart Trading

CMD=$1

case "$CMD" in
    stop)
        echo "[SEC-CTL] Encerrando Agente Pai e todos os Sub-Agentes..."
        pkill -f main.py
        pkill -f worker.py
        echo "[SEC-CTL] Sistema totalmente parado com sucesso."
        ;;
    clean)
        echo "[SEC-CTL] Limpando ambiente (banco de dados e logs)..."
        pkill -f main.py
        pkill -f worker.py
        rm -f sec_trading.db
        rm -f sec_auditoria.log
        echo "[SEC-CTL] Ambiente limpo e resetado para os $50 iniciais."
        ;;
    status)
        echo "[SEC-CTL] Verificando processos ativos..."
        ps aux | grep -E "main.py|worker.py" | grep -v grep
        ;;
    *)
        echo "Uso incorreto."
        echo "Comandos disponíveis:"
        echo "  ./sec_ctl.sh stop   - Para todos os agentes em execução"
        echo "  ./sec_ctl.sh clean  - Para os agentes e reseta o banco de dados ($50)"
        echo "  ./sec_ctl.sh status - Mostra os processos ativos no sistema"
        ;;
esac
