"""
数据管理模块
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import os


class DataManager:
    """
    数据管理器
    """
    
    def __init__(self, data_dir: str = None):
        """
        初始化
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '../data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def generate_sample_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """
        生成模拟数据（用于演示）
        
        Args:
            symbol: 股票代码
            days: 天数
            
        Returns:
            OHLCV数据
        """
        np.random.seed(hash(symbol) % 2**32)
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # 生成价格（带趋势的随机游走）
        trend = np.random.choice([-1, 1]) * np.random.uniform(0.0002, 0.001)
        volatility = np.random.uniform(0.01, 0.03)
        
        returns = np.random.normal(trend, volatility, days)
        price = np.random.uniform(10, 100)
        prices = []
        
        for ret in returns:
            price *= (1 + ret)
            prices.append(price)
            
        # 生成OHLCV
        data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'close': prices,
            'high': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
            'low': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
            'volume': [int(np.random.uniform(1000000, 10000000)) for _ in prices]
        })
        
        data.set_index('date', inplace=True)
        return data
    
    def load_from_csv(self, filepath: str) -> pd.DataFrame:
        """
        从CSV加载数据
        
        Args:
            filepath: 文件路径
            
        Returns:
            DataFrame
        """
        df = pd.read_csv(filepath)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        elif '日期' in df.columns:
            df['date'] = pd.to_datetime(df['日期'])
            df.set_index('date', inplace=True)
            
        return df
