import json
import os
import secrets
import hashlib
from datetime import datetime

WALLET_FILE = "sec_wallet.json"

def criar_ou_carregar_carteira():
    """
    Gera ou carrega uma carteira local segura para o SEC Smart Trading,
    criando chaves criptográficas e endereço público para o bot.
    """
    if os.path.exists(WALLET_FILE):
        print(f"[WALLET] A carregar carteira existente de {WALLET_FILE}...")
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    
    print(f"[WALLET] A gerar nova carteira criptográfica para o bot...")
    
    # Gera uma chave privada aleatória segura (simulando padrão Web3/Secp256k1)
    private_key_bytes = secrets.token_bytes(32)
    private_key_hex = private_key_bytes.hex()
    
    # Deriva um endereço público simulado com hash SHA256/Keccak
    public_hash = hashlib.sha256(private_key_bytes).digest()
    public_address = "0x" + hashlib.sha256(public_hash).hexdigest()[:40]
    
    wallet_data = {
        "address": public_address,
        "private_key_sig": private_key_hex[:16] + "...", # Apenas parte visível por segurança
        "network": "Binance Testnet / Multi-Chain",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "initial_balance_usdt": 50.0
    }
    
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet_data, f, indent=4)
        
    print(f"[WALLET] Carteira criada com sucesso!")
    print(f"  - Endereço: {public_address}")
    return wallet_data

if __name__ == "__main__":
    carteira = criar_ou_carregar_carteira()
    print(json.dumps(carteira, indent=2))
