# Phandas

**Phandas** is a simple cryptocurrency data fetching and visualization toolkit, developed by **Phantom Management**.

## Features

- 🚀 **One-click data download**: Fetch crypto OHLCV data from major exchanges
- 📊 **Smart visualization**: Plot price charts (line/candlestick) with data gap detection  
- 🔍 **Data quality checks**: Comprehensive data validation and anomaly detection
- 🎯 **Special handling**: Automatic support for renamed tokens (e.g., MATIC→POL)

## Installation

```bash
pip install phandas
```

## Quick Start

```python
import phandas as phn  # 建議使用 phn 作為別名

# 1. Download data
phn.fetch_and_prepare_data(['BTC', 'ETH', 'SOL'], output_path='crypto_data.csv')

# 2. Check data quality  
phn.check_data_quality('crypto_data.csv')

# 3. Plot line chart
phn.plot_price_data('crypto_data.csv')

# 4. Plot candlestick chart
phn.plot_price_data('crypto_data.csv', plot_type='candlestick')
```

Perfect for crypto data analysis and research! 📈
