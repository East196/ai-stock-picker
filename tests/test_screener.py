"""
筛选器单元测试
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screener import StockScreener


class TestStockScreener:
    """StockScreener 测试"""
    
    @pytest.fixture
    def screener(self):
        """创建筛选器实例"""
        return StockScreener(max_workers=1)
    
    def test_screen_empty_list(self, screener):
        """空列表测试"""
        results = screener.screen([], min_score=0, top_n=10, use_cache=False)
        assert results == []
        
    def test_screen_min_score_filter(self, screener):
        """最低分数过滤测试"""
        # 使用一个不存在的股票代码
        results = screener.screen(['999999'], min_score=100, top_n=10, use_cache=False)
        
        # 应该返回空（因为获取不到数据或分数不够）
        assert len(results) == 0
        
    def test_generate_report_empty(self, screener):
        """空结果报告测试"""
        report = screener.generate_report([])
        
        assert "未找到符合条件的股票" in report
        
    def test_generate_report_with_results(self, screener):
        """有结果报告测试"""
        mock_results = [{
            'symbol': '600570',
            'scores': {
                'total': 75,
                'trend': 20,
                'volume': 18,
                'volatility': 15,
                'momentum': 12,
                'risk': 8
            },
            'recommendation': {
                'level': '可以考虑',
                'action': '轻仓买入',
                'stars': '⭐⭐⭐',
                'description': '部分指标较好'
            },
            'latest_price': 30.0,
            'price_change': 1.5
        }]
        
        report = screener.generate_report(mock_results)
        
        assert '600570' in report
        assert '75' in report
        assert '可以考虑' in report
        
    def test_clear_cache(self, screener):
        """清除缓存测试"""
        # 应该不抛出异常
        screener.clear_cache()


class TestCache:
    """缓存测试"""
    
    @pytest.fixture
    def screener(self):
        """创建筛选器实例"""
        return StockScreener(max_workers=1)
    
    def test_cache_path(self, screener):
        """缓存路径测试"""
        path = screener._get_cache_path('600570')
        assert '600570.json' in path
        
    def test_save_and_load_cache(self, screener):
        """保存和加载缓存测试"""
        screener.clear_cache()
        
        mock_result = {
            'symbol': 'TEST',
            'scores': {'total': 50}
        }
        
        # 保存缓存
        screener._save_cache('TEST', mock_result)
        
        # 加载缓存
        loaded = screener._load_cache('TEST')
        
        assert loaded is not None
        assert loaded['symbol'] == 'TEST'
        
        # 清理
        screener.clear_cache()
        
    def test_cache_expiry(self, screener):
        """缓存过期测试"""
        import json
        from datetime import datetime, timedelta
        
        screener.clear_cache()
        
        # 创建一个过期的缓存
        cache_path = screener._get_cache_path('EXPIRED')
        expired_cache = {
            'cache_time': (datetime.now() - timedelta(hours=5)).isoformat(),
            'result': {'symbol': 'EXPIRED'}
        }
        
        with open(cache_path, 'w') as f:
            json.dump(expired_cache, f)
        
        # 应该返回 None（已过期）
        loaded = screener._load_cache('EXPIRED')
        assert loaded is None
        
        screener.clear_cache()


class TestStrategies:
    """策略测试"""
    
    @pytest.fixture
    def screener(self):
        """创建筛选器实例"""
        return StockScreener(max_workers=1)
    
    def test_strategy_types(self, screener):
        """策略类型测试"""
        # 这些策略应该存在且不抛出异常
        strategies = ['aggressive', 'balanced', 'conservative', 'unknown']
        
        for strategy in strategies:
            # 即使是空列表也不应该报错
            screener.screen_by_strategy([], strategy)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
