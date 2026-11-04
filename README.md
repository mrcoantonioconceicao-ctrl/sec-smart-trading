# 🛡️ SEC Smart Trading — Nolan & Sub-Agentes (Binance Testnet)

Ecossistema de trading autônomo baseado em agentes inteligentes, projetado com uma camada robusta de **Segurança Criptográfica em Repouso (AES-256-GCM + PBKDF2)**, operando de forma totalmente isolada e sem expor dados sensíveis em *plaintext*.

---

## 🏗️ Arquitetura do Ecossistema

O projeto combina inteligência autônoma de mercado com blindagem de dados de nível corporativo:

1. **Agente Pai (Nolan)**: Orquestra o ecossistema contábil, inicia com o capital base de **$50.00 USD**, consome feeds da Binance Testnet (`SOL/USDT`) e gere a escalabilidade da equipa de sub-agentes.
2. **Sub-Agentes Semânticos**: Cada sub-agente opera com contextos dedicados (Scout, Risk Guardian, Vault e analistas táticos), expandindo-se de forma controlada até ao teto estipulado de **10 sub-agentes**.
3. **Cofre Cifrado (Vault)**: Persistência transacional protegida por criptografia autenticada. Nenhuma ordem ou estado contábil é gravado sem blindagem prévia.

---

## 📂 Componentes Principais

* **`main.py`**: Motor principal de execução autônoma, consultas à API da Binance Testnet e integração contínua com o cofre de segurança.
* **`sec_cli.py`**: Painel de controlo interativo em CLI com 7 opções avançadas (identidade da carteira, inspeção de cofre cifrado, estado do agente, auditoria, monitoramento em tempo real e reset contábil para $50.00).
* **`sec_crypto.py`**: Módulo criptográfico central utilizando **AES-256-GCM** com derivação de chave **PBKDF2HMAC** (100.000 iterações e salt fixo/dinâmico).
* **`sec_wallet.py`**: Gestão e autocura de identidades de carteira protegidas (`sec_wallet.json`), capaz de detetar chaves incompatíveis e regenerar cofres limpos automaticamente.
* **`sec_db.py`**: Base de dados de ordens e histórico encriptada (`sec_orders.enc`).
* **`monitor.py`**: Painel secundário de observabilidade em tempo real.
* **`sec_ctl.sh`**: Script Bash para gestão rápida de processos (`stop`, `clean`, `status`).

---

## 🚀 Como Executar o Projeto no Termux

### 1. Inspecionar o Ecossistema via Painel CLI
O painel centralizado permite gerir toda a simulação de forma interativa:
```bash
python sec_cli.py
python main.py
./sec_ctl.sh clean
📊 Regras de Negócio e Segurança
​Zero Plaintext: Todos os ficheiros de estado e histórico de ordens (sec_wallet.json, sec_orders.enc) são gravados estritamente sob cifra AEAD.
​Resiliência de Cofre: Mecanismo de autocura integrado para evitar que alterações de chave corrompam o ambiente de testes.
​Escalabilidade Monetária: O capital inicial de $50.00 evolui ciclicamente com base nas variações de mercado em tempo real.
