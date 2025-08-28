# Phandas

**Phandas** is a quantitative analysis and backtesting toolkit for cryptocurrency markets, developed by **Phantom Management**.

## Features

- 🚀 **One-click data download**: Fetch crypto OHLCV data from major exchanges
- 📊 **Smart visualization**: Plot price charts (line/candlestick) with data gap detection  
- 🔍 **Data quality checks**: Comprehensive data validation and anomaly detection
- 🎯 **Special handling**: Automatic support for renamed tokens (e.g., MATIC→POL)
- ⚡ **Factor generation**: Alpha101-style factor expressions with built-in parser
- 📈 **Professional backtesting**: Complete backtesting engine with performance metrics

## Installation

```bash
pip install phandas
```

## Quick Start

```python
# phandas: Quantitative analysis for cryptocurrency markets
# Complete workflow: data -> factors -> backtest

import phandas as phn

# Step 1: Download historical OHLCV data
data = phn.fetch_and_prepare_data(['ETH', 'SOL', 'BNB', 'MATIC', 'OP', 'ARB'])

# Step 2: Generate factor values
factor_data = phn.add_factor_to_data(data, 'ts_rank(rank(low), 9)', 'alpha004_reverse')

# Step 3: Run backtest
bt = phn.Backtester(data=factor_data, factor_col='alpha004_reverse', transaction_cost=0)
bt.run_backtest()
bt.calculate_performance_metrics()
bt.summary()
bt.plot_equity_curve()
bt.plot_pnl_distribution()
```

Perfect for crypto quantitative research and strategy development! 📈
