# AI Stock Picker - AI选股助手

基于技术指标和数据分析的智能选股系统。

## 特性

- ✅ 多维度技术指标分析
- ✅ AI智能评分系统
- ✅ 买卖信号推荐
- ✅ 风险评估
- ✅ 支持批量选股
- ✅ 详细的分析报告

## 快速开始

```bash
cd ~/wsclaw/ai-stock-picker
source venv/bin/activate
python examples/analyze_stock.py
```

## 功能

### 1. 单股分析
```python
from core.analyzer import StockAnalyzer

analyzer = StockAnalyzer()
result = analyzer.analyze('600570')
print(result['recommendation'])
```

### 2. 批量选股
```python
from core.screener import StockScreener

screener = StockScreener()
stocks = screener.screen(['600570', '000001', '000002'])
print(stocks)
```

### 3. 生成报告
```python
from core.reporter import ReportGenerator

reporter = ReportGenerator()
reporter.generate(result, 'report.html')
```

## 评分系统

AI选股助手基于以下维度评分（0-100分）：

1. **趋势指标** (30分)
   - 均线排列
   - MACD信号
   - 趋势强度

2. **量能指标** (25分)
   - 成交量变化
   - 量价配合
   - 资金流向

3. **波动指标** (20分)
   - RSI超买超卖
   - 布林带位置
   - 波动率

4. **动量指标** (15分)
   - 涨跌幅
   - 连续涨跌天数
   - 突破情况

5. **风险指标** (10分)
   - 最大回撤
   - 换手率
   - 流动性

## 推荐等级

- **90-100分**: 强烈推荐买入 ⭐⭐⭐⭐⭐
- **80-89分**: 推荐买入 ⭐⭐⭐⭐
- **70-79分**: 可以考虑 ⭐⭐⭐
- **60-69分**: 观望 ⭐⭐
- **0-59分**: 不推荐 ⭐

## 注意事项

⚠️ 本系统仅供学习参考，不构成投资建议
⚠️ 股市有风险，投资需谨慎
⚠️ 建议结合基本面分析和市场环境

## License

MIT
