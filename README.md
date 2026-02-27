# AI Stock Picker - AI选股助手

[![GitHub stars](https://img.shields.io/github/stars/East196/ai-stock-picker.svg?style=social&label=Star&maxAge=2592000)](https://github.com/East196/ai-stock-picker)
[![GitHub forks](https://img.shields.io/github/forks/East196/ai-stock-picker.svg?style=social&label=Fork&maxAge=2592000)](https://github.com/East196/ai-stock-picker)
[![GitHub issues](https://img.shields.io/github/issues/East196/ai-stock-picker.svg)](https://github.com/East196/ai-stock-picker/issues)
[![GitHub license](https://img.shields.io/github/license/East196/ai-stock-picker.svg)](https://github.com/East196/ai-stock-picker/blob/master/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![量化交易](https://img.shields.io/badge/领域-量化交易-brightgreen.svg)]()

> 🤖 基于多维度技术指标分析的智能选股系统

**[English](#english)** | **[中文](#中文)**

---

<a name="中文"></a>
## 📖 中文文档

### ✨ 核心特性

- 🎯 **100分制多因子评分** - 5维度综合评估
- 📊 **批量选股** - 支持激进/平衡/保守策略
- 📈 **8个技术指标** - SMA/MACD/RSI/BOLL/KDJ/ATR/OBV
- 📝 **HTML可视化报告** - 专业的分析报告生成
- 🔄 **智能筛选** - 多种投资风格自动适配
- ⚡ **易于扩展** - 模块化设计，方便定制

### 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/East196/ai-stock-picker.git
cd ai-stock-picker

# 安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# 运行演示
python examples/demo.py
```

### 📊 评分系统（100分制）

| 维度 | 权重 | 满分 | 评分内容 |
|------|------|------|----------|
| **趋势指标** | 30% | 30 | 均线排列、MACD、趋势强度 |
| **量能指标** | 25% | 25 | 成交量、量价配合、资金流 |
| **波动指标** | 20% | 20 | RSI、布林带、波动率 |
| **动量指标** | 15% | 15 | 涨跌幅、连续涨跌、突破 |
| **风险指标** | 10% | 10 | 最大回撤、流动性、稳定性 |

### ⭐ 推荐等级

- **90-100分** 🔴 强烈推荐
- **80-89分** 🟡 推荐买入
- **70-79分** 🟢 可以考虑
- **60-69分** ⚪ 观望
- **0-59分** ⭕ 不推荐

### 🤝 相关项目

- [quant-backtest](https://github.com/East196/quant-backtest) - 量化回测框架
- [quant-pipeline](https://github.com/East196/quant-pipeline) - 量化交易流水线

---

<a name="english"></a>
## 📖 English Documentation

### ✨ Key Features

- 🎯 **100-Point Multi-Factor Scoring** - 5 dimensions
- 📊 **Batch Stock Screening** - Multiple strategies
- 📈 **8 Technical Indicators** - SMA/MACD/RSI/BOLL/KDJ/ATR/OBV
- 📝 **HTML Reports** - Professional analysis
- 🔄 **Smart Filtering** - Investment style matching
- ⚡ **Easy to Extend** - Modular design

---

## 📄 License

MIT License

## ⚠️ Disclaimer

This system is for educational purposes only and does not constitute investment advice.

---

**If this project helps you, please give it a ⭐ Star!**
