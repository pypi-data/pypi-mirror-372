# -*- coding: utf-8 -*-

"""
Phandas: Quantitative analysis and backtesting for cryptocurrency markets.
"""

__author__ = "Phantom Management"
__version__ = "0.1.1" # Added Alpha101 factors and utility functions

from .data_manager import fetch_and_prepare_data, plot_price_data, check_data_quality
from .factors import (
    # ?šç”¨è¼”åŠ©?½æ•¸ (for factor expression parser)
    ts_sum, ts_mean, ts_std, ts_min, ts_max, ts_rank,
    ts_argmax, ts_argmin, correlation, delta, delay, rank, scale, returns, decay_linear
)
from .factor_parser import (
    FactorExpressionParser, calculate_factor_from_expression, add_factor_to_data
)
from .backtester import Backtester

__all__ = [
    # ?¸æ?ç®¡ç?
    'fetch_and_prepare_data',
    'plot_price_data', 
    'check_data_quality',
    # ?šç”¨è¼”åŠ©?½æ•¸ (mainly for internal use by factor parser)
    'ts_sum', 'ts_mean', 'ts_std', 'ts_min', 'ts_max', 'ts_rank',
    'ts_argmax', 'ts_argmin', 'correlation', 'delta', 'delay', 'rank', 'scale', 'returns', 'decay_linear',
    # ? å?è¡¨é?å¼è§£?å™¨
    'FactorExpressionParser', 'calculate_factor_from_expression', 'add_factor_to_data',
    # ?æ¸¬å¼•æ?
    'Backtester'
]
