# -*- coding: utf-8 -*-

"""
Phandas: Quantitative analysis and backtesting for cryptocurrency markets.
"""

__author__ = "Phantom Management"
__version__ = "0.1.0" # Added Alpha101 factors and utility functions

from .data_manager import fetch_and_prepare_data, plot_price_data, check_data_quality
from .factors import (
    # 通用輔助函數 (for factor expression parser)
    ts_sum, ts_mean, ts_std, ts_min, ts_max, ts_rank,
    ts_argmax, ts_argmin, correlation, delta, delay, rank, scale, returns, decay_linear
)
from .factor_parser import (
    FactorExpressionParser, calculate_factor_from_expression, add_factor_to_data
)
from .backtester import Backtester

__all__ = [
    # 數據管理
    'fetch_and_prepare_data',
    'plot_price_data', 
    'check_data_quality',
    # 通用輔助函數 (mainly for internal use by factor parser)
    'ts_sum', 'ts_mean', 'ts_std', 'ts_min', 'ts_max', 'ts_rank',
    'ts_argmax', 'ts_argmin', 'correlation', 'delta', 'delay', 'rank', 'scale', 'returns', 'decay_linear',
    # 因子表達式解析器
    'FactorExpressionParser', 'calculate_factor_from_expression', 'add_factor_to_data',
    # 回測引擎
    'Backtester'
]