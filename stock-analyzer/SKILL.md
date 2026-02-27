---
name: stock-analyzer
description: AI选股分析技能。当用户需要分析A股股票、获取技术指标评分、生成选股报告时使用此技能。支持单股分析和批量筛选，输入股票代码（如600570、000001），输出包含趋势、量能、波动、动量、风险五个维度的综合评分报告。
---

# AI选股分析器

## 概述

此技能提供A股技术分析能力，基于真实历史数据计算多维度评分并生成投资参考报告。数据来源为baostock，分析涵盖趋势、量能、波动、动量、风险五大维度。

## 快速开始

### 单股分析

当用户提供单个股票代码时：

```
分析 600570
```

执行步骤：
1. 调用 `scripts/analyze_stock.py 600570`
2. 输出包含综合得分、推荐等级、分项得分、技术信号

### 批量筛选

当用户提供多个股票代码时：

```
分析 600570 600036 600519
```

执行步骤：
1. 调用 `scripts/analyze_stock.py 600570 600036 600519`
2. 输出按分数排序的筛选报告

### 指定输出格式

```
分析 600570 --output html
```

生成HTML报告保存到 `reports/` 目录。

## 使用场景

| 场景 | 命令示例 |
|------|----------|
| 分析单只股票 | `分析 600570` |
| 批量筛选股票 | `分析 600000 600036 600519` |
| 生成HTML报告 | `分析 600570 -o html` |
| 筛选高分股票 | `分析 600000 600036 -m 70` |

## 评分体系

详见 `references/scoring_metrics.md`，核心要点：

| 维度 | 满分 | 说明 |
|------|------|------|
| 趋势指标 | 30 | 均线、MACD、趋势强度 |
| 量能指标 | 25 | 成交量、量价配合 |
| 波动指标 | 20 | RSI、布林带、波动率 |
| 动量指标 | 15 | 涨跌幅、连续性 |
| 风险指标 | 10 | 最大回撤、流动性 |

**推荐等级**：
- 90+ 分：强烈推荐 ⭐⭐⭐⭐⭐
- 80-89 分：推荐 ⭐⭐⭐⭐
- 70-79 分：可以考虑 ⭐⭐⭐
- 60-69 分：观望 ⭐⭐
- <60 分：不推荐 ⭐

## 代码示例

### Python直接调用

```python
from core.analyzer import StockAnalyzer
from core.data import DataManager
from core.reporter import ReportGenerator

# 初始化
analyzer = StockAnalyzer()
data_manager = DataManager()
reporter = ReportGenerator()

# 获取数据并分析
data = data_manager.get_data('600570', use_real=True)
result = analyzer.analyze(data, '600570')

# 查看结果
print(f"综合得分: {result['scores']['total']}分")
print(f"推荐等级: {result['recommendation']['level']}")

# 生成报告
report = reporter.generate_text(result)
print(report)
```

### 批量筛选

```python
from core.screener import StockScreener

screener = StockScreener()
symbols = ['600000', '600036', '600519', '600887']

# 筛选70分以上的股票
results = screener.screen(symbols, min_score=70, top_n=5)

# 生成报告
report = screener.generate_report(results)
print(report)
```

## 资源文件

- `scripts/analyze_stock.py` - 命令行分析脚本
- `references/scoring_metrics.md` - 详细评分标准说明

## 风险提示

此技能仅供学习研究使用，不构成任何投资建议。股市有风险，投资需谨慎。
