"""
数据管理单元测试
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data import DataManager


class TestDataManager:
    """DataManager 测试"""
    
    @pytest.fixture
    def data_manager(self):
        """创建数据管理器实例"""
        return DataManager()
    
    @pytest.fixture
    def data_manager_temp(self):
        """使用临时目录的数据管理器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield DataManager(data_dir=tmpdir)
    
    def test_generate_sample_data(self, data_manager):
        """生成模拟数据测试"""
        data = data_manager.generate_sample_data('TEST', days=100)
        
        assert len(data) == 100
        assert 'open' in data.columns
        assert 'close' in data.columns
        assert 'high' in data.columns
        assert 'low' in data.columns
        assert 'volume' in data.columns
        
    def test_generate_sample_data_structure(self, data_manager):
        """模拟数据结构测试"""
        data = data_manager.generate_sample_data('TEST', days=50)
        
        # 索引应该是日期
        assert isinstance(data.index, pd.DatetimeIndex)
        
        # 价格关系：high >= close >= low
        assert (data['high'] >= data['close']).all()
        assert (data['close'] >= data['low']).all()
        
    def test_save_and_load_csv(self, data_manager_temp):
        """CSV 保存和加载测试"""
        data_manager = data_manager_temp
        
        # 生成测试数据
        original_data = data_manager.generate_sample_data('TEST', days=50)
        
        # 保存
        data_manager.save_to_csv(original_data, 'test_data.csv')
        
        # 加载
        loaded_data = data_manager.load_from_csv(
            os.path.join(data_manager.data_dir, 'test_data.csv')
        )
        
        # 检查数据一致性
        pd.testing.assert_frame_equal(original_data, loaded_data)
        
    def test_get_data_with_mock(self, data_manager):
        """获取数据测试（使用模拟）"""
        # 使用模拟数据
        data = data_manager.get_data('TEST', use_real=False)
        
        assert len(data) > 0
        assert 'close' in data.columns


class TestRealData:
    """真实数据测试（需要网络）"""
    
    @pytest.fixture
    def data_manager(self):
        """创建数据管理器实例"""
        return DataManager()
    
    @pytest.mark.skip(reason="需要网络连接，手动测试时移除此行")
    def test_fetch_from_baostock(self, data_manager):
        """从 baostock 获取数据测试"""
        data = data_manager.fetch_from_baostock(
            '600570',
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        assert len(data) > 0
        assert 'open' in data.columns
        assert 'close' in data.columns
        
    @pytest.mark.skip(reason="需要网络连接，手动测试时移除此行")
    def test_get_data_real(self, data_manager):
        """获取真实数据测试"""
        data = data_manager.get_data('600570', use_real=True)
        
        assert len(data) > 0
        
    def test_get_data_fallback(self, data_manager):
        """数据获取失败回退测试"""
        # 使用不存在的股票代码
        data = data_manager.get_data('999999', use_real=True)
        
        # 应该回退到模拟数据
        assert len(data) > 0


class TestDataValidation:
    """数据验证测试"""
    
    @pytest.fixture
    def data_manager(self):
        """创建数据管理器实例"""
        return DataManager()
    
    def test_data_sorted_by_date(self, data_manager):
        """数据按日期排序测试"""
        data = data_manager.generate_sample_data('TEST', days=100)
        
        # 检查索引是否排序
        assert data.index.is_monotonic_increasing
        
    def test_no_duplicate_dates(self, data_manager):
        """无重复日期测试"""
        data = data_manager.generate_sample_data('TEST', days=100)
        
        assert not data.index.duplicated().any()
        
    def test_no_nan_in_generated_data(self, data_manager):
        """生成数据无 NaN 测试"""
        data = data_manager.generate_sample_data('TEST', days=100)
        
        assert not data.isna().any().any()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
