import sqlite3
import os
import time
from datetime import datetime

DB_NAME = "sec_trading.db"

# Mapeamento de personas para exibição limpa
PERSONAS_MAP = {
    "SCALPER": "SCALPER (Alta Freq.)",
    "TREND": "TREND (Tendência)",
    "CONSERVATIVE": "CONSERVATIVE (Prudente)",
    "CEQUEOPS_CORE": "CEQUEOPS (Tático)"
}

def limpar_tela():
    os.system('clear' if os.name == 'posix' else 'cls')

def exibir_painel():
    if not os.path.exists(DB_NAME):
        print(f"[MONITOR] Banco de dados '{DB_NAME}' não encontrado. Aguardando inicialização do Agente Pai...")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Busca estado do Pai
    cursor.execute("SELECT saldo, status, atualizado_em FROM estado WHERE id = 1")
    pai_row = cursor.fetchone()
    
    saldo_pai = pai_row[0] if pai_row else 0.0
    status_pai = pai_row[1] if pai_row else "UNKNOWN"
    atualizado_em = pai_row[2] if pai_row else "N/A"
    
    # Busca sub-agentes ativos e calcula personas com base na ordem de criação
    cursor.execute("SELECT id, nome, saldo_alocado, criado_em FROM sub_agentes WHERE status = 'ACTIVE'")
    workers = cursor.fetchall()
    total_workers = len(workers)
    
    # Busca últimas auditorias
    cursor.execute("SELECT ciclo_timestamp, saldo_atual, preco_mercado, status FROM auditoria ORDER BY id DESC LIMIT 5")
    auditorias = cursor.fetchall()
    
    conn.close()
    
    limpar_tela()
    print("=" * 78)
    print(" 🛡️ SEC SMART TRADING - PAINEL DE MONITORAMENTO MULTI-AGENTES (BINANCE TESTNET)")
    print("=" * 78)
    print(f" Data/Hora da Consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 78)
    print(f"👑 AGENTE PAI:")
    print(f"   - Saldo Atual: ${saldo_pai:.2f}                                    - Status BPMN: [{status_pai}]")
    print(f"   - Última Atualização: {atualizado_em}")
    print("=" * 78)
    print(f" 🤖 SUB-AGENTES ATIVOS (Total: {total_workers}/10):")
    print("-" * 78)
    print(f" {'ID':<4} | {'NOME DO WORKER':<22} | {'PERSONA ESTRATEGICA':<24} | {'SALDO':<8}")
    print("-" * 78)
    
    if not workers:
        print("   Nenhum sub-agente ativo no momento (Aguardando meta de escala de $70).")
    else:
        chaves_personas = list(PERSONAS_MAP.keys())
        for idx, w in enumerate(workers):
            # Recalcula a persona do worker baseada na mesma lógica do worker.py
            tipo_persona = chaves_personas[idx % len(chaves_personas)]
            nome_persona_exibicao = PERSONAS_MAP.get(tipo_persona, tipo_persona)
            print(f" {w[0]:<4} | {w[1]:<22} | {nome_persona_exibicao:<24} | ${w[2]:.2f}")
            
    print("=" * 78)
    print(" 📊 ÚLTIMOS CICLOS DE AUDITORIA (Pai):")
    print("-" * 78)
    if not auditorias:
        print("   Nenhum registro de auditoria ainda.")
    else:
        for aud in auditorias:
            print(f"   [{aud[0]}] Saldo: ${aud[1]:.2f} | SOL: ${aud[2]:.2f} | Status: {aud[3]}")
    print("=" * 78)
    print(" Pressione Ctrl+C para sair do monitor.")

if __name__ == "__main__":
    try:
        while True:
            exibir_painel()
            time.sleep(2) # Atualiza o painel a cada 2 segundos
    except KeyboardInterrupt:
        print("\nPainel de monitoramento encerrado.")
