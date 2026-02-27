"""
AI选股分析器
基于多维度技术指标进行智能评分和推荐
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

from utils.indicators import SMA, EMA, MACD, RSI, BOLL, ATR

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockAnalyzer:
    """
    股票分析器
    
    基于技术指标进行多维度分析并生成AI评分
    """
    
    # 评分权重配置
    WEIGHTS = {
        'trend': 0.30,      # 趋势指标权重
        'volume': 0.25,     # 量能指标权重
        'volatility': 0.20, # 波动指标权重
        'momentum': 0.15,   # 动量指标权重
        'risk': 0.10        # 风险指标权重
    }
    
    # 最小数据要求
    MIN_DATA_LENGTH = 50
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        初始化分析器
        
        Args:
            weights: 自定义权重配置
        """
        if weights:
            self.weights = {**self.WEIGHTS, **weights}
        else:
            self.weights = self.WEIGHTS
        
    def analyze(self, data: pd.DataFrame, symbol: str = None) -> Dict:
        """
        分析股票数据
        
        Args:
            data: 股票数据（OHLCV格式）
            symbol: 股票代码
            
        Returns:
            分析结果字典
            
        Raises:
            ValueError: 数据不足时
        """
        # 数据校验
        if data is None or len(data) < self.MIN_DATA_LENGTH:
            raise ValueError(f"数据不足，至少需要{self.MIN_DATA_LENGTH}天的数据，当前{len(data) if data is not None else 0}天")
        
        # 确保数据按日期排序
        data = data.sort_index()
            
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
        
        # 获取最新价格信息
        latest_price = float(data['close'].iloc[-1])
        prev_price = float(data['close'].iloc[-2]) if len(data) > 1 else latest_price
        price_change = (latest_price / prev_price - 1) * 100
        
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
            'latest_price': latest_price,
            'price_change': round(price_change, 2)
        }
    
    def _safe_get(self, series: pd.Series, index: int = -1, default: float = 0) -> float:
        """
        安全获取 Series 值
        
        Args:
            series: 数据序列
            index: 索引（支持负数）
            default: 默认值
            
        Returns:
            值或默认值
        """
        try:
            if series is None or len(series) == 0:
                return default
            if abs(index) > len(series):
                return default
            val = series.iloc[index]
            return val if not pd.isna(val) else default
        except (IndexError, KeyError):
            return default
    
    def _analyze_trend(self, data: pd.DataFrame) -> float:
        """
        分析趋势指标（30分）
        
        评分标准：
        - 均线排列（多头/空头）
        - MACD信号
        - 趋势强度
        """
        score = 0
        close = data['close']
        
        # 1. 均线排列（15分）
        ma5 = SMA(close, 5)
        ma10 = SMA(close, 10)
        ma20 = SMA(close, 20)
        ma60 = SMA(close, 60)
        
        ma5_val = self._safe_get(ma5)
        ma10_val = self._safe_get(ma10)
        ma20_val = self._safe_get(ma20)
        ma60_val = self._safe_get(ma60)
        
        # 多头排列
        if ma5_val > ma10_val > ma20_val > ma60_val:
            score += 15
        elif ma5_val > ma10_val > ma20_val:
            score += 12
        elif ma5_val > ma10_val:
            score += 8
        elif ma10_val > ma20_val:
            score += 5
            
        # 2. MACD信号（10分）
        macd_data = MACD(close)
        macd = macd_data['macd']
        signal = macd_data['signal']
        
        macd_val = self._safe_get(macd)
        signal_val = self._safe_get(signal)
        macd_prev = self._safe_get(macd, -2)
        signal_prev = self._safe_get(signal, -2)
        
        # 金叉
        if macd_val > signal_val and macd_prev <= signal_prev:
            score += 10
        elif macd_val > signal_val:
            score += 7
        elif macd_val > 0:
            score += 4
            
        # 3. 趋势强度（5分）
        price = self._safe_get(close)
        if price > ma20_val:
            score += 3
        if price > ma60_val:
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
        
        vol_now = self._safe_get(volume)
        vol_ma5_val = self._safe_get(vol_ma5)
        vol_ma20_val = self._safe_get(vol_ma20)
        
        # 放量
        if vol_ma5_val > 0 and vol_now > vol_ma5_val * 1.5:
            score += 8
        elif vol_ma5_val > 0 and vol_now > vol_ma5_val:
            score += 5
        elif vol_ma20_val > 0 and vol_now > vol_ma20_val:
            score += 3
            
        # 2. 量价配合（10分）
        price_up = close.iloc[-1] > close.iloc[-2]
        volume_up = volume.iloc[-1] > volume.iloc[-2]
        
        if price_up and volume_up:
            score += 10  # 价涨量增，好
        elif not price_up and not volume_up:
            score += 7   # 价跌量缩，也不错（缩量回调）
        elif price_up and not volume_up:
            score += 5   # 价涨量缩，一般
        else:
            score += 2   # 价跌量增，不好
            
        # 3. 成交量趋势（5分）
        if len(volume) >= 5:
            recent_vol = volume.iloc[-5:]
            if all(recent_vol.iloc[i] < recent_vol.iloc[i+1] for i in range(len(recent_vol)-1)):
                score += 5
            elif vol_ma20_val > 0 and vol_now > vol_ma20_val:
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
        rsi_value = self._safe_get(rsi)
        
        if 30 <= rsi_value <= 70:
            score += 10  # 正常区间
        elif 20 <= rsi_value < 30:
            score += 9   # 超卖区间（买入机会）
        elif 70 < rsi_value <= 80:
            score += 6   # 超买区间
        elif rsi_value < 20:
            score += 8   # 严重超卖（更好的买点）
        elif rsi_value > 80:
            score += 3   # 严重超买
            
        # 2. 布林带位置（7分）
        boll = BOLL(close, 20)
        upper = self._safe_get(boll['upper'])
        lower = self._safe_get(boll['lower'])
        middle = self._safe_get(boll['middle'])
        price = self._safe_get(close)
        
        if price < lower:
            score += 7  # 跌破下轨（超卖，买入机会）
        elif lower <= price < middle:
            score += 5  # 下轨和中轨之间
        elif middle <= price < upper:
            score += 4  # 中轨和上轨之间
        else:
            score += 2  # 突破上轨（超买）
            
        # 3. 波动率（3分）
        returns = close.pct_change()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        if not pd.isna(volatility):
            if volatility < 0.2:
                score += 3
            elif volatility < 0.3:
                score += 2
            else:
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
        if len(close) >= 5:
            change_5d = (close.iloc[-1] / close.iloc[-5] - 1) * 100
            
            if 0 < change_5d <= 10:
                score += 8
            elif 10 < change_5d <= 20:
                score += 6
            elif -10 < change_5d <= 0:
                score += 5  # 小幅回调也可以
            elif change_5d > 20:
                score += 4  # 涨太多要小心
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
        ma20_val = self._safe_get(ma20)
        ma20_prev = self._safe_get(ma20, -2)
        price = self._safe_get(close)
        price_prev = self._safe_get(close, -2)
        
        # 突破20日均线
        if price > ma20_val and price_prev <= ma20_prev:
            score += 3
        elif price > ma20_val:
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
        if len(volume) >= 20:
            vol_std = volume.iloc[-20:].std()
            vol_mean = volume.iloc[-20:].mean()
            vol_cv = vol_std / vol_mean if vol_mean > 0 else 1
            
            if vol_cv < 0.3:
                score += 3
            elif vol_cv < 0.5:
                score += 2
            else:
                score += 1
            
        # 3. 价格稳定性（2分）
        if len(close) >= 20:
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
        close = data['close']
        
        # MACD信号
        macd_data = MACD(close)
        macd_val = self._safe_get(macd_data['macd'])
        signal_val = self._safe_get(macd_data['signal'])
        macd_prev = self._safe_get(macd_data['macd'], -2)
        signal_prev = self._safe_get(macd_data['signal'], -2)
        
        if macd_val > signal_val:
            if macd_prev <= signal_prev:
                signals.append('MACD金叉')
            else:
                signals.append('MACD多头')
        else:
            signals.append('MACD空头')
            
        # RSI信号
        rsi = self._safe_get(RSI(close, 14))
        if rsi < 30:
            signals.append('RSI超卖')
        elif rsi > 70:
            signals.append('RSI超买')
        else:
            signals.append('RSI正常')
            
        # 均线信号
        ma5 = self._safe_get(SMA(close, 5))
        ma20 = self._safe_get(SMA(close, 20))
        if ma5 > ma20:
            signals.append('短期均线上穿')
        else:
            signals.append('短期均线下穿')
            
        # 布林带信号
        boll = BOLL(close, 20)
        price = self._safe_get(close)
        lower = self._safe_get(boll['lower'])
        upper = self._safe_get(boll['upper'])
        
        if price < lower:
            signals.append('跌破布林下轨')
        elif price > upper:
            signals.append('突破布林上轨')
        
        # 趋势判断
        if len(close) >= 20:
            trend = '上涨' if close.iloc[-1] > close.iloc[-20] else '下跌'
            strength = '强' if abs(close.iloc[-1] / close.iloc[-20] - 1) > 0.1 else '弱'
        else:
            trend = '未知'
            strength = '未知'
            
        return {
            'signals': signals,
            'trend': trend,
            'strength': strength
        }
