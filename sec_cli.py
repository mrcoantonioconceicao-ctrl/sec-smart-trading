import sqlite3, os, time
from datetime import datetime
from sec_wallet import gerar_ou_carregar_carteira
from sec_db import listar_ordens_seguras

DB_NAME = "sec_trading.db"
CAPITAL_INICIAL = 50.0

def limpar_tela():
    os.system("clear" if os.name == "posix" else "cls")

def resetar_ambiente():
    print("\n[SEC-CTL] 🔄 A limpar o ecossistema e a reiniciar o saldo para $50.00 USD...")
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        if os.path.exists("sec_orders.enc"): os.remove("sec_orders.enc")
        if os.path.exists("sec_auditoria.log"): os.remove("sec_auditoria.log")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS estado (id INTEGER PRIMARY KEY, saldo REAL, status TEXT, atualizado_em TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS auditoria (id INTEGER PRIMARY KEY AUTOINCREMENT, ciclo_timestamp TEXT, saldo_anterior REAL, saldo_atual REAL, preco_mercado REAL, status TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS sub_agentes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, saldo_alocado REAL, status TEXT, criado_em TEXT)")
        cursor.execute("INSERT INTO estado (id, saldo, status, atualizado_em) VALUES (1, ?, 'ACTIVE', ?)", (CAPITAL_INICIAL, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        print("[SEC-CTL] ✔️ Ecossistema limpo com sucesso! Pronto para arrancar com $50.00.")
    except Exception as e:
        print(f"[SEC-CTL ERROR] Falha ao resetar ambiente: {e}")

def painel_cli():
    carteira = gerar_ou_carregar_carteira()
    while True:
        print("\n" + "=" * 65)
        print(" 🛡️ SEC SMART TRADING - PAINEL DE CONTROLO CLI (NOLAN & COFRE)")
        print("=" * 65)
        print(" [1] Consultar Identidade da Carteira (Decifrada em Memória)")
        print(" [2] Inspecionar Cofre de Ordens Cifradas (AES-256-GCM)")
        print(" [3] Consultar Estado Atual do Agente Pai (Banco SQLite)")
        print(" [4] Verificar Auditoria de Ciclos Anteriores")
        print(" [5] Monitorar Agentes em Tempo Real (Feed Binance Testnet)")
        print(" [6] Resetar Ecossistema (Zerar e Recomeçar com $50.00 USD)")
        print(" [7] Sair do Painel CLI")
        print("-" * 65)
        escolha = input(" Escolha uma opção [1-7]: ").strip()
        if escolha == "1":
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(" 🔐 [CARTEIRA SEGURA]")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f" Endereço Público : {carteira.get('address')}")
            print(f" Rede Configurada : {carteira.get('network')}")
            print(f" Estado do Cofre  : {carteira.get('status')}")
            input("\nPressione Enter para voltar ao menu...")
        elif escolha == "2":
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(" 📂 [COFRE DE ORDENS ENCRIPTADAS]")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            ordens = listar_ordens_seguras()
            if not ordens: print(" O cofre está vazio ou sem registos encriptados.")
            else:
                for o in ordens: print(f" ID #{o['id']} | [{o['type']}] {o['symbol']} @ ${o['price']} (Valor: ${o.get('amount', 0):.2f}) | Status: {o['status']}")
            input("\nPressione Enter para voltar ao menu...")
        elif escolha == "3":
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(" 👑 [ESTADO DO AGENTE PAI]")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            if not os.path.exists(DB_NAME): print(" Base de dados ainda não inicializada.")
            else:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT saldo, status, atualizado_em FROM estado WHERE id = 1")
                row = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) FROM sub_agentes WHERE status = 'ACTIVE'")
                total_workers = cursor.fetchone()[0]
                conn.close()
                if row:
                    print(f" Saldo Atual em Caixa : ${row[0]:.2f} USD")
                    print(f" Status BPMN          : [{row[1]}]")
                    print(f" Sub-Agentes Ativos   : {total_workers}/10")
                    print(f" Última Atualização   : {row[2]}")
            input("\nPressione Enter para voltar ao menu...")
        elif escolha == "4":
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(" 📊 [AUDITORIA RECENTE]")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            if not os.path.exists(DB_NAME): print(" Base de dados não encontrada.")
            else:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT ciclo_timestamp, saldo_atual, preco_mercado, status FROM auditoria ORDER BY id DESC LIMIT 5")
                auditorias = cursor.fetchall()
                conn.close()
                for aud in auditorias: print(f" [{aud[0]}] Saldo: ${aud[1]:.2f} | SOL: ${aud[2]:.2f} | Status: {aud[3]}")
            input("\nPressione Enter para voltar ao menu...")
        elif escolha == "5":
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(" 🚀 [MODO DE MONITORAMENTO EM TEMPO REAL]")
            print(" Pressione Ctrl+C a qualquer momento para voltar ao menu.")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            time.sleep(1.5)
            try:
                while True:
                    limpar_tela()
                    print("=" * 65)
                    print(" 🟢 MONITOR EM TEMPO REAL (Pressione Ctrl+C para sair)")
                    print("=" * 65)
                    if os.path.exists(DB_NAME):
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("SELECT saldo, status, atualizado_em FROM estado WHERE id = 1")
                        pai = cursor.fetchone()
                        cursor.execute("SELECT ciclo_timestamp, saldo_atual, preco_mercado, status FROM auditoria ORDER BY id DESC LIMIT 1")
                        ultima_aud = cursor.fetchone()
                        conn.close()
                        if pai: print(f" Saldo Pai: ${pai[0]:.2f} USD | Status: [{pai[1]}]")
                        if ultima_aud: print(" Último Ciclo [", ultima_aud[0], "]: SOL @ $", f"{ultima_aud[2]:.2f}", " ert{} Saldo: $", f"{ultima_aud[1]:.2f}", sep="")
                        else: print(" Aguardando ciclos do Agente Pai...")
                    else: print(" Base de dados pendente de criação...")
                    print("=" * 65)
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\n Saindo do monitor...")
                time.sleep(1)
        elif escolha == "6":
            if input(" Tem certeza que deseja zerar e reiniciar com $50.00? [s/N]: ").strip().lower() == "s":
                resetar_ambiente()
            input("\nPressione Enter para voltar ao menu...")
        elif escolha == "7":
            print("\n A sair do Painel CLI. Até breve!")
            break

if __name__ == "__main__":
    painel_cli()
