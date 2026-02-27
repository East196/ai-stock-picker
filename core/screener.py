"""
批量选股器
从股票池中筛选优质股票
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import StockAnalyzer
from core.data import DataManager


class StockScreener:
    """
    股票筛选器
    
    批量分析股票并筛选出优质标的
    """
    
    def __init__(self):
        """初始化筛选器"""
        self.analyzer = StockAnalyzer()
        self.data_manager = DataManager()
        
    def screen(self, 
               symbols: List[str], 
               min_score: float = 70,
               top_n: int = 10) -> List[Dict]:
        """
        批量筛选股票
        
        Args:
            symbols: 股票代码列表
            min_score: 最低分数阈值
            top_n: 返回前N只股票
            
        Returns:
            筛选结果列表
        """
        results = []
        
        print(f"开始分析 {len(symbols)} 只股票...")
        
        for i, symbol in enumerate(symbols):
            try:
                print(f"分析中 [{i+1}/{len(symbols)}]: {symbol}")
                
                # 获取真实数据
                data = self.data_manager.get_data(symbol, use_real=True)
                
                # 分析
                result = self.analyzer.analyze(data, symbol)
                
                # 过滤低分股票
                if result['scores']['total'] >= min_score:
                    results.append(result)
                    
            except Exception as e:
                print(f"分析 {symbol} 失败: {e}")
                continue
                
        # 按总分排序
        results.sort(key=lambda x: x['scores']['total'], reverse=True)
        
        # 返回前N只
        return results[:top_n]
    
    def screen_by_strategy(self, symbols: List[str], strategy: str = 'balanced') -> List[Dict]:
        """
        按策略筛选
        
        Args:
            symbols: 股票代码列表
            strategy: 策略类型
                - 'aggressive': 激进型（高分）
                - 'balanced': 平衡型（中高分）
                - 'conservative': 保守型（低风险）
                
        Returns:
            筛选结果
        """
        if strategy == 'aggressive':
            # 激进策略：追求高分，不考虑风险
            return self.screen(symbols, min_score=80, top_n=5)
            
        elif strategy == 'balanced':
            # 平衡策略：综合考虑
            results = self.screen(symbols, min_score=70, top_n=10)
            # 过滤风险得分低于6的
            return [r for r in results if r['scores']['risk'] >= 6]
            
        elif strategy == 'conservative':
            # 保守策略：优先考虑风险
            results = self.screen(symbols, min_score=65, top_n=15)
            # 按风险得分排序
            results.sort(key=lambda x: x['scores']['risk'], reverse=True)
            return results[:10]
            
        else:
            return self.screen(symbols)
    
    def get_top_stocks_by_dimension(self,
                                   symbols: List[str],
                                   dimension: str = 'total',
                                   top_n: int = 5) -> List[Dict]:
        """
        按特定维度获取top股票
        
        Args:
            symbols: 股票代码列表
            dimension: 维度 (total, trend, volume, volatility, momentum, risk)
            top_n: 返回数量
            
        Returns:
            排序结果
        """
        results = []
        
        for symbol in symbols:
            try:
                data = self.data_manager.get_data(symbol, use_real=True)
                result = self.analyzer.analyze(data, symbol)
                results.append(result)
            except:
                continue
                
        # 按指定维度排序
        results.sort(key=lambda x: x['scores'].get(dimension, 0), reverse=True)
        
        return results[:top_n]
    
    def generate_report(self, results: List[Dict]) -> str:
        """
        生成筛选报告
        
        Args:
            results: 筛选结果
            
        Returns:
            报告文本
        """
        report = []
        report.append("=" * 80)
        report.append("AI选股助手 - 筛选报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        if not results:
            report.append("未找到符合条件的股票")
            return "\n".join(report)
            
        report.append(f"共筛选出 {len(results)} 只优质股票:")
        report.append("")
        
        for i, result in enumerate(results, 1):
            scores = result['scores']
            rec = result['recommendation']
            
            report.append(f"【第{i}名】{result['symbol']}")
            report.append(f"  综合得分: {scores['total']}分 {rec['stars']}")
            report.append(f"  推荐等级: {rec['level']} - {rec['action']}")
            report.append(f"  最新价: ¥{result['latest_price']:.2f}")
            report.append(f"  涨跌幅: {result['price_change']:+.2f}%")
            report.append(f"  分项得分:")
            report.append(f"    趋势: {scores['trend']}/30")
            report.append(f"    量能: {scores['volume']}/25")
            report.append(f"    波动: {scores['volatility']}/20")
            report.append(f"    动量: {scores['momentum']}/15")
            report.append(f"    风险: {scores['risk']}/10")
            report.append(f"  分析建议: {rec['description']}")
            report.append("")
            
        report.append("=" * 80)
        report.append("⚠️  风险提示:")
        report.append("本报告仅供参考，不构成投资建议")
        report.append("股市有风险，投资需谨慎")
        report.append("=" * 80)
        
        return "\n".join(report)
