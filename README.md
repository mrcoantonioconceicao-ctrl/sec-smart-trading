# 🛡️ SEC Smart Trading

> Sistema de trading autônomo multi-agentes de alta resiliência, projetado para operar com governança rígida, orquestração de estados e sub-agentes especializados integrados à **Binance Testnet**.

---

## 📋 Visão Geral

O **SEC Smart Trading** é um ecossistema de agentes econômicos autônomos executado nativamente em ambiente móvel (**Termux**), estruturado sob preceitos de arquitetura limpa, Domain-Driven Design (DDD), Protocolo MCP (*Model Context Protocol*) e uma Máquina de Estados BPMN. 

O projeto foca na simulação e execução controlada de estratégias de mercado em rede de testes (Testnet), garantindo automação paralela, controle estrito de capital e mitigações severas de risco operacional.

---

## 🏛️ Arquitetura do Sistema

O ecossistema divide-se em domínios isolados e desacoplados:

1. **Domain-Driven Design (DDD):** Separação clara entre infraestrutura de dados (`sec_trading.db`), regras de negócio centrais, motor de estados e execução de workers.
2. **Model Context Protocol (MCP):** Camada de ferramentas padronizadas para consulta de estado, atualização de capital e regras de escalabilidade.
3. **Máquina de Estados BPMN:** Controla o ciclo de vida global do Agente Pai através de três estados principais:
   * `ACTIVE`: Operação contínua de monitoramento e arbitragem na Binance Testnet.
   * `SCALING`: Acionada ao atingir a meta de capital, gerando novos sub-agentes paralelos.
   * `HIBERNATING`: Modo de segurança ativado automaticamente quando o capital atinge limiares críticos de risco.

---

## 🤖 Personas dos Sub-Agentes

Quando o Agente Pai atinge metas de escala, o sistema spawna processos paralelos independentes (*Workers*), cada qual assumindo uma **persona estratégica** com pesos e ciclos próprios:

| Persona | Frequência de Ciclo | Margem de Retorno (USD) | Perfil Comportamental |
| :--- | :---: | :---: | :--- |
| **`SCALPER`** | 3s | -0.05 a +1.20 | Focado em micro-operações rápidas e alta frequência. |
| **`TREND`** | 7s | -0.40 a +3.50 | Focado em capturar oscilações e tendências maiores. |
| **`CONSERVATIVE`** | 10s | -0.02 a +0.80 | Operações prudentes focadas na preservação do orçamento. |
| **`CEQUEOPS_CORE`** | 5s | -0.20 a +2.50 | Agente tático alinhado às diretrizes estruturais avançadas. |

---

## ⚙️ Regras de Negócio e Governança

* **Capital Inicial:** $50.00 (USDT Testnet).
* **Meta de Escala (`SCALING`):** $70.00 (com alocação fixa de $15.00 por sub-agente).
* **Teto Rígido de Segurança:** Máximo de **10 workers ativos simultaneamente** no ecossistema.
* **Limiar de Hibernação (`HIBERNATING`):** Ativado caso o saldo global caia para ou abaixo de $10.00.

---

## 📂 Estrutura de Ficheiros

```text
sec_smart_trading/
├── main.py          # Agente Pai, Servidor MCP, BPMN e Orquestrador Principal
├── worker.py        # Sub-agentes paralelos baseados em Personas Estratégicas
├── monitor.py       # Dashboard em tempo real para o terminal
├── sec_ctl.sh       # Script CLI de controle, limpeza e auditoria
└── .gitignore       # Regras de exclusão de bases de dados e logs locais

🚀 Guia de Instalação e Execução (Termux)
​1. Clonar o Repositório

git clone [https://github.com/SEU_UTILIZADOR/sec-smart-trading.git](https://github.com/SEU_UTILIZADOR/sec-smart-trading.git)
cd sec-smart-trading


chmod +x sec_ctl.sh


python main.py


4. Acompanhar o Painel de Monitoramento (Sessão 2)


python monitor.py


🔒 Licenciamento e Governança
​Projeto desenvolvido para fins de pesquisa em automação multi-agentes, engenharia de prompt e resiliência de sistemas distribuídos em ambientes de borda.
