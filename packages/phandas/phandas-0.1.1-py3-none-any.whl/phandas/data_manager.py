import pandas as pd
import ccxt
import time
import os
import logging
from typing import List, Optional, Dict, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEFRAME = '1d'
DEFAULT_EXCHANGE = 'binance'
EXTREME_MOVE_THRESHOLD = 0.5


def fetch_and_prepare_data(
    symbols: List[str], 
    timeframe: str = DEFAULT_TIMEFRAME, 
    start_date_str: Optional[str] = None, 
    exchange_name: str = DEFAULT_EXCHANGE, 
    output_path: Optional[str] = None,
    verbose: bool = True
) -> pd.DataFrame:
    """Fetch and prepare historical OHLCV data from cryptocurrency exchanges.
    
    This function automatically handles:
    1. Downloads data from specified exchange using ccxt (single request per symbol)
    2. Merges all symbols into a single DataFrame
    3. Handles special cases (e.g., MATIC -> POL renaming)
    4. Aligns data to common start date across all symbols
    5. Forward fills missing values for weekends/maintenance periods
    6. Optionally saves processed data to CSV
    
    Parameters
    ----------
    symbols : List[str]
        List of cryptocurrency symbols, e.g., ['BTC', 'ETH', 'SOL'].
        Automatically converted to exchange format (e.g., 'BTC/USDT').
        Special handling: 'MATIC' merges MATIC and POL historical data.
    timeframe : str, default '1d'
        Candlestick timeframe.
    start_date_str : str, optional
        Start date in 'YYYY-MM-DD' format. If None, fetches from earliest available.
    exchange_name : str, default 'binance'
        Exchange name supported by ccxt.
    output_path : str, optional
        Path to save processed data as CSV.
    verbose : bool, default True
        Enable detailed logging output.
        
    Returns
    -------
    pd.DataFrame
        MultiIndex DataFrame with ('timestamp', 'symbol') index and
        ['open', 'high', 'low', 'close', 'volume'] columns.
        
    Raises
    ------
    AttributeError
        If exchange_name is not supported by ccxt.
    ValueError
        If exchange doesn't support OHLCV data or no data downloaded.
    """
    # Configure logging level based on verbose flag
    if not verbose:
        logger.setLevel(logging.WARNING)
    
    try:
        exchange = getattr(ccxt, exchange_name)()
    except AttributeError:
        raise AttributeError(f"Exchange '{exchange_name}' not found. Please check ccxt supported exchanges.")

    if not exchange.has['fetchOHLCV']:
        raise ValueError(f"Exchange '{exchange_name}' does not support OHLCV data fetching.")
        
    since = exchange.parse8601(f'{start_date_str}T00:00:00Z') if start_date_str else None

    def download_symbol_data(symbol: str, final_symbol_name: str) -> Optional[pd.DataFrame]:
        """Download OHLCV data for a single symbol.
        
        Parameters
        ----------
        symbol : str
            Base symbol name (e.g., 'BTC')
        final_symbol_name : str
            Final symbol name to use in output data
            
        Returns
        -------
        pd.DataFrame or None
            OHLCV data or None if download failed
        """
        try:
            market_symbol = f'{symbol}/USDT'
            logger.info(f"Downloading {market_symbol}...")
            
            # Download OHLCV data
            # Most exchanges can handle large date ranges in a single request
            ohlcv = exchange.fetch_ohlcv(market_symbol, timeframe, since=since)
            
            if not ohlcv:
                logger.warning(f"No data downloaded for {market_symbol}")
                return None
                
            # Rate limiting
            time.sleep(exchange.rateLimit / 1000)

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = final_symbol_name
            return df

        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            logger.error(f"Failed to download {market_symbol}: {e}")
            return None

    def merge_renamed_symbols(original_symbol: str, new_symbol: str, unified_name: str) -> Optional[pd.DataFrame]:
        """Merge data from renamed cryptocurrency symbols.
        
        Parameters
        ----------
        original_symbol : str
            Original symbol name
        new_symbol : str
            New symbol name after renaming
        unified_name : str
            Unified name to use in output
            
        Returns
        -------
        pd.DataFrame or None
            Merged OHLCV data or None if both downloads failed
        """
        logger.info(f"Processing renamed symbol {unified_name}: {original_symbol} -> {new_symbol}")
        
        # Download data for both symbols
        original_df = download_symbol_data(original_symbol, unified_name)
        new_df = download_symbol_data(new_symbol, unified_name)
        
        if original_df is None and new_df is None:
            logger.error(f"Failed to download data for both {original_symbol} and {new_symbol}")
            return None
        elif original_df is None:
            logger.warning(f"Using only {new_symbol} data (failed to download {original_symbol})")
            return new_df
        elif new_df is None:
            logger.warning(f"Using only {original_symbol} data (failed to download {new_symbol})")
            return original_df
        
        # Merge data and handle gaps
        logger.info(f"Merging {original_symbol} and {new_symbol} data")
        
        # Find data boundary points
        original_last_date = original_df['timestamp'].max()
        new_first_date = new_df['timestamp'].min()
        
        logger.debug(f"{original_symbol} last date: {original_last_date.strftime('%Y-%m-%d')}")
        logger.debug(f"{new_symbol} start date: {new_first_date.strftime('%Y-%m-%d')}")
        
        # Handle overlaps and gaps
        if new_first_date <= original_last_date:
            # Overlapping period - prioritize new symbol data
            original_filtered = original_df[original_df['timestamp'] < new_first_date].copy()
            combined_df = pd.concat([original_filtered, new_df], ignore_index=True)
            logger.info(f"Overlap detected, prioritizing {new_symbol} data")
        else:
            # Gap exists - will be filled in unified processing stage
            gap_days = (new_first_date - original_last_date).days
            if gap_days > 1:
                logger.info(f"Gap of {gap_days-1} days detected, will be filled during processing")
            combined_df = pd.concat([original_df, new_df], ignore_index=True)
        
        # Sort by time and remove duplicates
        combined_df = combined_df.sort_values('timestamp').drop_duplicates(subset=['timestamp'], keep='last')
        
        logger.info(f"Successfully merged data: {len(combined_df)} data points")
        return combined_df

    # 定義改名映射表，便於未來擴展
    # 無論指定 MATIC 還是 POL，都會下載完整的歷史數據
    SYMBOL_RENAME_MAP = {
        'MATIC': ('MATIC', 'POL', 'MATIC'),  # (原名, 新名, 統一輸出名)
        'POL': ('MATIC', 'POL', 'MATIC'),    # POL 也觸發相同的合併邏輯
        # 未來可以在這裡添加其他改名的幣種
        # 'OLD_NAME': ('OLD_NAME', 'NEW_NAME', 'UNIFIED_NAME'),
        # 'NEW_NAME': ('OLD_NAME', 'NEW_NAME', 'UNIFIED_NAME'),
    }

    all_dfs = []
    logger.info(f"Starting data download from {exchange_name}")

    for symbol in symbols:
        if symbol in SYMBOL_RENAME_MAP:
            # Handle renamed symbols
            original_symbol, new_symbol, unified_name = SYMBOL_RENAME_MAP[symbol]
            merged_df = merge_renamed_symbols(original_symbol, new_symbol, unified_name)
            if merged_df is not None:
                all_dfs.append(merged_df)
        else:
            # Handle regular symbols
            df = download_symbol_data(symbol, symbol)
            if df is not None:
                all_dfs.append(df)

    if not all_dfs:
        raise ValueError("No data successfully downloaded, cannot proceed with processing")

    logger.info("Data download completed, starting integration and processing")
    # 3. 將所有 DataFrame 合併
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # 4. 數據對齊與填充
    # 使用 pivot_table 來將數據從 long format 轉為 wide format，以 symbol 為 columns
    # 這樣可以輕鬆地對齊和填充
    pivoted_dfs = {}
    ohlcv_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in ohlcv_columns:
        pivoted = combined_df.pivot_table(index='timestamp', columns='symbol', values=col)
        pivoted_dfs[col] = pivoted

    # Find common start date where all symbols have data
    first_valid_indices = {col: pivoted_dfs[col].apply(lambda s: s.first_valid_index()) for col in ohlcv_columns}
    common_start_date = max(series.max() for series in first_valid_indices.values())
    
    logger.info(f"Aligning data from common start date: {common_start_date.strftime('%Y-%m-%d')}")

    # Create complete date range to handle gaps
    end_date = combined_df['timestamp'].max()
    full_date_range = pd.date_range(start=common_start_date, end=end_date, freq='D')
    logger.info(f"Created complete time series: {len(full_date_range)} date points")

    # 對齊並填充
    aligned_filled_dfs = {}
    for col in ohlcv_columns:
        # 從共同起始日期開始切片
        aligned = pivoted_dfs[col][pivoted_dfs[col].index >= common_start_date]
        # 重新索引到完整日期序列，缺失日期會自動填充為 NaN
        aligned = aligned.reindex(full_date_range)
        # 向前填充缺失值
        filled = aligned.ffill()
        # 再次填充，以防第一行就有 NaN
        filled = filled.bfill()
        aligned_filled_dfs[col] = filled

    # 5. 將數據從 wide format 轉回 long format (MultiIndex)
    # 根據 pandas 新版本的建議，使用 future_stack=True 時，必須移除 dropna 參數。
    stacked_series = {col: df.stack(future_stack=True).rename(col) for col, df in aligned_filled_dfs.items()}
    final_df = pd.concat(stacked_series.values(), axis=1)
    
    # 調整索引
    final_df.index.names = ['timestamp', 'symbol']
    final_df = final_df.sort_index()

    logger.info("Data processing completed")

    # Save to file if output path provided
    if output_path:
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            final_df.to_csv(output_path)
            logger.info(f"Processed data saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise

    return final_df


def plot_price_data(
    csv_path: str, 
    plot_type: str = 'line', 
    symbols: Optional[List[str]] = None, 
    figsize: Tuple[int, int] = (15, 10), 
    save_path: Optional[str] = None,
    verbose: bool = True
) -> None:
    """Plot price data for data quality checking and visualization.
    
    Parameters
    ----------
    csv_path : str
        Path to CSV file with MultiIndex format
    plot_type : {'line', 'candlestick'}, default 'line'
        Type of plot to generate
    symbols : List[str], optional
        List of symbols to plot. If None, plots all symbols
    figsize : Tuple[int, int], default (15, 10)
        Figure size for the plot
    save_path : str, optional
        Path to save the plot image
    verbose : bool, default True
        Enable detailed logging output
        
    Raises
    ------
    FileNotFoundError
        If csv_path does not exist
    ValueError
        If plot_type is not supported
    """
    # Configure logging
    if not verbose:
        logger.setLevel(logging.WARNING)
        
    try:
        # Load data
        logger.info(f"Loading data from: {csv_path}")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"File not found: {csv_path}")
            
        # Read MultiIndex CSV
        df = pd.read_csv(csv_path, index_col=[0, 1], parse_dates=[0])
        logger.info(f"Data loaded successfully, shape: {df.shape}")
        logger.info(f"Available symbols: {list(df.index.get_level_values('symbol').unique())}")
        logger.info(f"Time range: {df.index.get_level_values('timestamp').min()} to {df.index.get_level_values('timestamp').max()}")
        
        # Check for missing values
        missing_info = df.isnull().sum()
        if missing_info.any():
            logger.info("Missing value statistics:")
            for col, count in missing_info.items():
                if count > 0:
                    logger.info(f"  {col}: {count} missing values")
        else:
            logger.info("No missing values found")
        
        # Select symbols to plot
        available_symbols = list(df.index.get_level_values('symbol').unique())
        if symbols is None:
            symbols = available_symbols
        else:
            symbols = [s for s in symbols if s in available_symbols]
            if not symbols:
                raise ValueError("None of the specified symbols found in data")
        
        logger.info(f"Preparing to plot {len(symbols)} symbols")
        
        # Set matplotlib font configuration
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        if plot_type == 'line':
            _plot_line_chart(df, symbols, figsize, save_path, verbose)
        elif plot_type == 'candlestick':
            _plot_candlestick_chart(df, symbols, figsize, save_path, verbose)
        else:
            raise ValueError(f"Unsupported plot type '{plot_type}'. Use 'line' or 'candlestick'")
            
    except Exception as e:
        logger.error(f"Plotting error: {e}")
        raise


def _plot_line_chart(df: pd.DataFrame, symbols: List[str], figsize: Tuple[int, int], save_path: Optional[str], verbose: bool) -> None:
    """Plot closing price line charts."""
    fig, axes = plt.subplots(len(symbols), 1, figsize=figsize, sharex=True)
    if len(symbols) == 1:
        axes = [axes]
    
    for i, symbol in enumerate(symbols):
        try:
            symbol_data = df.loc[df.index.get_level_values('symbol') == symbol]
            timestamps = symbol_data.index.get_level_values('timestamp')
            close_prices = symbol_data['close']
            
            axes[i].plot(timestamps, close_prices, linewidth=1.5, label=f'{symbol} Close Price')
            axes[i].set_title(f'{symbol} Price Chart', fontsize=12, fontweight='bold')
            axes[i].set_ylabel('Price (USDT)', fontsize=10)
            axes[i].grid(True, alpha=0.3)
            axes[i].legend()
            
            # 格式化x軸日期
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            axes[i].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
            # 檢查數據中斷
            time_diff = timestamps.to_series().diff()
            normal_interval = time_diff.mode().iloc[0] if not time_diff.mode().empty else pd.Timedelta(days=1)
            gaps = time_diff > normal_interval * 2
            
            if gaps.any():
                gap_dates = timestamps[gaps]
                for gap_date in gap_dates:
                    axes[i].axvline(x=gap_date, color='red', linestyle='--', alpha=0.7, linewidth=1)
                if verbose:
                    logger.info(f"{symbol}: Found {len(gap_dates)} data gaps")
            
        except Exception as e:
            logger.error(f"Error plotting {symbol}: {e}")
    
    plt.xlabel('Date', fontsize=10)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Chart saved to: {save_path}")
    
    plt.show()


def _plot_candlestick_chart(df: pd.DataFrame, symbols: List[str], figsize: Tuple[int, int], save_path: Optional[str], verbose: bool) -> None:
    """Plot simplified candlestick charts."""
    fig, axes = plt.subplots(len(symbols), 1, figsize=figsize, sharex=True)
    if len(symbols) == 1:
        axes = [axes]
    
    for i, symbol in enumerate(symbols):
        try:
            symbol_data = df.loc[df.index.get_level_values('symbol') == symbol]
            timestamps = symbol_data.index.get_level_values('timestamp')
            
            opens = symbol_data['open'].values
            highs = symbol_data['high'].values
            lows = symbol_data['low'].values
            closes = symbol_data['close'].values
            
            # 簡化的K棒圖：使用線條和顏色表示
            for j, (timestamp, o, h, l, c) in enumerate(zip(timestamps, opens, highs, lows, closes)):
                color = 'green' if c >= o else 'red'
                alpha = 0.7
                
                # 畫影線（高低點）
                axes[i].plot([timestamp, timestamp], [l, h], color='black', linewidth=0.5, alpha=0.8)
                
                # 畫實體（開收盤價）
                body_height = abs(c - o)
                bottom = min(o, c)
                
                # 使用矩形表示K棒實體
                width = pd.Timedelta(hours=12)  # K棒寬度
                rect = Rectangle((mdates.date2num(timestamp) - width.total_seconds()/(24*3600)/2, bottom), 
                               width.total_seconds()/(24*3600), body_height, 
                               facecolor=color, alpha=alpha, edgecolor='black', linewidth=0.3)
                axes[i].add_patch(rect)
            
            axes[i].set_title(f'{symbol} Candlestick Chart', fontsize=12, fontweight='bold')
            axes[i].set_ylabel('Price (USDT)', fontsize=10)
            axes[i].grid(True, alpha=0.3)
            
            # 格式化x軸
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            axes[i].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
        except Exception as e:
            logger.error(f"Error plotting candlestick for {symbol}: {e}")
    
    plt.xlabel('Date', fontsize=10)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Candlestick chart saved to: {save_path}")
    
    plt.show()


def check_data_quality(csv_path: str, detailed: bool = False, verbose: bool = True) -> Dict:
    """Check data quality including missing values, duplicates, and anomalies.
    
    Parameters
    ----------
    csv_path : str
        Path to CSV file
    detailed : bool, default False
        Whether to show detailed statistics
    verbose : bool, default True
        Enable detailed logging output
        
    Returns
    -------
    dict
        Dictionary containing data quality report
        
    Raises
    ------
    FileNotFoundError
        If csv_path does not exist
    """
    # Configure logging
    if not verbose:
        logger.setLevel(logging.WARNING)
        
    try:
        logger.info(f"Checking data quality: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"File not found: {csv_path}")
        
        df = pd.read_csv(csv_path, index_col=[0, 1], parse_dates=[0])
        
        report = {
            'file_path': csv_path,
            'total_rows': len(df),
            'symbols': list(df.index.get_level_values('symbol').unique()),
            'time_range': {
                'start': df.index.get_level_values('timestamp').min(),
                'end': df.index.get_level_values('timestamp').max()
            },
            'missing_values': {},
            'duplicates': 0,
            'anomalies': {}
        }
        
        logger.info("=== Data Quality Report ===")
        logger.info(f"File: {csv_path}")
        logger.info(f"Total rows: {report['total_rows']:,}")
        logger.info(f"Number of symbols: {len(report['symbols'])}")
        logger.info(f"Symbols: {', '.join(report['symbols'])}")
        logger.info(f"Time range: {report['time_range']['start']} to {report['time_range']['end']}")
        
        # 檢查缺失值
        missing = df.isnull().sum()
        report['missing_values'] = missing.to_dict()
        
        logger.info("--- Missing Values Check ---")
        if missing.any():
            for col, count in missing.items():
                if count > 0:
                    percentage = (count / len(df)) * 100
                    logger.info(f"{col}: {count:,} missing ({percentage:.2f}%)")
                    report['missing_values'][col] = {'count': int(count), 'percentage': percentage}
        else:
            logger.info("No missing values found")
        
        # 檢查重複值
        duplicates = df.index.duplicated().sum()
        report['duplicates'] = int(duplicates)
        logger.info("--- Duplicates Check ---")
        if duplicates > 0:
            logger.warning(f"Found {duplicates} duplicate timestamps")
        else:
            logger.info("No duplicate timestamps found")
        
        # Check for data anomalies per symbol
        logger.info("--- Data Anomalies Check ---")
        for symbol in report['symbols']:
            symbol_data = df.loc[df.index.get_level_values('symbol') == symbol]
            anomalies = {}
            
            # 檢查負價格
            negative_prices = (symbol_data[['open', 'high', 'low', 'close']] <= 0).any(axis=1).sum()
            if negative_prices > 0:
                anomalies['negative_prices'] = int(negative_prices)
            
            # 檢查異常高低價關係
            invalid_ohlc = ((symbol_data['high'] < symbol_data['low']) | 
                           (symbol_data['high'] < symbol_data['open']) |
                           (symbol_data['high'] < symbol_data['close']) |
                           (symbol_data['low'] > symbol_data['open']) |
                           (symbol_data['low'] > symbol_data['close'])).sum()
            if invalid_ohlc > 0:
                anomalies['invalid_ohlc'] = int(invalid_ohlc)
            
            # Check for extreme price movements (daily change > threshold)
            returns = symbol_data['close'].pct_change()
            extreme_moves = (abs(returns) > EXTREME_MOVE_THRESHOLD).sum()
            if extreme_moves > 0:
                anomalies['extreme_moves'] = int(extreme_moves)
            
            if anomalies:
                report['anomalies'][symbol] = anomalies
                logger.warning(f"{symbol}: Found anomalies")
                for anomaly_type, count in anomalies.items():
                    logger.warning(f"  {anomaly_type}: {count} instances")
            else:
                logger.info(f"{symbol}: No anomalies found")
        
        if detailed:
            logger.info("--- Detailed Statistics ---")
            for symbol in report['symbols']:
                symbol_data = df.loc[df.index.get_level_values('symbol') == symbol]
                logger.info(f"{symbol}:")
                logger.info(f"  Data points: {len(symbol_data):,}")
                logger.info(f"  Price range: ${symbol_data['close'].min():.4f} - ${symbol_data['close'].max():.4f}")
                logger.info(f"  Average volume: {symbol_data['volume'].mean():,.0f}")
        
        return report
        
    except Exception as e:
        logger.error(f"Error checking data quality: {e}")
        raise
