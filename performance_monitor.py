"""
Performance monitoring and reporting for Enhanced Solana Trading Desktop
Tracks trades, calculates metrics, and generates comprehensive reports
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from pathlib import Path
import aiosqlite

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Individual trade record"""
    id: str
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL, STAKE, LEND
    platform: str
    amount: float
    price: float
    value: float
    tx_signature: str
    success: bool
    profit_loss: Optional[float] = None
    fees: float = 0.0
    metadata: Dict = field(default_factory=dict)

@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    
    total_volume: float = 0.0
    total_fees: float = 0.0
    
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0
    
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    best_trade: Optional[Trade] = None
    worst_trade: Optional[Trade] = None
    
    by_platform: Dict[str, Dict] = field(default_factory=dict)
    by_symbol: Dict[str, Dict] = field(default_factory=dict)
    by_strategy: Dict[str, Dict] = field(default_factory=dict)

class PerformanceMonitor:
    """Monitor and analyze trading performance"""
    
    def __init__(self, db_path: str = "trading_performance.db"):
        self.db_path = db_path
        self.current_session_trades: List[Trade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.initial_balance: float = 0.0
        
    async def initialize(self):
        """Initialize database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    symbol TEXT,
                    action TEXT,
                    platform TEXT,
                    amount REAL,
                    price REAL,
                    value REAL,
                    tx_signature TEXT,
                    success INTEGER,
                    profit_loss REAL,
                    fees REAL,
                    metadata TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS equity_curve (
                    timestamp TEXT PRIMARY KEY,
                    balance REAL,
                    session_pnl REAL,
                    total_pnl REAL
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS daily_summary (
                    date TEXT PRIMARY KEY,
                    trades_count INTEGER,
                    volume REAL,
                    gross_profit REAL,
                    gross_loss REAL,
                    net_profit REAL,
                    fees REAL,
                    win_rate REAL
                )
            """)
            
            await db.commit()
    
    async def record_trade(self, trade: Trade):
        """Record a new trade"""
        self.current_session_trades.append(trade)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.id,
                trade.timestamp.isoformat(),
                trade.symbol,
                trade.action,
                trade.platform,
                trade.amount,
                trade.price,
                trade.value,
                trade.tx_signature,
                int(trade.success),
                trade.profit_loss,
                trade.fees,
                json.dumps(trade.metadata)
            ))
            await db.commit()
        
        logger.info(f"Recorded trade: {trade.symbol} {trade.action} on {trade.platform}")
    
    async def update_equity_curve(self, current_balance: float):
        """Update equity curve"""
        timestamp = datetime.now()
        session_pnl = current_balance - self.initial_balance
        
        # Calculate total PnL from all trades
        total_pnl = sum(t.profit_loss or 0 for t in self.current_session_trades)
        
        self.equity_curve.append((timestamp, current_balance))
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO equity_curve VALUES (?, ?, ?, ?)
            """, (
                timestamp.isoformat(),
                current_balance,
                session_pnl,
                total_pnl
            ))
            await db.commit()
    
    async def calculate_metrics(self, period: str = "all") -> PerformanceMetrics:
        """Calculate performance metrics for specified period"""
        metrics = PerformanceMetrics()
        
        # Determine date range
        end_date = datetime.now()
        if period == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:  # all
            start_date = datetime.min
        
        async with aiosqlite.connect(self.db_path) as db:
            # Fetch trades for period
            async with db.execute("""
                SELECT * FROM trades 
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp
            """, (start_date.isoformat(), end_date.isoformat())) as cursor:
                
                trades = []
                async for row in cursor:
                    trade = Trade(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        symbol=row[2],
                        action=row[3],
                        platform=row[4],
                        amount=row[5],
                        price=row[6],
                        value=row[7],
                        tx_signature=row[8],
                        success=bool(row[9]),
                        profit_loss=row[10],
                        fees=row[11],
                        metadata=json.loads(row[12])
                    )
                    trades.append(trade)
        
        if not trades:
            return metrics
        
        # Basic metrics
        metrics.total_trades = len(trades)
        metrics.successful_trades = sum(1 for t in trades if t.success)
        metrics.failed_trades = metrics.total_trades - metrics.successful_trades
        
        if metrics.successful_trades > 0:
            metrics.win_rate = metrics.successful_trades / metrics.total_trades
        
        # Financial metrics
        for trade in trades:
            if trade.success:
                metrics.total_volume += trade.value
                metrics.total_fees += trade.fees
                
                if trade.profit_loss:
                    if trade.profit_loss > 0:
                        metrics.gross_profit += trade.profit_loss
                    else:
                        metrics.gross_loss += abs(trade.profit_loss)
        
        metrics.net_profit = metrics.gross_profit - metrics.gross_loss - metrics.total_fees
        
        # Profit factor
        if metrics.gross_loss > 0:
            metrics.profit_factor = metrics.gross_profit / metrics.gross_loss
        
        # Best/worst trades
        profitable_trades = [t for t in trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in trades if t.profit_loss and t.profit_loss < 0]
        
        if profitable_trades:
            metrics.best_trade = max(profitable_trades, key=lambda t: t.profit_loss)
        if losing_trades:
            metrics.worst_trade = min(losing_trades, key=lambda t: t.profit_loss)
        
        # Platform breakdown
        for trade in trades:
            if trade.platform not in metrics.by_platform:
                metrics.by_platform[trade.platform] = {
                    "trades": 0,
                    "volume": 0,
                    "profit_loss": 0,
                    "win_rate": 0
                }
            
            platform_stats = metrics.by_platform[trade.platform]
            platform_stats["trades"] += 1
            platform_stats["volume"] += trade.value
            if trade.profit_loss:
                platform_stats["profit_loss"] += trade.profit_loss
        
        # Symbol breakdown
        for trade in trades:
            if trade.symbol not in metrics.by_symbol:
                metrics.by_symbol[trade.symbol] = {
                    "trades": 0,
                    "volume": 0,
                    "profit_loss": 0,
                    "win_rate": 0
                }
            
            symbol_stats = metrics.by_symbol[trade.symbol]
            symbol_stats["trades"] += 1
            symbol_stats["volume"] += trade.value
            if trade.profit_loss:
                symbol_stats["profit_loss"] += trade.profit_loss
        
        # Calculate advanced metrics
        metrics = await self._calculate_advanced_metrics(metrics, trades)
        
        return metrics
    
    async def _calculate_advanced_metrics(self, metrics: PerformanceMetrics, trades: List[Trade]) -> PerformanceMetrics:
        """Calculate advanced performance metrics"""
        
        # Sharpe ratio calculation
        if len(trades) > 1:
            returns = []
            for i in range(1, len(trades)):
                if trades[i].profit_loss and trades[i-1].value > 0:
                    return_pct = trades[i].profit_loss / trades[i-1].value
                    returns.append(return_pct)
            
            if returns:
                returns_array = np.array(returns)
                if len(returns_array) > 0 and returns_array.std() > 0:
                    # Annualized Sharpe ratio (assuming 365 trading days)
                    metrics.sharpe_ratio = (returns_array.mean() * np.sqrt(365)) / returns_array.std()
        
        # Maximum drawdown calculation
        equity_curve = [0.0]
        cumulative_pnl = 0.0
        
        for trade in trades:
            if trade.profit_loss:
                cumulative_pnl += trade.profit_loss
                equity_curve.append(cumulative_pnl)
        
        if len(equity_curve) > 1:
            equity_array = np.array(equity_curve)
            running_max = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - running_max) / np.maximum(running_max, 1)
            metrics.max_drawdown = abs(drawdown.min())
        
        return metrics
    
    async def generate_report(self, period: str = "all") -> str:
        """Generate a comprehensive performance report"""
        metrics = await self.calculate_metrics(period)
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          SOLANA TRADING DESKTOP PERFORMANCE REPORT           ║
╚══════════════════════════════════════════════════════════════╝

📅 Period: {period.upper()}
📊 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════════════════════
📈 OVERVIEW
═══════════════════════════════════════════════════════════════
Total Trades:        {metrics.total_trades:,}
Successful Trades:   {metrics.successful_trades:,}
Failed Trades:       {metrics.failed_trades:,}
Win Rate:           {metrics.win_rate:.1%}

═══════════════════════════════════════════════════════════════
💰 FINANCIAL PERFORMANCE
═══════════════════════════════════════════════════════════════
Total Volume:       {metrics.total_volume:,.4f} SOL
Gross Profit:       +{metrics.gross_profit:,.4f} SOL
Gross Loss:         -{metrics.gross_loss:,.4f} SOL
Total Fees:         -{metrics.total_fees:,.4f} SOL
Net Profit/Loss:    {metrics.net_profit:+,.4f} SOL

═══════════════════════════════════════════════════════════════
📊 RISK METRICS
═══════════════════════════════════════════════════════════════
Profit Factor:      {metrics.profit_factor:.2f}
Sharpe Ratio:       {metrics.sharpe_ratio:.2f}
Max Drawdown:       {metrics.max_drawdown:.1%}
"""

        # Best/Worst trades
        if metrics.best_trade:
            report += f"""
═══════════════════════════════════════════════════════════════
🏆 BEST TRADE
═══════════════════════════════════════════════════════════════
Symbol:     {metrics.best_trade.symbol}
Platform:   {metrics.best_trade.platform}
P&L:        +{metrics.best_trade.profit_loss:,.4f} SOL
Date:       {metrics.best_trade.timestamp.strftime('%Y-%m-%d %H:%M')}
"""

        if metrics.worst_trade:
            report += f"""
═══════════════════════════════════════════════════════════════
😰 WORST TRADE
═══════════════════════════════════════════════════════════════
Symbol:     {metrics.worst_trade.symbol}
Platform:   {metrics.worst_trade.platform}
P&L:        {metrics.worst_trade.profit_loss:,.4f} SOL
Date:       {metrics.worst_trade.timestamp.strftime('%Y-%m-%d %H:%M')}
"""

        # Platform breakdown
        if metrics.by_platform:
            report += """
═══════════════════════════════════════════════════════════════
🔄 PLATFORM BREAKDOWN
═══════════════════════════════════════════════════════════════
"""
            for platform, stats in sorted(metrics.by_platform.items(), 
                                         key=lambda x: x[1]["profit_loss"], 
                                         reverse=True):
                report += f"""
{platform.upper()}:
  Trades: {stats['trades']:,}
  Volume: {stats['volume']:,.2f} SOL
  P&L:    {stats['profit_loss']:+,.4f} SOL
"""

        # Top symbols
        if metrics.by_symbol:
            report += """
═══════════════════════════════════════════════════════════════
🪙 TOP SYMBOLS
═══════════════════════════════════════════════════════════════
"""
            top_symbols = sorted(metrics.by_symbol.items(), 
                               key=lambda x: x[1]["profit_loss"], 
                               reverse=True)[:5]
            
            for symbol, stats in top_symbols:
                report += f"""
{symbol}:
  Trades: {stats['trades']:,}
  P&L:    {stats['profit_loss']:+,.4f} SOL
"""

        report += """
═══════════════════════════════════════════════════════════════
"""

        return report
    
    async def export_to_csv(self, filename: str = "trading_history.csv"):
        """Export trading history to CSV"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM trades ORDER BY timestamp") as cursor:
                rows = await cursor.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=[
            'id', 'timestamp', 'symbol', 'action', 'platform',
            'amount', 'price', 'value', 'tx_signature', 'success',
            'profit_loss', 'fees', 'metadata'
        ])
        
        # Clean up data
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['success'] = df['success'].astype(bool)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(df)} trades to {filename}")
    
    async def plot_equity_curve(self):
        """Generate equity curve plot (requires matplotlib)"""
        try:
            import matplotlib.pyplot as plt
            
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT timestamp, balance FROM equity_curve 
                    ORDER BY timestamp
                """) as cursor:
                    data = await cursor.fetchall()
            
            if not data:
                logger.warning("No equity curve data to plot")
                return
            
            timestamps = [datetime.fromisoformat(d[0]) for d in data]
            balances = [d[1] for d in data]
            
            plt.figure(figsize=(12, 6))
            plt.plot(timestamps, balances, 'b-', linewidth=2)
            plt.title('Equity Curve - Solana Trading Desktop')
            plt.xlabel('Date')
            plt.ylabel('Balance (SOL)')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filename = f"equity_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename)
            plt.close()
            
            logger.info(f"Saved equity curve plot to {filename}")
            
        except ImportError:
            logger.warning("matplotlib not installed - cannot generate plots")

async def main():
    """Run performance analysis"""
    monitor = PerformanceMonitor()
    await monitor.initialize()
    
    # Generate reports for different periods
    for period in ["today", "week", "month", "all"]:
        print(f"\n{'='*60}")
        print(f"GENERATING {period.upper()} REPORT")
        print('='*60)
        
        report = await monitor.generate_report(period)
        print(report)
        
        # Save to file
        filename = f"performance_report_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {filename}")
    
    # Export to CSV
    await monitor.export_to_csv()
    
    # Try to generate equity curve
    await monitor.plot_equity_curve()
    
    print("\n✅ Performance analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())
