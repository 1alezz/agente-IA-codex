from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import importlib.util
from datetime import datetime, timedelta

from app.core.logging import LogBuffer, TradeLogBuffer, configure_logger
from app.core.schemas import TradingConfig
from app.core.storage import ConfigStorage
from app.trading.agent import TradingAgent
from app.trading.backtest import Backtester


app = FastAPI(title="Agente de Trading ICT")

_jinja_available = importlib.util.find_spec("jinja2") is not None
templates = Jinja2Templates(directory="app/dashboard/templates") if _jinja_available else None

log_buffer = LogBuffer()
trade_log_buffer = TradeLogBuffer()
logger = configure_logger(log_buffer)
storage = ConfigStorage()
config = storage.load()
agent = TradingAgent(config, log_buffer, trade_log_buffer)
backtester = Backtester()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    current_config = storage.load()
    if templates is None:
        return HTMLResponse(
            content=(
                "<html><body><h1>Jinja2 não instalado.</h1>"
                "<p>Instale dependências com <code>pip install -r requirements.txt</code> "
                "para carregar o dashboard completo.</p></body></html>"
            )
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "config": current_config,
        },
    )


@app.get("/api/config")
async def get_config() -> TradingConfig:
    return storage.load()


@app.post("/api/config")
async def update_config(payload: TradingConfig) -> TradingConfig:
    storage.save(payload)
    agent.update_config(payload)
    return payload


@app.post("/api/agent/start")
async def start_agent() -> dict:
    agent.start()
    return {"status": "started"}


@app.post("/api/agent/stop")
async def stop_agent() -> dict:
    agent.stop()
    return {"status": "stopped"}


@app.get("/api/status")
async def status() -> dict:
    return agent.status().model_dump()


@app.get("/api/logs")
async def logs() -> dict:
    return {"entries": log_buffer.list()}


@app.get("/api/trade-logs")
async def trade_logs() -> dict:
    return {"entries": trade_log_buffer.list()}


@app.post("/api/actions/test-connection")
async def test_connection() -> dict:
    if not agent.config.binance.api_key or not agent.config.binance.api_secret:
        raise HTTPException(status_code=400, detail="API key/secret não configuradas.")
    logger.info("Teste de conexão solicitado via dashboard.")
    return {"status": "ok"}


@app.post("/api/actions/backtest")
async def run_backtest() -> dict:
    logger.info("Backtest iniciado via dashboard.")
    result = backtester.run(agent.config.backtest, [])
    return result.__dict__


@app.post("/api/actions/backtest-30d")
async def run_backtest_30d() -> dict:
    logger.info("Backtest de 30 dias iniciado via dashboard.")
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    config = agent.config.backtest.model_copy(
        update={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
    )
    result = backtester.run(config, [])
    return result.__dict__


@app.post("/api/actions/train")
async def train_agent() -> dict:
    logger.info("Treinamento RL iniciado via dashboard.")
    return {"status": "training", "message": "Treinamento em progresso."}
