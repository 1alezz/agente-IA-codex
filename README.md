# Agente de Trading Automatizado com IA (Metodologia ICT)

## Visão geral

Este projeto descreve um agente de trading automatizado para criptomoedas que combina a metodologia ICT (Inner Circle Trader) com técnicas modernas de Aprendizado por Reforço. O agente opera múltiplos ativos e timeframes em paralelo, detecta setups clássicos do ICT (Order Blocks, Liquidity Sweeps, Fair Value Gaps, etc.), avalia confluências de sinais e executa decisões autônomas de compra/venda com gestão de risco.

Toda a configuração e acompanhamento do bot é feita por um dashboard web interativo, com controle sobre ativos, risco, estratégias ativas e visualização das decisões em tempo real. O sistema inicia em paper trading usando Binance Testnet e pode ser alternado para conta real.

---

## Estratégias e sinais (Metodologia ICT)

### 1) Order Blocks (Blocos de Ordens)
Regiões de forte desequilíbrio entre oferta e demanda, definidas pelo último candle significativo antes de um movimento impulsivo. O agente detecta OBs em diferentes timeframes, marcando zonas de demanda (compra) e oferta (venda) e avaliando entradas quando o preço retorna a essas zonas.

### 2) FVG/IFVG (Fair Value Gaps / Imbalances)
Gaps de valor justo gerados por movimentos impulsivos. O agente identifica FVGs bullish e bearish e monitora o preço quando retorna à zona, tratando essas áreas como potenciais regiões de suporte/resistência.

### 3) Zonas de Liquidez e Liquidity Sweeps
Mapeia níveis de liquidez (BSL/SSL) e detecta varreduras (sweeps) de liquidez quando o preço ultrapassa um nível-chave e retorna rapidamente. Esses eventos sinalizam possíveis reversões.

### 4) Divergência de RSI
Detecta divergências bullish/bearish no RSI para antecipar perda de força da tendência. Serve como confirmação adicional junto a outros sinais.

### 5) Estrutura de Preço e Quebra de Tendência (MSS/CHOCH)
Identifica mudanças estruturais (Market Structure Shift/Change of Character) e padrões de candles (pin bars, engulfing, etc.) para confirmar reversões e entradas.

### 6) Turtle Soup (ICT)
Estratégia de reversão por rompimentos falsos (liquidity sweeps). O agente marca níveis de liquidez em timeframes maiores, espera o sweep no timeframe operacional e busca confirmação de estrutura para entrar contra o rompimento.

### 7) Médias Móveis (Filtro de Tendência)
Utiliza EMAs como filtro de tendência. Opera majoritariamente a favor da direção definida pela média móvel, reduzindo sinais contra o fluxo principal.

### 8) Confluência de sinais e alvos em Fibonacci
A execução de trades exige múltiplos sinais alinhados. Alvos podem ser definidos por retrações de Fibonacci (50%/61.8%) combinadas com zonas de liquidez.

---

## Aprendizado por Reforço (RL) e adaptação contínua

### Ambiente de Trading
O agente modela o trading como um MDP:

- **Estado (state)**: preços, indicadores, sinais ICT detectados, posição atual etc.
- **Ações (action)**: comprar, vender, fechar posição, manter.
- **Recompensa (reward)**: baseada no P&L, com opções de ajuste por risco.

### Algoritmo PPO
Utiliza Proximal Policy Optimization (PPO) via Stable-Baselines3, por sua estabilidade, capacidade de exploração e boa performance em ambientes com sequência longa de decisões.

### Exploração vs. Exploitação
A política mantém estocasticidade suficiente para continuar explorando, evitando convergência prematura. Parâmetros de entropia e ruído podem ser ajustados.

### Treinamento contínuo
O agente pode ser re-treinado periodicamente com dados novos ou ajustar sua política online (com cautela). A UI exibe métricas de treinamento para transparência.

---

## Dashboard de configuração e monitoramento

### Seleção de ativos e timeframes
Permite escolher ativos (ex: BTC/USDT, ETH/USDT) e timeframes (1m, 5m, 1h etc.).

### Parâmetros de risco
Controle de tamanho de posição, risco por trade, alavancagem, exposição máxima e trades simultâneos.

### Testnet vs. Real
Switch para alternar entre Binance Testnet e conta real. Um banner destaca o modo ativo.

### Estratégias ativáveis
Toggles para ligar/desligar módulos (OB, FVG, Liquidez, RSI, Turtle Soup, EMA).

### Logs e narrativa
Logs em tempo real descrevem detecção de sinais, confluência e execução de trades com justificativa clara.

### Painel de performance
Métricas como P&L, drawdown, profit factor, taxa de acerto, curva de capital e gráficos por período.

### Gestão de operações
Lista de posições abertas, stops/targets, P&L não realizado, com possibilidade de intervenção manual.

---

## Logging detalhado

O sistema registra:

- Detecção de sinais e contexto.
- Justificativa completa de entradas.
- Execução de ordens e possíveis erros.
- Ajustes dinâmicos (trailing stop, parciais, breakeven).
- Encerramento de posições com resultado.
- Atualizações do modelo RL.

Logs são armazenados e exibidos no dashboard com níveis de detalhe configuráveis.

---

## Backtesting e Paper Trading

### Backtest offline
Executa simulações com dados históricos (velas) para validar estratégias e parâmetros.

### Paper trading (Testnet)
Opera em tempo real sem risco financeiro usando a Binance Testnet.

### Métricas de backtest
ROI, drawdown, Sharpe, profit factor, curva de capital, trades detalhadas e comparações entre configurações.

---

## Considerações técnicas

### Linguagem e bibliotecas
- **Python 3.10+**
- **Binance SDK / ccxt**
- **Pandas, NumPy**
- **Stable-Baselines3 (PPO), PyTorch**
- **Flask/FastAPI + WebSockets**

### Arquitetura modular
- `core/agent.py`: lógica principal.
- `core/strategies.py`: detectores ICT.
- `core/environment.py`: ambiente Gym.
- `core/model.py`: treino e inferência RL.
- `web/`: dashboard e APIs.

### Execução de ordens e risco
Orquestração de ordens (market/limit/OCO), validação de saldo, proteção com stops e controle de drawdown.

### Segurança
Criptografia de chaves, logs sem dados sensíveis e preferências de acesso seguro.

---

## Testes e validação

- Testes unitários com `pytest` para sinais e cálculos de risco.
- Backtests extensivos antes de operar com capital real.
- Monitoramento contínuo de performance.

---

## Status

Este repositório descreve a visão e a arquitetura do agente. A implementação prática deve seguir a estrutura acima, com foco em modularidade, rastreabilidade e segurança.
