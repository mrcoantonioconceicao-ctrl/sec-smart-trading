import os
import time
from sec_crypto import cifrar_dados, decifrar_dados

DB_ARQUIVO = "sec_orders.enc"

def guardar_ordem_segura(tipo: str, simbolo: str, preco: float, quantidade: float = 0.0):
    ordens = listar_ordens_seguras()
    nova_ordem = {
        "id": len(ordens) + 1,
        "type": tipo,
        "symbol": simbolo,
        "price": preco,
        "amount": quantidade,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "SIMULATED_SECURED"
    }
    ordens.append(nova_ordem)
    
    # Cifra toda a base de dados de ordens de uma só vez
    payload_cifrado = cifrar_dados({"orders": ordens})
    with open(DB_ARQUIVO, "wb") as f:
        f.write(payload_cifrado)
    print(f"[SEC-DB] 🔒 Ordem #{nova_ordem['id']} registada e cifrada com sucesso no cofre!")

def listar_ordens_seguras():
    if not os.path.exists(DB_ARQUIVO):
        return []
    try:
        with open(DB_ARQUIVO, "rb") as f:
            payload = f.read()
        dados = decifrar_dados(payload)
        return dados.get("orders", [])
    except Exception as e:
        print(f"[SEC-DB ERROR] Falha ao decifrar cofre: {e}")
        return []
