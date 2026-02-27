"""
批量选股器
从股票池中筛选优质股票
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.analyzer import StockAnalyzer
from core.data import DataManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockScreener:
    """
    股票筛选器
    
    批量分析股票并筛选出优质标的
    """
    
    # 缓存目录
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '../data/cache')
    CACHE_EXPIRE_HOURS = 4  # 缓存过期时间（小时）
    
    def __init__(self, max_workers: int = 5):
        """
        初始化筛选器
        
        Args:
            max_workers: 并行工作线程数
        """
        self.analyzer = StockAnalyzer()
        self.data_manager = DataManager()
        self.max_workers = max_workers
        
        # 确保缓存目录存在
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
    def _get_cache_path(self, symbol: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.CACHE_DIR, f'{symbol}.json')
    
    def _load_cache(self, symbol: str) -> Optional[Dict]:
        """
        加载缓存数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            缓存的分析结果或None
        """
        cache_path = self._get_cache_path(symbol)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                
            # 检查是否过期
            cache_time = datetime.fromisoformat(cache.get('cache_time', '2000-01-01'))
            if datetime.now() - cache_time > timedelta(hours=self.CACHE_EXPIRE_HOURS):
                return None
                
            return cache.get('result')
        except Exception as e:
            logger.debug(f"加载缓存失败 {symbol}: {e}")
            return None
    
    def _save_cache(self, symbol: str, result: Dict):
        """
        保存缓存数据
        
        Args:
            symbol: 股票代码
            result: 分析结果
        """
        cache_path = self._get_cache_path(symbol)
        
        try:
            cache = {
                'cache_time': datetime.now().isoformat(),
                'result': result
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"保存缓存失败 {symbol}: {e}")
    
    def _analyze_single(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """
        分析单只股票
        
        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存
            
        Returns:
            分析结果或None
        """
        # 尝试从缓存加载
        if use_cache:
            cached = self._load_cache(symbol)
            if cached:
                logger.debug(f"使用缓存数据: {symbol}")
                return cached
        
        try:
            # 获取真实数据
            data = self.data_manager.get_data(symbol, use_real=True)
            
            # 分析
            result = self.analyzer.analyze(data, symbol)
            
            # 保存缓存
            if use_cache:
                self._save_cache(symbol, result)
            
            return result
            
        except Exception as e:
            logger.warning(f"分析 {symbol} 失败: {e}")
            return None
    
    def screen(self, 
               symbols: List[str], 
               min_score: float = 70,
               top_n: int = 10,
               use_cache: bool = True) -> List[Dict]:
        """
        批量筛选股票（并行）
        
        Args:
            symbols: 股票代码列表
            min_score: 最低分数阈值
            top_n: 返回前N只股票
            use_cache: 是否使用缓存
            
        Returns:
            筛选结果列表
        """
        results = []
        total = len(symbols)
        completed = 0
        
        logger.info(f"开始分析 {total} 只股票...")
        
        # 并行分析
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self._analyze_single, symbol, use_cache): symbol 
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    result = future.result()
                    
                    if result and result['scores']['total'] >= min_score:
                        results.append(result)
                        
                    # 打印进度
                    if completed % 5 == 0 or completed == total:
                        logger.info(f"分析进度: {completed}/{total}")
                        
                except Exception as e:
                    logger.warning(f"分析 {symbol} 异常: {e}")
                    
        # 按总分排序
        results.sort(key=lambda x: x['scores']['total'], reverse=True)
        
        logger.info(f"筛选完成，共找到 {len(results)} 只符合条件的股票")
        
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
        results = self.screen(symbols, min_score=0, top_n=len(symbols))
        
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
    
    def clear_cache(self):
        """清除所有缓存"""
        import shutil
        if os.path.exists(self.CACHE_DIR):
            shutil.rmtree(self.CACHE_DIR)
            os.makedirs(self.CACHE_DIR, exist_ok=True)
            logger.info("缓存已清除")
