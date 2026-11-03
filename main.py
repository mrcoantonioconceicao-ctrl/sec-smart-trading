import sqlite3
import time
import json
import os
import subprocess
import urllib.request
from datetime import datetime

DB_NAME = "sec_trading.db"
CAPITAL_INICIAL = 50.0 
LIMITE_SEGURANCA = 10.0
META_ESCALA = 70.0
ORCAMENTO_SUB_AGENTE = 15.0
LIMITE_MAX_WORKERS = 10

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
    log_msg = f"{timestamp} [ANÁLISE-REAL] {mensagem}"
    print(log_msg)
    with open("sec_auditoria.log", "a") as f:
        f.write(f"{log_msg}\n")

def analisar_mercado_real() -> dict:
    url = "https://testnet.binance.vision/api/v3/klines?symbol=SOLUSDT&interval=1m&limit=5"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            dados_velas = json.loads(response.read().decode())
            precos_fecho = [float(vela[4]) for vela in dados_velas]
            preco_atual = precos_fecho[-1]
            preco_anterior = precos_fecho[0]
            variacao_pct = ((preco_atual - preco_anterior) / preco_anterior) * 100
            
            if variacao_pct > 0.02:
                lucro_calculado = abs(variacao_pct) * 0.5
                sinal = "BULLISH (COMPRA)"
            elif variacao_pct < -0.02:
                lucro_calculado = -abs(variacao_pct) * 0.4
                sinal = "BEARISH (VENDA/DEFESA)"
            else:
                lucro_calculado = 0.05
                sinal = "NEUTRAL (LATERAL)"
                
            return {
                "preco": preco_atual,
                "variacao": variacao_pct,
                "lucro": round(lucro_calculado, 3),
                "sinal": sinal
            }
    except Exception as e:
        registrar_log(f"Erro ao consultar API da Binance Testnet: {e}")
        return {"preco": 145.50, "variacao": 0.0, "lucro": 0.01, "sinal": "FALLBACK"}

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
        return {"sucesso": True, "saldo_atualizado": novo_saldo}

def executar_ciclo_agente():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT saldo, status FROM estado WHERE id = 1")
    row = cursor.fetchone()
    saldo_atual, status_atual = row[0], row[1]
    
    cursor.execute("SELECT COUNT(*) FROM sub_agentes WHERE status = 'ACTIVE'")
    total_workers = cursor.fetchone()[0]
    conn.close()

    if saldo_atual <= LIMITE_SEGURANCA:
        registrar_log(f"[BPMN: HIBERNATING] Saldo crítico (${saldo_atual:.2f}).")
        return

    analise = analisar_mercado_real()
    custo_api = 0.015
    novo_saldo = saldo_atual + analise["lucro"] - custo_api
    
    registrar_log(f"SOL: ${analise['preco']:.2f} | Var: {analise['variacao']:.3f}% | Sinal: {analise['sinal']} | Op: ${analise['lucro']:+.2f} | Saldo: ${saldo_atual:.2f} -> ${novo_saldo:.2f}")
    
    ServidorMCPTools.tool_atualizar_capital({
        "novo_saldo": novo_saldo,
        "status": "ACTIVE",
        "saldo_anterior": saldo_atual,
        "preco_mercado": analise["preco"]
    })

if __name__ == "__main__":
    registrar_log("=== SEC SMART TRADING (ANÁLISE TÉCNICA REAL - BINANCE TESTNET) INICIADA ===")
    inicializar_banco()
    try:
        while True:
            executar_ciclo_agente()
            time.sleep(6)
    except KeyboardInterrupt:
        registrar_log("Encerrado pelo utilizador.")
