"""
分析器单元测试
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import StockAnalyzer


class TestStockAnalyzer:
    """StockAnalyzer 测试"""
    
    @pytest.fixture
    def analyzer(self):
        """创建分析器实例"""
        return StockAnalyzer()
    
    @pytest.fixture
    def sample_data(self):
        """生成测试数据"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        
        # 生成模拟价格数据
        returns = np.random.normal(0.001, 0.02, 100)
        price = 50
        prices = []
        for ret in returns:
            price *= (1 + ret)
            prices.append(price)
            
        data = pd.DataFrame({
            'open': prices,
            'close': prices,
            'high': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
            'low': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
            'volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        return data
    
    def test_analyze_basic(self, analyzer, sample_data):
        """基本分析测试"""
        result = analyzer.analyze(sample_data, 'TEST')
        
        assert 'symbol' in result
        assert 'scores' in result
        assert 'recommendation' in result
        assert 'signals' in result
        
    def test_scores_range(self, analyzer, sample_data):
        """分数范围测试"""
        result = analyzer.analyze(sample_data, 'TEST')
        scores = result['scores']
        
        # 总分应该在 0-100 之间
        assert 0 <= scores['total'] <= 100
        
        # 各维度分数应该合理
        assert 0 <= scores['trend'] <= 30
        assert 0 <= scores['volume'] <= 25
        assert 0 <= scores['volatility'] <= 20
        assert 0 <= scores['momentum'] <= 15
        assert 0 <= scores['risk'] <= 10
        
    def test_recommendation_structure(self, analyzer, sample_data):
        """推荐结构测试"""
        result = analyzer.analyze(sample_data, 'TEST')
        rec = result['recommendation']
        
        assert 'level' in rec
        assert 'action' in rec
        assert 'stars' in rec
        assert 'description' in rec
        
    def test_signals_structure(self, analyzer, sample_data):
        """信号结构测试"""
        result = analyzer.analyze(sample_data, 'TEST')
        signals = result['signals']
        
        assert 'signals' in signals
        assert 'trend' in signals
        assert 'strength' in signals
        assert isinstance(signals['signals'], list)
        
    def test_insufficient_data(self, analyzer):
        """数据不足测试"""
        # 只有 30 天数据
        data = pd.DataFrame({
            'open': [10] * 30,
            'close': [10] * 30,
            'high': [11] * 30,
            'low': [9] * 30,
            'volume': [1000000] * 30
        })
        
        with pytest.raises(ValueError, match="数据不足"):
            analyzer.analyze(data, 'TEST')
            
    def test_empty_data(self, analyzer):
        """空数据测试"""
        data = pd.DataFrame()
        
        with pytest.raises(ValueError):
            analyzer.analyze(data, 'TEST')
            
    def test_none_data(self, analyzer):
        """None 数据测试"""
        with pytest.raises(ValueError):
            analyzer.analyze(None, 'TEST')
            
    def test_custom_weights(self):
        """自定义权重测试"""
        custom_weights = {
            'trend': 0.4,
            'volume': 0.2,
            'volatility': 0.15,
            'momentum': 0.15,
            'risk': 0.1
        }
        
        analyzer = StockAnalyzer(weights=custom_weights)
        
        assert analyzer.weights['trend'] == 0.4
        assert analyzer.weights['volume'] == 0.2
        
    def test_safe_get(self, analyzer):
        """安全访问测试"""
        series = pd.Series([1, 2, 3, 4, 5])
        
        # 正常访问
        assert analyzer._safe_get(series, -1) == 5
        
        # 越界访问
        assert analyzer._safe_get(series, -10) == 0  # 默认值
        
        # 空序列
        empty = pd.Series([])
        assert analyzer._safe_get(empty) == 0
        
        # None
        assert analyzer._safe_get(None) == 0


class TestScoreConsistency:
    """分数一致性测试"""
    
    def test_high_trend_score(self):
        """强趋势应得高分"""
        analyzer = StockAnalyzer()
        
        # 创建明显的上升趋势数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = [10 + i * 0.5 for i in range(100)]  # 持续上涨
        
        data = pd.DataFrame({
            'open': prices,
            'close': prices,
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'volume': [1000000] * 100
        }, index=dates)
        
        result = analyzer.analyze(data, 'TEST')
        
        # 趋势分数应该较高
        assert result['scores']['trend'] > 15
        
    def test_oversold_rsi_score(self):
        """超卖 RSI 应得高分（买入机会）"""
        analyzer = StockAnalyzer()
        
        # 创建持续下跌的数据（RSI 会超卖）
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = [100 - i * 0.5 for i in range(100)]  # 持续下跌
        
        data = pd.DataFrame({
            'open': prices,
            'close': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'volume': [1000000] * 100
        }, index=dates)
        
        result = analyzer.analyze(data, 'TEST')
        
        # 波动分数应该较高（RSI 超卖是买入机会）
        assert result['scores']['volatility'] > 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
