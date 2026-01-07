from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class StrategyToggles(BaseModel):
    order_blocks: bool = True
    fvg: bool = True
    liquidity_sweeps: bool = True
    rsi_divergence: bool = True
    market_structure: bool = True
    turtle_soup: bool = True
    moving_average_filter: bool = True
    fibonacci_targets: bool = True


class RiskConfig(BaseModel):
    risk_per_trade_pct: float = Field(2.0, ge=0.1, le=10.0)
    max_daily_drawdown_pct: float = Field(8.0, ge=1.0, le=50.0)
    max_consecutive_losses: int = Field(4, ge=1, le=20)
    max_exposure_per_asset_pct: float = Field(15.0, ge=1.0, le=100.0)
    leverage: float = Field(1.0, ge=1.0, le=50.0)


class AssetConfig(BaseModel):
    symbol: str
    timeframes: List[str] = Field(default_factory=lambda: ["5m", "1h"])


class BinanceConfig(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    use_testnet: bool = True


class BacktestConfig(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = Field(10000.0, ge=100.0)
    slippage_pct: float = Field(0.02, ge=0.0, le=1.0)


class RLConfig(BaseModel):
    algorithm: str = "PPO"
    train_interval_minutes: int = Field(60, ge=5, le=1440)
    exploration_rate: float = Field(0.1, ge=0.0, le=1.0)


class DashboardConfig(BaseModel):
    log_level: str = "INFO"
    refresh_seconds: int = Field(5, ge=1, le=60)


class TradingConfig(BaseModel):
    assets: List[AssetConfig] = Field(
        default_factory=lambda: [AssetConfig(symbol="BTCUSDT"), AssetConfig(symbol="ETHUSDT")]
    )
    strategies: StrategyToggles = Field(default_factory=StrategyToggles)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    binance: BinanceConfig = Field(default_factory=BinanceConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    rl: RLConfig = Field(default_factory=RLConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)


class StrategySignal(BaseModel):
    name: str
    direction: str
    confidence: float
    context: Dict[str, str] = Field(default_factory=dict)


class AgentDecision(BaseModel):
    symbol: str
    timeframe: str
    action: str
    reason: str
    signals: List[StrategySignal] = Field(default_factory=list)


class PositionSnapshot(BaseModel):
    symbol: str
    side: str
    entry_price: float
    stop_loss: float
    take_profit: float
    unrealized_pnl: float
    duration_minutes: int


class PerformanceSnapshot(BaseModel):
    total_pnl_usd: float
    win_rate_pct: float
    profit_factor: float
    max_drawdown_pct: float
    trades: int


class AgentStatus(BaseModel):
    running: bool
    mode: str
    last_decisions: List[AgentDecision] = Field(default_factory=list)
    performance: PerformanceSnapshot
    positions: List[PositionSnapshot] = Field(default_factory=list)
