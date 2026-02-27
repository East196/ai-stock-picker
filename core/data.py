"""
数据管理模块
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import os
import baostock as bs


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
        self._bs_logged_in = False
        
    def _ensure_bs_login(self):
        """确保 baostock 已登录"""
        if not self._bs_logged_in:
            lg = bs.login()
            if lg.error_code != '0':
                raise Exception(f'baostock 登录失败: {lg.error_msg}')
            self._bs_logged_in = True
            
    def fetch_from_baostock(self, symbol: str, start_date: str = None, end_date: str = None, 
                            adjust: str = "2") -> pd.DataFrame:
        """
        从 baostock 获取真实股票数据
        
        Args:
            symbol: 股票代码（如 600570）
            start_date: 开始日期 (YYYY-MM-DD)，默认一年前
            end_date: 结束日期 (YYYY-MM-DD)，默认今天
            adjust: 复权类型，"2" 前复权，"1" 后复权，"0" 不复权
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        self._ensure_bs_login()
        
        # 处理日期
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
        # 转换股票代码格式 (600570 -> sh.600570, 000001 -> sz.000001)
        if symbol.startswith('6'):
            bs_code = f'sh.{symbol}'
        else:
            bs_code = f'sz.{symbol}'
            
        # 获取数据
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,code,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag=adjust
        )
        
        if rs.error_code != '0':
            raise Exception(f'获取数据失败: {rs.error_msg}')
            
        # 转换为 DataFrame
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
            
        if not data_list:
            raise Exception(f'未获取到数据: {symbol}')
            
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 数据类型转换
        df['date'] = pd.to_datetime(df['date'])
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # 设置索引
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        
        return df
        
    def get_data(self, symbol: str, start_date: str = None, end_date: str = None, 
                 use_real: bool = True) -> pd.DataFrame:
        """
        获取股票数据（优先真实数据）
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            use_real: 是否使用真实数据
            
        Returns:
            DataFrame
        """
        if use_real:
            try:
                return self.fetch_from_baostock(symbol, start_date, end_date)
            except Exception as e:
                print(f"⚠️ 获取真实数据失败: {e}，使用模拟数据")
                return self.generate_sample_data(symbol)
        return self.generate_sample_data(symbol)
        
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
