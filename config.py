"""
AI选股助手配置文件
集中管理所有配置参数
"""
from typing import Dict


# ============================================
# 评分权重配置
# ============================================
SCORE_WEIGHTS: Dict[str, float] = {
    'trend': 0.30,      # 趋势指标权重（30分）
    'volume': 0.25,     # 量能指标权重（25分）
    'volatility': 0.20, # 波动指标权重（20分）
    'momentum': 0.15,   # 动量指标权重（15分）
    'risk': 0.10        # 风险指标权重（10分）
}

# 最大得分
MAX_SCORES: Dict[str, int] = {
    'trend': 30,
    'volume': 25,
    'volatility': 20,
    'momentum': 15,
    'risk': 10
}

# ============================================
# 推荐等级阈值
# ============================================
RECOMMENDATION_THRESHOLDS = {
    'strong_buy': 90,   # 强烈推荐
    'buy': 80,          # 推荐
    'hold': 70,         # 可以考虑
    'watch': 60,        # 观望
    # < 60: 不推荐
}

# ============================================
# 技术指标参数
# ============================================
INDICATOR_PARAMS = {
    # 移动平均线
    'ma_short': 5,
    'ma_medium': 10,
    'ma_long': 20,
    'ma_very_long': 60,
    
    # MACD
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    
    # RSI
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'rsi_severe_oversold': 20,
    'rsi_severe_overbought': 80,
    
    # 布林带
    'boll_period': 20,
    'boll_std': 2,
    
    # KDJ
    'kdj_n': 9,
    'kdj_m1': 3,
    'kdj_m2': 3,
    
    # ATR
    'atr_period': 14,
}

# ============================================
# 数据参数
# ============================================
DATA_PARAMS = {
    'min_data_length': 50,       # 最小数据长度
    'default_days': 365,         # 默认获取天数
    'cache_expire_hours': 4,     # 缓存过期时间（小时）
}

# ============================================
# 筛选参数
# ============================================
SCREENING_PARAMS = {
    'default_min_score': 70,     # 默认最低分数
    'default_top_n': 10,         # 默认返回数量
    'max_workers': 5,            # 最大并行线程数
}

# ============================================
# 策略配置
# ============================================
STRATEGY_CONFIG = {
    'aggressive': {
        'min_score': 80,
        'top_n': 5,
        'min_risk_score': 0,     # 不考虑风险
    },
    'balanced': {
        'min_score': 70,
        'top_n': 10,
        'min_risk_score': 6,     # 风险分数至少6分
    },
    'conservative': {
        'min_score': 65,
        'top_n': 15,
        'min_risk_score': 7,     # 风险分数至少7分
        'sort_by_risk': True,    # 按风险排序
    }
}

# ============================================
# 日志配置
# ============================================
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}
