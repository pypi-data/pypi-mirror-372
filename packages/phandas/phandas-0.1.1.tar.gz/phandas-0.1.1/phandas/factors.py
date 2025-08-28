import pandas as pd
import numpy as np
from scipy.stats import rankdata

# ========== 通用輔助函數 (參考 Alpha101) ==========

def ts_sum(df, window=10):
    """時間序列滾動求和"""
    return df.rolling(window, min_periods=window).sum()

def ts_mean(df, window=10):
    """時間序列滾動平均 (別名: sma)"""
    return df.rolling(window, min_periods=window).mean()

def ts_std(df, window=10):
    """時間序列滾動標準差"""
    return df.rolling(window, min_periods=window).std()

def ts_min(df, window=10):
    """時間序列滾動最小值"""
    return df.rolling(window, min_periods=window).min()

def ts_max(df, window=10):
    """時間序列滾動最大值"""
    return df.rolling(window, min_periods=window).max()

def ts_rank(df, window=10):
    """時間序列滾動排名"""
    def rolling_rank(na):
        return rankdata(na, method='min')[-1]
    return df.rolling(window, min_periods=window).apply(rolling_rank)

def ts_argmax(df, window=10):
    """時間序列滾動最大值位置"""
    return df.rolling(window).apply(np.argmax) + 1

def ts_argmin(df, window=10):
    """時間序列滾動最小值位置"""
    return df.rolling(window).apply(np.argmin) + 1

def correlation(x, y, window=10):
    """滾動相關性"""
    return x.rolling(window).corr(y).fillna(0).replace([np.inf, -np.inf], 0)

def delta(df, period=1):
    """差分 (今日值 - period 日前值)"""
    return df.diff(period)

def delay(df, period=1):
    """滯後 (period 日前的值)"""
    return df.shift(period)

def rank(df):
    """截面排名 (跨標的排名) - 最高值=1，最低值=0"""
    def simple_rank(group):
        ranks = group.rank(method='min', ascending=True)
        # 線性壓縮到 [0, 1]: 第1名→0, 最後一名→1
        return (ranks - 1) / (len(group) - 1) if len(group) > 1 else pd.Series([1.0], index=group.index)
    
    if isinstance(df.index, pd.MultiIndex):
        return df.groupby('timestamp').apply(simple_rank).droplevel(0)
    else:
        return simple_rank(df)

def scale(df, k=1):
    """標準化：使得 sum(abs(df)) = k"""
    return df.mul(k).div(np.abs(df).sum())

def returns(df):
    """簡單收益率"""
    return df.pct_change()

def decay_linear(df, period=10):
    """線性衰減加權移動平均"""
    weights = np.array(range(1, period+1))
    sum_weights = np.sum(weights)
    return df.rolling(period).apply(lambda x: np.sum(weights*x) / sum_weights)

# ========== 原有因子函數 ==========

# Note: All predefined factor functions have been moved to expression-based approach
# Use phn.add_factor_to_data() with expressions instead:
#
# alpha001: Complex expression - use legacy function if needed
# alpha002: "-1 * correlation(rank(delta(log(volume), 2)), rank((close - open) / open), 6)"
# alpha003: "-1 * correlation(rank(open), rank(volume), 10)"  
# alpha004: "-1 * ts_rank(rank(low), 9)"
# alpha006: "-1 * correlation(open, volume, 10)"
# momentum: "returns(close, 20)"
# volatility: "-1 * ts_std(returns(close, 1), 30)"
