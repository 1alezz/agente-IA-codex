# MEXC SMC AI Signal Engine

Sistema modular para geração de sinais SMC/ICT com confluências, IA auxiliar e simulação de paper trading. Fase 1 foca no motor de sinais; a arquitetura já prepara a automação futura.

## Stack
- Python 3.11+
- Streamlit (dashboard)
- Pandas/Numpy
- Scikit-learn (IA auxiliar)

## Estrutura
Consulte a árvore em `mexc_smc_ai/app/` para módulos de dados, indicadores, SMC, IA, risco, engine e UI.

## Instalação
```bash
cd mexc_smc_ai
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Ou, se preferir instalar via `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Configuração
1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
2. Ajuste `config.yaml` conforme símbolos, timeframes e parâmetros de estratégia.

## Execução do motor
```bash
python -m app.main --mode engine
```

## Execução do dashboard
```bash
streamlit run app/ui/streamlit_app.py
```

## MEXC API
O cliente usa o endpoint público de candles:
- Base URL: `https://api.mexc.com`
- Endpoint: `/api/v3/klines`

Caso a MEXC altere rotas/parametrização, ajuste em `app/data/mexc_client.py`.

## Testes
```bash
pytest
```

## Observações
- Nenhuma chave é embutida no código. Use `.env`.
- O módulo `app/engine/execution.py` está pronto para integrar execução real na fase 2.
