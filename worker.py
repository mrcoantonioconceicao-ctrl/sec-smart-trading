import sys
import time
import random
import sqlite3
import urllib.request
import json
from datetime import datetime

DB_NAME = "sec_trading.db"

# Definição das Personas Estratégicas dos Sub-Agentes
PERSONAS = {
    "SCALPER": {
        "intervalo": 3,   # Ciclo super rápido
        "margem_min": -0.05,
        "margem_max": 1.20,
        "custo_infra": 0.01,
        "descricao": "Focado em micro-operações rápidas de alta frequência."
    },
    "TREND": {
        "intervalo": 7,   # Ciclo mais moderado
        "margem_min": -0.40,
        "margem_max": 3.50,
        "custo_infra": 0.03,
        "descricao": "Focado em capturar grandes variações de tendência."
    },
    "CONSERVATIVE": {
        "intervalo": 10,  # Ciclo lento e prudente
        "margem_min": -0.02,
        "margem_max": 0.80,
        "custo_infra": 0.005,
        "descricao": "Operações de baixo risco e preservação de capital."
    },
    "CEQUEOPS_CORE": {
        "intervalo": 5,   # Perfil estratégico personalizado
        "margem_min": -0.20,
        "margem_max": 2.50,
        "custo_infra": 0.02,
        "descricao": "Agente tático alinhado às diretrizes estruturais avançadas."
    }
}

def registrar_log_worker(nome_worker, persona, mensagem):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_msg = f"{timestamp} [{nome_worker} | {persona}] {mensagem}"
    print(log_msg)
    with open("sec_auditoria.log", "a") as f:
        f.write(f"{log_msg}\n")

def consultar_preco_binance() -> float:
    url = "https://testnet.binance.vision/api/v3/ticker/price?symbol=SOLUSDT"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return float(data["price"])
    except Exception:
        return 145.50

def determinar_persona(index: int) -> str:
    # Distribui as personas com base na ordem de criação
    chaves = list(PERSONAS.keys())
    return chaves[index % len(chaves)]

def rodar_worker(nome_worker, saldo_inicial, index_worker):
    tipo_persona = determinar_persona(index_worker)
cfg = PERSONAS[tipo_persona]
    
    saldo = saldo_inicial
    registrar_log_worker(nome_worker, tipo_persona, f"Iniciado com ${saldo:.2f}. Perfil: {cfg['descricao']}")
    
    try:
        while True:
            time.sleep(cfg["intervalo"])
            preco_sol = consultar_preco_binance()
            
            # Simulação baseada na persona estratégica
            lucro = random.uniform(cfg["margem_min"], cfg["margem_max"])
            saldo = saldo + lucro - cfg["custo_infra"]
            
            registrar_log_worker(nome_worker, tipo_persona, f"SOL: ${preco_sol:.2f} | Op: ${lucro:+.2f} | Saldo: ${saldo:.2f}")
            
            if saldo <= 3.0:
                registrar_log_worker(nome_worker, tipo_persona, "Saldo crítico esgotado. Encerrando sub-agente.")
                break
                
    except KeyboardInterrupt:
        registrar_log_worker(nome_worker, tipo_persona, "Finalizado por interrupção manual.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python worker.py <nome_do_worker>")
        sys.exit(1)
        
    nome = sys.argv[1]
    
    # Conecta ao banco para buscar dados e contar quantos workers já vieram antes (para definir a persona)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, saldo_alocado FROM sub_agentes WHERE nome = ? ORDER BY id DESC LIMIT 1", (nome,))
    row = cursor.fetchone()
    
    # Conta quantos workers existem no total para calcular a rotação de persona
    cursor.execute("SELECT COUNT(*) FROM sub_agentes")
    total_criados = cursor.fetchone()[0]
    conn.close()
    
    saldo_inicial = row[1] if row else 15.0
    index_id = (row[0] if row else total_criados) - 1
    
    rodar_worker(nome, saldo_inicial, max(0, index_id))
