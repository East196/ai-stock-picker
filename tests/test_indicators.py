"""
技术指标单元测试
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicators import SMA, EMA, MACD, RSI, BOLL, KDJ, ATR, OBV, VWAP


class TestSMA:
    """SMA 测试"""
    
    def test_sma_basic(self):
        """基本计算"""
        data = pd.Series([1, 2, 3, 4, 5])
        result = SMA(data, 3)
        assert result.iloc[-1] == 4.0  # (3+4+5)/3
        
    def test_sma_empty(self):
        """空数据处理"""
        data = pd.Series([])
        result = SMA(data, 3)
        assert len(result) == 0
        
    def test_sma_window_larger_than_data(self):
        """窗口大于数据"""
        data = pd.Series([1, 2, 3])
        result = SMA(data, 5)
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[2])


class TestEMA:
    """EMA 测试"""
    
    def test_ema_basic(self):
        """基本计算"""
        data = pd.Series([1, 2, 3, 4, 5])
        result = EMA(data, 3)
        assert len(result) == len(data)
        assert result.iloc[-1] > result.iloc[0]  # 上升趋势


class TestRSI:
    """RSI 测试"""
    
    def test_rsi_range(self):
        """RSI 应在 0-100 之间"""
        np.random.seed(42)
        data = pd.Series(np.random.randn(100).cumsum() + 100)
        rsi = RSI(data, 14)
        
        # 跳过 NaN 值
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
        
    def test_rsi_all_up(self):
        """持续上涨 RSI 应接近 100"""
        data = pd.Series(range(1, 101))
        rsi = RSI(data, 14)
        assert rsi.iloc[-1] > 90  # 应该接近 100
        
    def test_rsi_all_down(self):
        """持续下跌 RSI 应接近 0"""
        data = pd.Series(range(100, 0, -1))
        rsi = RSI(data, 14)
        assert rsi.iloc[-1] < 10  # 应该接近 0


class TestMACD:
    """MACD 测试"""
    
    def test_macd_structure(self):
        """返回结构正确"""
        data = pd.Series(range(1, 101))
        result = MACD(data)
        
        assert 'macd' in result
        assert 'signal' in result
        assert 'histogram' in result
        
    def test_macd_lengths(self):
        """长度一致"""
        data = pd.Series(range(1, 101))
        result = MACD(data)
        
        assert len(result['macd']) == len(data)
        assert len(result['signal']) == len(data)
        assert len(result['histogram']) == len(data)


class TestBOLL:
    """布林带测试"""
    
    def test_boll_structure(self):
        """返回结构正确"""
        data = pd.Series(range(1, 101))
        result = BOLL(data)
        
        assert 'upper' in result
        assert 'middle' in result
        assert 'lower' in result
        
    def test_boll_order(self):
        """上轨 > 中轨 > 下轨"""
        data = pd.Series(range(1, 101))
        result = BOLL(data)
        
        # 最后一个有效值
        upper = result['upper'].dropna().iloc[-1]
        middle = result['middle'].dropna().iloc[-1]
        lower = result['lower'].dropna().iloc[-1]
        
        assert upper > middle > lower


class TestKDJ:
    """KDJ 测试"""
    
    def test_kdj_structure(self):
        """返回结构正确"""
        high = pd.Series(range(10, 110))
        low = pd.Series(range(0, 100))
        close = pd.Series(range(5, 105))
        
        result = KDJ(high, low, close)
        
        assert 'K' in result
        assert 'D' in result
        assert 'J' in result
        
    def test_kdj_range(self):
        """KDJ 值通常在 0-100 之间"""
        high = pd.Series(range(10, 110))
        low = pd.Series(range(0, 100))
        close = pd.Series(range(5, 105))
        
        result = KDJ(high, low, close)
        
        # K 和 D 应该在 0-100 之间（J 可能超出）
        k = result['K'].dropna()
        d = result['D'].dropna()
        
        assert (k >= 0).all() and (k <= 100).all()
        assert (d >= 0).all() and (d <= 100).all()
        
    def test_kdj_division_by_zero(self):
        """除零保护"""
        # 高低价相同的情况
        high = pd.Series([10] * 20)
        low = pd.Series([10] * 20)
        close = pd.Series([10] * 20)
        
        result = KDJ(high, low, close)
        
        # 不应该抛出异常，K 应该是 50（默认值）
        assert not result['K'].isna().all()


class TestATR:
    """ATR 测试"""
    
    def test_atr_positive(self):
        """ATR 应该是正数"""
        high = pd.Series(range(10, 110))
        low = pd.Series(range(0, 100))
        close = pd.Series(range(5, 105))
        
        atr = ATR(high, low, close)
        
        valid_atr = atr.dropna()
        assert (valid_atr > 0).all()


class TestOBV:
    """OBV 测试"""
    
    def test_obv_cumulative(self):
        """OBV 是累积值"""
        close = pd.Series([100, 101, 102, 101, 103])
        volume = pd.Series([1000, 1100, 1200, 900, 1300])
        
        obv = OBV(close, volume)
        
        assert len(obv) == len(close)


class TestVWAP:
    """VWAP 测试"""
    
    def test_vwap_range(self):
        """VWAP 应该在最高价和最低价之间"""
        high = pd.Series([105, 106, 107, 108, 109])
        low = pd.Series([95, 96, 97, 98, 99])
        close = pd.Series([100, 101, 102, 103, 104])
        volume = pd.Series([1000, 1100, 1200, 900, 1300])
        
        vwap = VWAP(high, low, close, volume)
        
        # VWAP 应该在价格范围内
        typical_price = (high + low + close) / 3
        assert vwap.iloc[-1] >= low.min()
        assert vwap.iloc[-1] <= high.max()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
