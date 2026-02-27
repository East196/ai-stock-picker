"""
AI选股分析器
基于多维度技术指标进行智能评分和推荐
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

# 添加父目录到路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicators import SMA, EMA, MACD, RSI, BOLL, ATR


class StockAnalyzer:
    """
    股票分析器
    
    基于技术指标进行多维度分析并生成AI评分
    """
    
    def __init__(self):
        """初始化分析器"""
        self.weights = {
            'trend': 0.30,      # 趋势指标权重
            'volume': 0.25,     # 量能指标权重
            'volatility': 0.20, # 波动指标权重
            'momentum': 0.15,   # 动量指标权重
            'risk': 0.10        # 风险指标权重
        }
        
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Dict:
        """
        分析股票数据
        
        Args:
            data: 股票数据（OHLCV格式）
            symbol: 股票代码
            
        Returns:
            分析结果字典
        """
        if len(data) < 50:
            raise ValueError("数据不足，至少需要50天的数据")
            
        # 计算各维度得分
        trend_score = self._analyze_trend(data)
        volume_score = self._analyze_volume(data)
        volatility_score = self._analyze_volatility(data)
        momentum_score = self._analyze_momentum(data)
        risk_score = self._analyze_risk(data)
        
        # 计算总分
        total_score = (
            trend_score * self.weights['trend'] +
            volume_score * self.weights['volume'] +
            volatility_score * self.weights['volatility'] +
            momentum_score * self.weights['momentum'] +
            risk_score * self.weights['risk']
        )
        
        # 生成推荐
        recommendation = self._generate_recommendation(total_score)
        
        # 生成详细信号
        signals = self._generate_signals(data)
        
        return {
            'symbol': symbol,
            'analyze_time': datetime.now().isoformat(),
            'scores': {
                'total': round(total_score, 2),
                'trend': round(trend_score, 2),
                'volume': round(volume_score, 2),
                'volatility': round(volatility_score, 2),
                'momentum': round(momentum_score, 2),
                'risk': round(risk_score, 2)
            },
            'recommendation': recommendation,
            'signals': signals,
            'latest_price': float(data['close'].iloc[-1]),
            'price_change': float((data['close'].iloc[-1] / data['close'].iloc[-2] - 1) * 100)
        }
    
    def _analyze_trend(self, data: pd.DataFrame) -> float:
        """
        分析趋势指标（30分）
        
        评分标准：
        - 均线排列（多头/空头）
        - MACD信号
        - 趋势强度
        """
        score = 0
        
        # 1. 均线排列（15分）
        ma5 = SMA(data['close'], 5)
        ma10 = SMA(data['close'], 10)
        ma20 = SMA(data['close'], 20)
        ma60 = SMA(data['close'], 60)
        
        # 多头排列
        if (ma5.iloc[-1] > ma10.iloc[-1] > ma20.iloc[-1] > ma60.iloc[-1]):
            score += 15
        elif (ma5.iloc[-1] > ma10.iloc[-1] > ma20.iloc[-1]):
            score += 12
        elif (ma5.iloc[-1] > ma10.iloc[-1]):
            score += 8
        elif (ma10.iloc[-1] > ma20.iloc[-1]):
            score += 5
            
        # 2. MACD信号（10分）
        macd_data = MACD(data['close'])
        macd = macd_data['macd']
        signal = macd_data['signal']
        
        # 金叉
        if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
            score += 10
        elif macd.iloc[-1] > signal.iloc[-1]:
            score += 7
        elif macd.iloc[-1] > 0:
            score += 4
            
        # 3. 趋势强度（5分）
        # 价格在均线上方
        price = data['close'].iloc[-1]
        if price > ma20.iloc[-1]:
            score += 3
        if price > ma60.iloc[-1]:
            score += 2
            
        return min(score, 30)
    
    def _analyze_volume(self, data: pd.DataFrame) -> float:
        """
        分析量能指标（25分）
        
        评分标准：
        - 成交量变化
        - 量价配合
        - 资金流向
        """
        score = 0
        volume = data['volume']
        close = data['close']
        
        # 1. 成交量变化（10分）
        vol_ma5 = volume.rolling(5).mean()
        vol_ma20 = volume.rolling(20).mean()
        
        # 放量
        if volume.iloc[-1] > vol_ma5.iloc[-1] * 1.5:
            score += 8
        elif volume.iloc[-1] > vol_ma5.iloc[-1]:
            score += 5
        elif volume.iloc[-1] > vol_ma20.iloc[-1]:
            score += 3
            
        # 2. 量价配合（10分）
        # 价涨量增
        price_up = close.iloc[-1] > close.iloc[-2]
        volume_up = volume.iloc[-1] > volume.iloc[-2]
        
        if price_up and volume_up:
            score += 10
        elif price_up and not volume_up:
            score += 5
        elif not price_up and not volume_up:
            score += 3
            
        # 3. 成交量趋势（5分）
        # 最近5天成交量递增
        recent_vol = volume.iloc[-5:]
        if all(recent_vol.iloc[i] < recent_vol.iloc[i+1] for i in range(len(recent_vol)-1)):
            score += 5
        elif volume.iloc[-1] > vol_ma20.iloc[-1]:
            score += 3
            
        return min(score, 25)
    
    def _analyze_volatility(self, data: pd.DataFrame) -> float:
        """
        分析波动指标（20分）
        
        评分标准：
        - RSI超买超卖
        - 布林带位置
        - 波动率
        """
        score = 0
        close = data['close']
        
        # 1. RSI（10分）
        rsi = RSI(close, 14)
        rsi_value = rsi.iloc[-1]
        
        if 30 <= rsi_value <= 70:
            # 正常区间
            score += 10
        elif 20 <= rsi_value < 30:
            # 超卖区间（买入机会）
            score += 8
        elif 70 < rsi_value <= 80:
            # 超买区间
            score += 5
        elif rsi_value < 20:
            # 严重超卖
            score += 6
        elif rsi_value > 80:
            # 严重超买
            score += 3
            
        # 2. 布林带位置（7分）
        boll = BOLL(close, 20)
        upper = boll['upper'].iloc[-1]
        lower = boll['lower'].iloc[-1]
        middle = boll['middle'].iloc[-1]
        price = close.iloc[-1]
        
        if price < lower:
            # 跌破下轨
            score += 7
        elif lower <= price < middle:
            # 下轨和中轨之间
            score += 5
        elif middle <= price < upper:
            # 中轨和上轨之间
            score += 3
        else:
            # 突破上轨
            score += 2
            
        # 3. 波动率（3分）
        returns = close.pct_change()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        if volatility < 0.2:
            # 低波动
            score += 3
        elif volatility < 0.3:
            # 中等波动
            score += 2
        else:
            # 高波动
            score += 1
            
        return min(score, 20)
    
    def _analyze_momentum(self, data: pd.DataFrame) -> float:
        """
        分析动量指标（15分）
        
        评分标准：
        - 涨跌幅
        - 连续涨跌天数
        - 突破情况
        """
        score = 0
        close = data['close']
        
        # 1. 涨跌幅（8分）
        # 5日涨跌幅
        change_5d = (close.iloc[-1] / close.iloc[-5] - 1) * 100
        
        if 0 < change_5d <= 10:
            score += 8
        elif 10 < change_5d <= 20:
            score += 6
        elif -10 < change_5d <= 0:
            score += 4
        elif change_5d > 20:
            score += 3
        else:
            score += 2
            
        # 2. 连续涨跌天数（4分）
        consecutive_up = 0
        for i in range(-1, -min(6, len(close)), -1):
            if close.iloc[i] > close.iloc[i-1]:
                consecutive_up += 1
            else:
                break
                
        if 2 <= consecutive_up <= 3:
            score += 4
        elif consecutive_up == 1:
            score += 3
        elif consecutive_up == 4:
            score += 2
        else:
            score += 1
            
        # 3. 突破情况（3分）
        ma20 = SMA(close, 20)
        
        # 突破20日均线
        if close.iloc[-1] > ma20.iloc[-1] and close.iloc[-2] <= ma20.iloc[-2]:
            score += 3
        elif close.iloc[-1] > ma20.iloc[-1]:
            score += 2
            
        return min(score, 15)
    
    def _analyze_risk(self, data: pd.DataFrame) -> float:
        """
        分析风险指标（10分）
        
        评分标准：
        - 最大回撤
        - 换手率
        - 流动性
        """
        score = 0
        close = data['close']
        volume = data['volume']
        
        # 1. 最大回撤（5分）
        cumulative = close / close.iloc[0]
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        if max_drawdown > -0.1:
            score += 5
        elif max_drawdown > -0.2:
            score += 4
        elif max_drawdown > -0.3:
            score += 3
        elif max_drawdown > -0.4:
            score += 2
        else:
            score += 1
            
        # 2. 成交量稳定性（3分）
        vol_std = volume.iloc[-20:].std()
        vol_mean = volume.iloc[-20:].mean()
        vol_cv = vol_std / vol_mean if vol_mean > 0 else 1  # 变异系数
        
        if vol_cv < 0.3:
            score += 3
        elif vol_cv < 0.5:
            score += 2
        else:
            score += 1
            
        # 3. 价格稳定性（2分）
        price_std = close.iloc[-20:].std()
        price_mean = close.iloc[-20:].mean()
        price_cv = price_std / price_mean if price_mean > 0 else 1
        
        if price_cv < 0.1:
            score += 2
        elif price_cv < 0.2:
            score += 1
            
        return min(score, 10)
    
    def _generate_recommendation(self, score: float) -> Dict:
        """
        生成推荐建议
        
        Args:
            score: 总分
            
        Returns:
            推荐字典
        """
        if score >= 90:
            return {
                'level': '强烈推荐',
                'action': '强烈买入',
                'stars': '⭐⭐⭐⭐⭐',
                'description': '各项指标表现优异，建议重点关注'
            }
        elif score >= 80:
            return {
                'level': '推荐',
                'action': '买入',
                'stars': '⭐⭐⭐⭐',
                'description': '整体表现良好，可以考虑买入'
            }
        elif score >= 70:
            return {
                'level': '可以考虑',
                'action': '轻仓买入',
                'stars': '⭐⭐⭐',
                'description': '部分指标较好，可小仓位尝试'
            }
        elif score >= 60:
            return {
                'level': '观望',
                'action': '持有/观望',
                'stars': '⭐⭐',
                'description': '表现一般，建议观望'
            }
        else:
            return {
                'level': '不推荐',
                'action': '不建议买入',
                'stars': '⭐',
                'description': '风险较大，不建议买入'
            }
    
    def _generate_signals(self, data: pd.DataFrame) -> Dict:
        """
        生成详细交易信号
        
        Args:
            data: 股票数据
            
        Returns:
            信号字典
        """
        signals = []
        
        # MACD信号
        macd_data = MACD(data['close'])
        if macd_data['macd'].iloc[-1] > macd_data['signal'].iloc[-1]:
            if macd_data['macd'].iloc[-2] <= macd_data['signal'].iloc[-2]:
                signals.append('MACD金叉')
            else:
                signals.append('MACD多头')
        else:
            signals.append('MACD空头')
            
        # RSI信号
        rsi = RSI(data['close'], 14).iloc[-1]
        if rsi < 30:
            signals.append('RSI超卖')
        elif rsi > 70:
            signals.append('RSI超买')
        else:
            signals.append('RSI正常')
            
        # 均线信号
        ma5 = SMA(data['close'], 5).iloc[-1]
        ma20 = SMA(data['close'], 20).iloc[-1]
        if ma5 > ma20:
            signals.append('短期均线上穿')
        else:
            signals.append('短期均线下穿')
            
        # 布林带信号
        boll = BOLL(data['close'], 20)
        price = data['close'].iloc[-1]
        if price < boll['lower'].iloc[-1]:
            signals.append('跌破布林下轨')
        elif price > boll['upper'].iloc[-1]:
            signals.append('突破布林上轨')
            
        return {
            'signals': signals,
            'trend': '上涨' if data['close'].iloc[-1] > data['close'].iloc[-20] else '下跌',
            'strength': '强' if abs(data['close'].iloc[-1] / data['close'].iloc[-20] - 1) > 0.1 else '弱'
        }
