import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional, List
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_INITIAL_CAPITAL = 100000
DEFAULT_RISK_FREE_RATE = 0.0
DEFAULT_PERIODS_PER_YEAR = 365
DEFAULT_HIST_BINS = 50

# Configure matplotlib to avoid font issues
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['font.size'] = 10
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans', 'sans-serif']

# Set matplotlib backend to avoid potential GUI issues
import matplotlib
matplotlib.use('TkAgg')

# Additional font configuration to handle any encoding issues
import locale
try:
    locale.setlocale(locale.LC_ALL, 'C')
except:
    pass

class Backtester:
    def __init__(
        self, 
        csv_path: Optional[str] = None, 
        data: Optional[pd.DataFrame] = None, 
        factor_col: Optional[str] = None,
        transaction_cost: float = 0.001,  # 0.1% default (0.05% open + 0.05% close)
        verbose: bool = False  # Default to quiet for cleaner quickstart
    ):
        """Initialize the backtesting engine.
        
        Parameters
        ----------
        csv_path : str, optional
            Path to CSV file containing price and factor data
        data : pd.DataFrame, optional
            Direct DataFrame input (for backward compatibility)
        factor_col : str, optional
            Name of factor column to backtest
        verbose : bool, default True
            Enable detailed logging output
            
        Raises
        ------
        FileNotFoundError
            If csv_path does not exist
        ValueError
            If required data or columns are missing
        """
        # Configure logging
        self.verbose = verbose
        if not verbose:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.INFO)
        # Load data
        if csv_path is not None:
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
            logger.info(f"Loading data from '{csv_path}'")
            self.data = pd.read_csv(csv_path, index_col=['timestamp', 'symbol'], parse_dates=['timestamp'])
            logger.info("Data loaded successfully")
            
        elif data is not None:
            # Backward compatibility
            if not isinstance(data.index, pd.MultiIndex) or data.index.names != ['timestamp', 'symbol']:
                raise ValueError("Data must be MultiIndex DataFrame with index ('timestamp', 'symbol')")
            self.data = data.copy()
        else:
            raise ValueError("Must provide either csv_path or data parameter")
        
        # Sort data
        self.data = self.data.sort_index()
        
        # Check required columns
        required_cols = ['open', 'close']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Set factor column
        if factor_col is None:
            # Auto-select first non-price column as factor
            price_cols = ['open', 'high', 'low', 'close', 'volume']
            factor_cols = [col for col in self.data.columns if col not in price_cols]
            if not factor_cols:
                raise ValueError("No factor columns found")
            factor_col = factor_cols[0]
            logger.info(f"Auto-selected factor: {factor_col}")
        
        if factor_col not in self.data.columns:
            raise ValueError(f"Factor column not found: '{factor_col}'")
        
        self.factor_col = factor_col
        
        # Get all trading symbols
        self.symbols = list(self.data.index.get_level_values('symbol').unique())
        logger.info(f"Trading symbols: {self.symbols}")
        
        # Set transaction cost
        self.transaction_cost = transaction_cost
        logger.info(f"Transaction cost: {transaction_cost:.3%}")
        
        # Initialize result variables
        self.daily_pnl = pd.Series(dtype=float)
        self.equity_curve = pd.Series(dtype=float)
        self.daily_positions = pd.DataFrame()
        self.performance_metrics = {}

    def run_backtest(self, initial_capital: float = DEFAULT_INITIAL_CAPITAL) -> None:
        """Execute simplified backtesting strategy.
        
        Strategy Logic:
        1. Find first date with valid factor values
        2. Daily rebalancing based on previous day's factor values
        3. Factor weighting: (factor_value - mean) / sum_of_absolute_factors
        4. Enter at open prices, calculate PnL at close prices
        
        Parameters
        ----------
        initial_capital : float, default 100000
            Initial capital for backtesting
        """
        logger.info(f"Starting backtest for factor: {self.factor_col}")
        
        # Find all valid trading dates
        dates = sorted(self.data.index.get_level_values('timestamp').unique())
        
        # Find first date where all symbols have factor values
        start_date_idx = None
        for i, date in enumerate(dates):
            date_data = self.data.loc[date]
            if not date_data[self.factor_col].isna().any():
                start_date_idx = i
                break
        
        if start_date_idx is None:
            raise ValueError("No valid factor data found")
        
        if start_date_idx >= len(dates) - 1:
            raise ValueError("Insufficient data for backtesting")
        
        logger.info(f"First valid factor date: {dates[start_date_idx]}")
        logger.info(f"Backtest start date: {dates[start_date_idx + 1]}")
        
        # 初始化結果
        daily_pnl_list = []
        equity_value = initial_capital
        
        # 從第二個有效日期開始回測（因為需要前一日因子值）
        for i in range(start_date_idx + 1, len(dates)):
            current_date = dates[i]
            prev_date = dates[i - 1]
            
            try:
                # Get previous day's factor values and current day's prices
                prev_factors = self.data.loc[prev_date][self.factor_col]
                current_prices = self.data.loc[current_date]
                
                # Check price data completeness
                if current_prices[['open', 'close']].isna().any().any():
                    logger.warning(f"Incomplete price data for {current_date}, skipping")
                    continue
                
                # Handle NaN in factor data: only keep symbols with valid factor values
                valid_factors_mask = prev_factors.notna()
                if not valid_factors_mask.any():
                    logger.warning(f"No valid factor values for {current_date}, skipping")
                    continue
                
                # Use only symbols with valid factor values
                valid_factors = prev_factors[valid_factors_mask]
                valid_prices = current_prices.loc[valid_factors_mask]
                
                # Calculate positions based on previous day's valid factor values
                positions = self._calculate_positions(valid_factors)
                
                # Calculate daily return (enter at open, settle at close)
                daily_return = self._calculate_daily_return(positions, valid_prices)
                daily_pnl = equity_value * daily_return
                
                # Update equity
                equity_value += daily_pnl
                daily_pnl_list.append({
                    'date': current_date,
                    'pnl': daily_pnl,
                    'equity': equity_value,
                    'return': daily_return
                })
                
            except Exception as e:
                logger.warning(f"Calculation failed for {current_date}: {e}")
                continue
        
        # Convert to Series
        if daily_pnl_list:
            pnl_df = pd.DataFrame(daily_pnl_list)
            self.daily_pnl = pd.Series(pnl_df['pnl'].values, index=pnl_df['date'])
            self.equity_curve = pd.Series(pnl_df['equity'].values, index=pnl_df['date'])
            
            # Add initial capital at the beginning
            start_equity = pd.Series([initial_capital], index=[pnl_df['date'].iloc[0] - pd.DateOffset(days=1)])
            self.equity_curve = pd.concat([start_equity, self.equity_curve])
            
            logger.info(f"Backtest completed with {len(self.daily_pnl)} trading days")
        else:
            logger.warning("No valid backtest results generated")
            self.daily_pnl = pd.Series(dtype=float)
            self.equity_curve = pd.Series([initial_capital], index=[dates[0]])
    
    def _calculate_positions(self, factors: pd.Series) -> pd.Series:
        """Calculate positions based on factor values using pure factor weighting.
        
        Parameters
        ----------
        factors : pd.Series
            Factor values for each symbol on the given date
            
        Returns
        -------
        pd.Series
            Position weights for each symbol (dollar neutral)
        """
        # Calculate factor mean
        factor_mean = factors.mean()
        
        # Demean factors
        demeaned_factors = factors - factor_mean
        
        # Calculate sum of absolute factor values
        abs_sum = np.abs(demeaned_factors).sum()
        
        # Avoid division by zero
        if abs_sum == 0:
            positions = pd.Series(0.0, index=factors.index)
        else:
            # Factor weighting: (factor_value - mean) / sum_of_absolute_factors
            positions = demeaned_factors / abs_sum
        
        return positions
    
    def _calculate_daily_return(self, positions: pd.Series, prices: pd.DataFrame) -> float:
        """Calculate daily strategy return with transaction costs.
        
        Parameters
        ----------
        positions : pd.Series
            Position weights for each symbol
        prices : pd.DataFrame
            Price data for the current day (contains open, close)
            
        Returns
        -------
        float
            Daily strategy return after transaction costs
        """
        # Calculate individual symbol returns (close/open - 1)
        symbol_returns = (prices['close'] / prices['open']) - 1
        
        # Portfolio return = weighted average of symbol returns
        portfolio_return = (positions * symbol_returns).sum()
        
        # Apply transaction cost (每日重新平衡產生的手續費)
        # 每天重新配倉都會產生固定的交易成本
        portfolio_return_after_cost = portfolio_return - self.transaction_cost
        
        return portfolio_return_after_cost
        
    def calculate_performance_metrics(
        self, 
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE, 
        periods_per_year: int = DEFAULT_PERIODS_PER_YEAR
    ) -> None:
        """Calculate comprehensive performance metrics for the strategy.
        
        Parameters
        ----------
        risk_free_rate : float, default 0.0
            Risk-free rate for Sharpe ratio calculation
        periods_per_year : int, default 365
            Number of periods per year for annualization
        """
        logger.info("Calculating performance metrics")
        if self.equity_curve.empty or len(self.equity_curve) < 2:
            logger.error("Insufficient equity curve data for performance calculation")
            self.performance_metrics = {
                "total_return": 0, "annualized_return": 0, "annualized_volatility": 0,
                "sharpe_ratio": 0, "max_drawdown": 0, "calmar_ratio": 0,
            }
            return

        total_return = (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]) - 1
        
        num_days = (self.equity_curve.index[-1] - self.equity_curve.index[0]).days
        if num_days == 0: 
            num_days = 1  # Avoid division by zero
        annualized_return = (1 + total_return)**(periods_per_year / num_days) - 1

        daily_returns = self.equity_curve.pct_change().dropna()
        if daily_returns.empty:
            annualized_volatility = 0
            sharpe_ratio = 0
        else:
            annualized_volatility = daily_returns.std() * np.sqrt(periods_per_year)
            sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility if annualized_volatility != 0 else 0

        roll_max = self.equity_curve.expanding(min_periods=1).max()
        daily_drawdown = self.equity_curve / roll_max - 1.0
        max_drawdown = daily_drawdown.min()
        
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0

        self.performance_metrics = {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "annualized_volatility": annualized_volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "calmar_ratio": calmar_ratio,
        }
        if self.verbose:
            logger.info("Performance metrics calculated successfully")
            for metric, value in self.performance_metrics.items():
                logger.info(f"  {metric}: {value:.4f}")

    def plot_equity_curve(self, title: Optional[str] = None) -> None:
        """Plot the equity curve.
        
        Parameters
        ----------
        title : str, optional
            Title for the plot. If None, auto-generates based on factor name
        """
        if title is None:
            title = f"Equity Curve ({self.factor_col})"
            
        if self.equity_curve.empty:
            logger.error("Equity curve is empty, cannot plot")
            return

        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            # Fallback if seaborn style is not available
            plt.style.use('default')
        
        fig, ax = plt.subplots(figsize=(14, 7))
        self.equity_curve.plot(ax=ax, title=title, legend=False, color='blue', linewidth=1.5)
        ax.set_xlabel("Date")
        ax.set_ylabel("Equity Value")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        # Try to show the plot, with fallback
        try:
            plt.show()
        except Exception as e:
            logger.warning(f"Could not display equity curve: {e}")
            # Save plot instead
            try:
                plot_path = f'equity_curve_{self.factor_col}.png'
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                logger.info(f"Equity curve saved to: {plot_path}")
            except Exception as save_e:
                logger.error(f"Could not save equity curve: {save_e}")
        finally:
            plt.close()

    def plot_pnl_distribution(self, title: Optional[str] = None, bins: int = DEFAULT_HIST_BINS) -> None:
        """Plot daily PnL distribution histogram.
        
        Parameters
        ----------
        title : str, optional
            Title for the plot. If None, auto-generates based on factor name
        bins : int, default 50
            Number of histogram bins
        """
        if title is None:
            title = f"Daily PnL Distribution ({self.factor_col})"

        if self.daily_pnl.empty:
            logger.error("PnL data is empty, cannot plot distribution")
            return
        
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            # Fallback if seaborn style is not available
            plt.style.use('default')
        
        fig, ax = plt.subplots(figsize=(14, 7))
        self.daily_pnl.hist(ax=ax, bins=bins, alpha=0.7, color='green', edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel("Daily PnL")
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.3)
        
        # Add some statistics to the plot
        mean_pnl = self.daily_pnl.mean()
        std_pnl = self.daily_pnl.std()
        ax.axvline(mean_pnl, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_pnl:.2f}')
        ax.axvline(mean_pnl + std_pnl, color='orange', linestyle='--', alpha=0.7, label=f'+1 Std: {mean_pnl + std_pnl:.2f}')
        ax.axvline(mean_pnl - std_pnl, color='orange', linestyle='--', alpha=0.7, label=f'-1 Std: {mean_pnl - std_pnl:.2f}')
        ax.legend()
        
        fig.tight_layout()
        
        # Try to show the plot, with fallback
        try:
            plt.show()
        except Exception as e:
            logger.warning(f"Could not display plot: {e}")
            # Save plot instead
            try:
                plot_path = self._last_output_path.replace('.csv', '_pnl_dist.png') if hasattr(self, '_last_output_path') else 'pnl_distribution.png'
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                logger.info(f"Plot saved to: {plot_path}")
            except Exception as save_e:
                logger.error(f"Could not save plot: {save_e}")
        finally:
            plt.close()

    def save_pnl_series(self, output_path: str) -> None:
        """Save daily PnL series to CSV file.
        
        Parameters
        ----------
        output_path : str
            Path to save the PnL series CSV file
            
        Raises
        ------
        ValueError
            If PnL data is empty
        """
        if self.daily_pnl.empty:
            raise ValueError("PnL data is empty, cannot save")
        
        # Store output path for potential plot saving
        self._last_output_path = output_path
        
        # Convert to DataFrame
        pnl_df = pd.DataFrame({
            f'pnl_{self.factor_col}': self.daily_pnl
        })
        
        # Reset index to make timestamp a column
        pnl_df.reset_index().to_csv(output_path, index=False)
        if self.verbose:
            logger.info(f"PnL series saved to: {output_path}")
        
    def get_pnl_series(self) -> pd.Series:
        """Get daily PnL series for correlation analysis.
        
        Returns
        -------
        pd.Series
            Daily PnL series with timestamp index
        """
        return self.daily_pnl.copy()

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get calculated performance metrics.
        
        Returns
        -------
        Dict[str, float]
            Dictionary containing performance metrics with clean float values
        """
        # Convert numpy types to clean Python floats for better display
        clean_metrics = {}
        for key, value in self.performance_metrics.items():
            if hasattr(value, 'item'):  # numpy scalar
                clean_metrics[key] = float(value.item())
            else:
                clean_metrics[key] = float(value)
        return clean_metrics
    
    def summary(self, title: Optional[str] = None) -> None:
        """Print a clean, professional summary of backtest results.
        
        Parameters
        ----------
        title : str, optional
            Custom title for the summary
        """
        if title is None:
            title = f"Backtest Results: {self.factor_col}"
            
        if not self.performance_metrics:
            print("⚠️  No performance metrics available. Run calculate_performance_metrics() first.")
            return
            
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
        
        # Basic info
        if not self.equity_curve.empty:
            start_date = self.equity_curve.index[0].strftime('%Y-%m-%d')
            end_date = self.equity_curve.index[-1].strftime('%Y-%m-%d')
            initial_capital = self.equity_curve.iloc[0]
            final_capital = self.equity_curve.iloc[-1]
            
            print(f"Period:                    {start_date} to {end_date}")
            print(f"Initial Capital:           ${initial_capital:,.0f}")
            print(f"Final Capital:             ${final_capital:,.0f}")
            print(f"Trading Days:              {len(self.daily_pnl)}")
            print(f"Symbols:                   {', '.join(self.symbols)}")
        
        print("\nPerformance Metrics:")
        print("-"*60)
        
        metrics = self.get_performance_metrics()
        
        # Format and display metrics
        print(f"Total Return:              {metrics['total_return']:>8.2%}")
        print(f"Annualized Return:         {metrics['annualized_return']:>8.2%}")
        print(f"Annualized Volatility:     {metrics['annualized_volatility']:>8.2%}")
        print(f"Sharpe Ratio:              {metrics['sharpe_ratio']:>8.3f}")
        print(f"Max Drawdown:              {metrics['max_drawdown']:>8.2%}")
        print(f"Calmar Ratio:              {metrics['calmar_ratio']:>8.3f}")
        
        # Performance assessment
        total_return = metrics['total_return']
        sharpe_ratio = metrics['sharpe_ratio']
        
        print("\nAssessment:")
        print("-"*60)
        
        if total_return > 0:
            return_status = "Profitable"
        else:
            return_status = "Loss-making"
            
        if sharpe_ratio > 1:
            risk_status = "Excellent risk-adjusted returns"
        elif sharpe_ratio > 0.5:
            risk_status = "Good risk-adjusted returns"
        elif sharpe_ratio > 0:
            risk_status = "Fair risk-adjusted returns"
        else:
            risk_status = "Poor risk-adjusted returns"
        
        print(f"Return Profile:            {return_status}")
        print(f"Risk Assessment:           {risk_status}")
        print("="*60 + "\n")
