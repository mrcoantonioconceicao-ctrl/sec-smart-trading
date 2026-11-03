import sqlite3
import time
import json
import os
import subprocess
import random
import urllib.request
from datetime import datetime

# ==========================================
# DOMÍNIO 1: CONFIGURAÇÕES E INFRAESTRUTURA
# ==========================================
DB_NAME = "sec_trading.db"
CAPITAL_INICIAL = 50.0 # Em dólares (USDT Testnet)
LIMITE_SEGURANCA = 10.0
META_ESCALA = 70.0
ORCAMENTO_SUB_AGENTE = 15.0
LIMITE_MAX_WORKERS = 10 # TETO RÍGIDO

def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS estado (
                        id INTEGER PRIMARY KEY, 
                        saldo REAL, 
                        status TEXT,
                        atualizado_em TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS auditoria (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ciclo_timestamp TEXT,
                        saldo_anterior REAL,
                        saldo_atual REAL,
                        preco_mercado REAL,
                        status TEXT)''')
                        
    cursor.execute('''CREATE TABLE IF NOT EXISTS sub_agentes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        saldo_alocado REAL,
                        status TEXT,
                        criado_em TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM estado WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO estado (id, saldo, status, atualizado_em) VALUES (1, ?, 'ACTIVE', ?)", 
                       (CAPITAL_INICIAL, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    conn.close()

def registrar_log(mensagem):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_msg = f"{timestamp} [PAI-BINANCE] {mensagem}"
    print(log_msg)
    with open("sec_auditoria.log", "a") as f:
        f.write(f"{log_msg}\n")

# ==========================================
# DOMÍNIO 2: SERVIDOR MCP (Com Blindagem de Teto)
# ==========================================
class ServidorMCPTools:
    
    @staticmethod
    def tool_obter_estado(params: dict) -> dict:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT saldo, status FROM estado WHERE id = 1")
        row = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM sub_agentes WHERE status = 'ACTIVE'")
        total_workers = cursor.fetchone()[0]
        
        conn.close()
        return {"saldo": row[0], "status": row[1], "total_workers": total_workers}

    @staticmethod
    def tool_atualizar_capital(params: dict) -> dict:
        novo_saldo = params.get("novo_saldo")
        novo_status = params.get("status")
        saldo_anterior = params.get("saldo_anterior")
        preco_mercado = params.get("preco_mercado", 0.0)
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE estado SET saldo = ?, status = ?, atualizado_em = ? WHERE id = 1", 
                       (novo_saldo, novo_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        cursor.execute('''INSERT INTO auditoria (ciclo_timestamp, saldo_anterior, saldo_atual, preco_mercado, status) 
                          VALUES (?, ?, ?, ?, ?)''',
                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), saldo_anterior, novo_saldo, preco_mercado, novo_status))
        
        conn.commit()
        conn.close()
        return {"sucesso": True, "saldo_atualizado": novo_saldo, "status_atualizado": novo_status}

    @staticmethod
    def tool_escalar_sub_agente(params: dict) -> dict:
        saldo_pai_atual = params.get("saldo_pai")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sub_agentes WHERE status = 'ACTIVE'")
        total_workers_real = cursor.fetchone()[0]
        
        if total_workers_real >= LIMITE_MAX_WORKERS:
            conn.close()
            return {"sucesso": False, "motivo": f"TETO ATINGIDO: Já existem {total_workers_real} workers ativos (Máx: {LIMITE_MAX_WORKERS})."}
            
        if saldo_pai_atual < ORCAMENTO_SUB_AGENTE:
            conn.close()
            return {"sucesso": False, "motivo": "Saldo insuficiente para alocar novo sub-agente."}
            
        novo_saldo_pai = saldo_pai_atual - ORCAMENTO_SUB_AGENTE
        nome_filho = f"SEC_Binance_Worker_{int(time.time())}"
        
        cursor.execute("UPDATE estado SET saldo = ?, status = ?, atualizado_em = ? WHERE id = 1", 
                       (novo_saldo_pai, "ACTIVE", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                       
        cursor.execute('''INSERT INTO sub_agentes (nome, saldo_alocado, status, criado_em) 
                          VALUES (?, ?, ?, ?)''',
                       (nome_filho, ORCAMENTO_SUB_AGENTE, "ACTIVE", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        
        return {
            "sucesso": True, 
            "novo_saldo_pai": novo_saldo_pai, 
            "sub_agente_criado": nome_filho,
            "capital_alocado": ORCAMENTO_SUB_AGENTE
        }

def executar_mcp_tool(tool_name: str, arguments: dict) -> str:
    ferramentas = {
        "obter_estado": ServidorMCPTools.tool_obter_estado,
        "atualizar_capital": ServidorMCPTools.tool_atualizar_capital,
        "escalar_sub_agente": ServidorMCPTools.tool_escalar_sub_agente
    }
    
    if tool_name not in ferramentas:
        return json.dumps({"erro": f"Tool '{tool_name}' não encontrada no protocolo MCP da SEC Smart Trading."})
    
    resultado = ferramentas[tool_name](arguments)
    return json.dumps(resultado)

# ==========================================
# DOMÍNIO 3: INTEGRAÇÃO COM BINANCE TESTNET API
# ==========================================
def consultar_preco_binance() -> float:
    """
    Busca o preço real do par SOL/USDT diretamente na API pública da Binance Testnet.
    """
    url = "https://testnet.binance.vision/api/v3/ticker/price?symbol=SOLUSDT"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return float(data["price"])
    except Exception as e:
        registrar_log(f"[AVISO] Falha ao consultar Binance Testnet: {e}. Usando fallback.")
        return 145.50

# ==========================================
# DOMÍNIO 4: MÁQUINA DE ESTADOS BPMN
# ==========================================
class BPMNStateMachine:
    def __init__(self, saldo: float, status_atual: str, total_workers: int):
        self.saldo = saldo
        self.status_atual = status_atual
        self.total_workers = total_workers

    def avaliar_gateway_decisao(self) -> str:
        if self.saldo <= LIMITE_SEGURANCA:
            return "HIBERNATING"
        if self.saldo >= META_ESCALA:
            if self.total_workers >= LIMITE_MAX_WORKERS:
                return "ACTIVE"
            return "SCALING"
        if self.status_atual == "HIBERNATING" and self.saldo > LIMITE_SEGURANCA:
            return "ACTIVE"
        return "ACTIVE"

# ==========================================
# DOMÍNIO 5: CICLO DE VIDA DA SEC SMART TRADING
# ==========================================
def executar_ciclo_agente():
    estado = json.loads(executar_mcp_tool("obter_estado", {}))
    saldo_atual = estado["saldo"]
    status_atual = estado["status"]
    total_workers = estado["total_workers"]
    
    bpmn = BPMNStateMachine(saldo_atual, status_atual, total_workers)
    proximo_status = bpmn.avaliar_gateway_decisao()
    
    if proximo_status == 'HIBERNATING':
        registrar_log(f"[BPMN: HIBERNATING] Saldo crítico (${saldo_atual:.2f}). Congelando Agente Pai.")
        executar_mcp_tool("atualizar_capital", {"novo_saldo": saldo_atual, "status": "HIBERNATING", "saldo_anterior": saldo_atual})
        return

    if proximo_status == 'SCALING':
        registrar_log(f"[BPMN: SCALING] Meta atingida! Saldo: ${saldo_atual:.2f} | Workers: {total_workers}/{LIMITE_MAX_WORKERS}. Escalando...")
        
        resultado_escala = json.loads(executar_mcp_tool("escalar_sub_agente", {"saldo_pai": saldo_atual}))
        
        if resultado_escala.get("sucesso"):
            novo_pai = resultado_escala["novo_saldo_pai"]
            filho = resultado_escala["sub_agente_criado"]
            registrar_log(f"[SUCESSO DE ESCALA] Sub-agente '{filho}' alocado. Saldo do Pai: ${novo_pai:.2f}.")
        else:
            registrar_log(f"[BLOQUEIO DE SEGURANÇA] {resultado_escala.get('motivo')}")
        return

    # Execução Ativa consultando Binance Testnet
    preco_sol = consultar_preco_binance()
    lucro_arbitragem = random.uniform(-0.15, 5.00) # Simulação controlada de ganho/perda de arbitragem
    custo_api = 0.02
    
    novo_saldo = saldo_atual + lucro_arbitragem - custo_api
    
    registrar_log(f"[ATIVO] SOL/USDT Binance: ${preco_sol:.2f} | Workers: {total_workers}/{LIMITE_MAX_WORKERS} | Op: ${lucro_arbitragem:+.2f} | Saldo: ${saldo_atual:.2f} -> ${novo_saldo:.2f}")
    
    executar_mcp_tool("atualizar_capital", {
        "novo_saldo": novo_saldo, 
        "status": "ACTIVE", 
        "saldo_anterior": saldo_atual,
        "preco_mercado": preco_sol
    })

if __name__ == "__main__":
    registrar_log("=== SEC SMART TRADING (BINANCE TESTNET MODE) INICIADA ===")
    inicializar_banco()
    
    try:
        while True:
            executar_ciclo_agente()
            time.sleep(5)
    except KeyboardInterrupt:
        registrar_log("Sistema interrompido manualmente pelo usuário.")
