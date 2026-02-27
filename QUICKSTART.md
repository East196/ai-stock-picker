# AI选股助手 - 快速开始

## 5分钟快速上手

### 1. 安装依赖

```bash
cd ~/wsclaw/ai-stock-picker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 运行演示

```bash
cd examples
python demo.py
```

### 3. 单股分析

```python
from core.analyzer import StockAnalyzer
from core.data import DataManager

# 创建分析器
analyzer = StockAnalyzer()
data_manager = DataManager()

# 获取数据（示例使用模拟数据）
data = data_manager.generate_sample_data('600570', days=100)

# 分析
result = analyzer.analyze(data, '600570')

# 查看结果
print(f"综合得分: {result['scores']['total']}分")
print(f"推荐等级: {result['recommendation']['level']}")
print(f"操作建议: {result['recommendation']['action']}")
```

### 4. 批量选股

```python
from core.screener import StockScreener

# 创建筛选器
screener = StockScreener()

# 股票池
symbols = ['600000', '600036', '600519', '600887', '601318']

# 筛选优质股票（得分>=70，返回前5名）
results = screener.screen(symbols, min_score=70, top_n=5)

# 打印报告
report = screener.generate_report(results)
print(report)
```

### 5. 生成HTML报告

```python
from core.reporter import ReportGenerator

# 创建报告生成器
reporter = ReportGenerator()

# 生成HTML报告
html_file = reporter.generate_html(result)
print(f"报告已保存: {html_file}")

# 生成文本报告
text_report = reporter.generate_text(result)
print(text_report)
```

## 核心功能

### 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 趋势指标 | 30% | 均线、MACD、趋势强度 |
| 量能指标 | 25% | 成交量、量价配合 |
| 波动指标 | 20% | RSI、布林带、波动率 |
| 动量指标 | 15% | 涨跌幅、连续涨跌 |
| 风险指标 | 10% | 最大回撤、流动性 |

### 推荐等级

- ⭐⭐⭐⭐⭐ (90-100分): 强烈推荐
- ⭐⭐⭐⭐ (80-89分): 推荐
- ⭐⭐⭐ (70-79分): 可以考虑
- ⭐⭐ (60-69分): 观望
- ⭐ (0-59分): 不推荐

## 使用建议

1. **先运行演示** - 理解系统如何工作
2. **准备真实数据** - 使用akshare或tushare获取
3. **调整参数** - 根据需要修改评分权重
4. **结合实际** - 不要完全依赖AI建议
5. **风险控制** - 永远做好风险管理

## 注意事项

⚠️ 本系统仅供学习研究使用
⚠️ 不构成任何投资建议
⚠️ 股市有风险，投资需谨慎

## 下一步

1. 阅读 [README.md](README.md) 了解详细功能
2. 查看 [examples/](examples/) 目录的示例代码
3. 尝试自己的股票数据
4. 根据需要调整评分算法

祝你投资顺利！📈
