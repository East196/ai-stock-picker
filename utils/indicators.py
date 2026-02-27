"""
技术指标计算
"""
import pandas as pd
import numpy as np


def SMA(data: pd.Series, window: int) -> pd.Series:
    """
    简单移动平均线
    
    Args:
        data: 价格数据
        window: 窗口期
        
    Returns:
        SMA序列
    """
    return data.rolling(window=window).mean()


def EMA(data: pd.Series, window: int) -> pd.Series:
    """
    指数移动平均线
    
    Args:
        data: 价格数据
        window: 窗口期
        
    Returns:
        EMA序列
    """
    return data.ewm(span=window, adjust=False).mean()


def MACD(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    MACD指标
    
    Args:
        close: 收盘价
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期
        
    Returns:
        dict: {'macd': MACD线, 'signal': 信号线, 'histogram': 柱状图}
    """
    ema_fast = EMA(close, fast)
    ema_slow = EMA(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = EMA(macd_line, signal)
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def RSI(close: pd.Series, window: int = 14) -> pd.Series:
    """
    相对强弱指标
    
    Args:
        close: 收盘价
        window: 窗口期
        
    Returns:
        RSI序列
    """
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def BOLL(close: pd.Series, window: int = 20, num_std: int = 2) -> dict:
    """
    布林带
    
    Args:
        close: 收盘价
        window: 窗口期
        num_std: 标准差倍数
        
    Returns:
        dict: {'upper': 上轨, 'middle': 中轨, 'lower': 下轨}
    """
    middle = SMA(close, window)
    std = close.rolling(window=window).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }


def KDJ(high: pd.Series, low: pd.Series, close: pd.Series, 
        n: int = 9, m1: int = 3, m2: int = 3) -> dict:
    """
    KDJ指标
    
    Args:
        high: 最高价
        low: 最低价
        close: 收盘价
        n: RSV周期
        m1: K值周期
        m2: D值周期
        
    Returns:
        dict: {'K': K值, 'D': D值, 'J': J值}
    """
    # 计算RSV
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
    
    # 计算K、D、J
    K = rsv.ewm(com=m1-1, adjust=False).mean()
    D = K.ewm(com=m2-1, adjust=False).mean()
    J = 3 * K - 2 * D
    
    return {
        'K': K,
        'D': D,
        'J': J
    }


def ATR(high: pd.Series, low: pd.Series, close: pd.Series, 
        window: int = 14) -> pd.Series:
    """
    平均真实波幅
    
    Args:
        high: 最高价
        low: 最低价
        close: 收盘价
        window: 窗口期
        
    Returns:
        ATR序列
    """
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    
    return atr


def OBV(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    能量潮指标
    
    Args:
        close: 收盘价
        volume: 成交量
        
    Returns:
        OBV序列
    """
    direction = np.where(close > close.shift(), 1, np.where(close < close.shift(), -1, 0))
    obv = (volume * direction).cumsum()
    return pd.Series(obv, index=close.index)
