# AI选股助手 - 使用指南

## 🎯 核心功能

### 1. 单股分析

分析单只股票的多维度表现：

```python
from core.analyzer import StockAnalyzer
from core.data import DataManager

# 创建分析器和数据管理器
analyzer = StockAnalyzer()
data_manager = DataManager()

# 获取数据（示例使用模拟数据）
data = data_manager.generate_sample_data('600570', days=100)

# 执行分析
result = analyzer.analyze(data, '600570')

# 查看结果
print(f"综合得分: {result['scores']['total']}分")
print(f"推荐等级: {result['recommendation']['level']}")
```

**返回结果包含：**
- `symbol`: 股票代码
- `scores`: 各维度得分（总分100）
  - `total`: 总分
  - `trend`: 趋势指标（30分）
  - `volume`: 量能指标（25分）
  - `volatility`: 波动指标（20分）
  - `momentum`: 动量指标（15分）
  - `risk`: 风险指标（10分）
- `recommendation`: 推荐建议
  - `level`: 推荐等级
  - `action`: 操作建议
  - `stars`: 星级评价
  - `description`: 详细说明
- `signals`: 技术信号列表
- `latest_price`: 最新价格
- `price_change`: 涨跌幅

---

### 2. 批量选股

从股票池中筛选优质标的：

```python
from core.screener import StockScreener

# 创建筛选器
screener = StockScreener()

# 定义股票池
symbols = ['600000', '600036', '600519', '600887', '601318']

# 筛选（得分>=70，返回前5名）
results = screener.screen(symbols, min_score=70, top_n=5)

# 生成报告
report = screener.generate_report(results)
print(report)
```

**参数说明：**
- `symbols`: 股票代码列表
- `min_score`: 最低分数阈值（默认70）
- `top_n`: 返回前N只股票（默认10）

---

### 3. 策略选股

按不同投资风格筛选：

```python
# 激进策略（追求高分，风险较高）
aggressive = screener.screen_by_strategy(symbols, strategy='aggressive')

# 平衡策略（综合考虑，风险适中）
balanced = screener.screen_by_strategy(symbols, strategy='balanced')

# 保守策略（优先考虑安全）
conservative = screener.screen_by_strategy(symbols, strategy='conservative')
```

**策略特点：**
- **激进型**: min_score=80, top_n=5，不考虑风险
- **平衡型**: min_score=70, top_n=10，过滤风险得分<6的
- **保守型**: min_score=65, top_n=15，按风险得分排序

---

### 4. 维度排名

按特定维度找最优股票：

```python
# 趋势最强
top_trend = screener.get_top_stocks_by_dimension(symbols, dimension='trend', top_n=5)

# 量能最强
top_volume = screener.get_top_stocks_by_dimension(symbols, dimension='volume', top_n=5)

# 最安全（风险分越高越安全）
top_risk = screener.get_top_stocks_by_dimension(symbols, dimension='risk', top_n=5)
```

**可用维度：**
- `total`: 综合得分
- `trend`: 趋势指标
- `volume`: 量能指标
- `volatility`: 波动指标
- `momentum`: 动量指标
- `risk`: 风险指标

---

### 5. 生成报告

#### HTML报告

```python
from core.reporter import ReportGenerator

reporter = ReportGenerator()

# 生成HTML报告
html_file = reporter.generate_html(result)
print(f"报告已保存: {html_file}")
```

**特点：**
- 美观的卡片式布局
- 分数可视化（进度条）
- 彩色编码（高分绿色，低分红色）
- 技术信号标签
- 风险提示

#### 文本报告

```python
# 生成文本报告
text_report = reporter.generate_text(result)
print(text_report)
```

**适合：**
- 命令行输出
- 日志记录
- 快速查看

---

## 📊 评分系统详解

### 趋势指标（30分）

**评分项目：**
1. **均线排列**（15分）
   - 多头排列（5>10>20>60）: 15分
   - 短期多头（5>10>20）: 12分
   - 金叉（5>10）: 8分
   - 中期多头（10>20）: 5分

2. **MACD信号**（10分）
   - 金叉: 10分
   - 多头: 7分
   - 零轴以上: 4分

3. **趋势强度**（5分）
   - 价格>20日均线: +3分
   - 价格>60日均线: +2分

### 量能指标（25分）

**评分项目：**
1. **成交量变化**（10分）
   - 放量1.5倍以上: 8分
   - 温和放量: 5分
   - 量能正常: 3分

2. **量价配合**（10分）
   - 价涨量增: 10分
   - 价涨量缩: 5分
   - 价跌量缩: 3分

3. **成交量趋势**（5分）
   - 5日连续放量: 5分
   - 量能高于平均: 3分

### 波动指标（20分）

**评分项目：**
1. **RSI**（10分）
   - 30-70正常区间: 10分
   - 20-30超卖: 8分
   - 70-80超买: 5分
   - <20严重超卖: 6分
   - >80严重超买: 3分

2. **布林带位置**（7分）
   - 跌破下轨: 7分
   - 下轨-中轨: 5分
   - 中轨-上轨: 3分
   - 突破上轨: 2分

3. **波动率**（3分）
   - 低波动（<20%）: 3分
   - 中等波动（20-30%）: 2分
   - 高波动（>30%）: 1分

### 动量指标（15分）

**评分项目：**
1. **涨跌幅**（8分）
   - 5日涨幅0-10%: 8分
   - 5日涨幅10-20%: 6分
   - 5日跌幅0-10%: 4分
   - 5日涨幅>20%: 3分
   - 5日跌幅>10%: 2分

2. **连续涨跌**（4分）
   - 2-3连涨: 4分
   - 1连涨: 3分
   - 4连涨: 2分
   - 其他: 1分

3. **突破情况**（3分）
   - 突破20日均线: 3分
   - 站稳20日均线: 2分

### 风险指标（10分）

**评分项目：**
1. **最大回撤**（5分）
   - <10%: 5分
   - 10-20%: 4分
   - 20-30%: 3分
   - 30-40%: 2分
   - >40%: 1分

2. **成交量稳定性**（3分）
   - 变异系数<0.3: 3分
   - 变异系数0.3-0.5: 2分
   - 变异系数>0.5: 1分

3. **价格稳定性**（2分）
   - 变异系数<0.1: 2分
   - 变异系数0.1-0.2: 1分

---

## 🎓 学习建议

### 初学者（第1-2周）

1. **运行演示程序**
   ```bash
   python examples/demo.py
   ```

2. **理解评分系统**
   - 阅读本指南的评分详解
   - 手动计算几只股票的得分
   - 对比AI评分和自己的判断

3. **尝试单股分析**
   - 选择熟悉的股票
   - 分析结果并记录
   - 观察后续走势验证

### 进阶用户（第3-4周）

1. **调整评分权重**
   ```python
   analyzer = StockAnalyzer()
   analyzer.weights = {
       'trend': 0.35,      # 提高趋势权重
       'volume': 0.25,
       'volatility': 0.15, # 降低波动权重
       'momentum': 0.15,
       'risk': 0.10
   }
   ```

2. **自定义评分标准**
   - 修改 `analyzer.py` 中的评分逻辑
   - 添加新的评分维度
   - 调整分数阈值

3. **集成真实数据**
   - 使用akshare获取数据
   - 保存到CSV供分析使用
   - 建立自己的股票池

### 高级用户（1个月后）

1. **机器学习增强**
   - 收集历史数据
   - 训练评分模型
   - 优化参数

2. **实盘验证**
   - 模拟盘测试
   - 记录分析结果
   - 统计准确率

3. **系统集成**
   - 结合回测框架
   - 自动化选股
   - 定时推送报告

---

## ⚠️ 重要提示

### 风险警告

1. **本系统仅供学习研究**
   - 不构成任何投资建议
   - 不保证盈利
   - 可能存在错误

2. **股市有风险**
   - 投资需谨慎
   - 历史不代表未来
   - 技术分析有局限

3. **建议结合使用**
   - 基本面分析
   - 市场环境
   - 个人风险承受能力

### 使用建议

1. **不要盲目跟从**
   - AI只是工具
   - 需要独立思考
   - 结合实际情况

2. **持续学习**
   - 理解评分逻辑
   - 学习技术指标
   - 总结经验教训

3. **风险控制**
   - 设置止损
   - 分散投资
   - 不满仓操作

---

## 🔧 常见问题

### Q: 如何获取真实数据？

A: 可以使用以下方法：
```python
import akshare as ak

# 方法1: akshare（需要安装）
df = ak.stock_zh_a_hist(symbol="600570", period="daily", 
                        start_date="20240101", end_date="20260227")

# 方法2: 从CSV导入
from core.data import DataManager
dm = DataManager()
data = dm.load_from_csv('600570.csv')
```

### Q: 如何调整评分权重？

A: 修改 `analyzer.py` 中的 `weights` 属性：
```python
analyzer = StockAnalyzer()
analyzer.weights = {
    'trend': 0.35,
    'volume': 0.25,
    'volatility': 0.15,
    'momentum': 0.15,
    'risk': 0.10
}
```

### Q: 评分为什么很低？

A: 可能原因：
1. 数据是模拟的（随机生成）
2. 市场环境不好
3. 评分标准严格
4. 需要调整参数

### Q: 如何提高准确率？

A: 建议：
1. 使用真实数据
2. 调整评分权重
3. 添加更多指标
4. 结合基本面分析
5. 长期验证优化

---

## 📚 扩展阅读

- [量化回测框架](../quant-backtest/)
- [技术指标详解](https://www.investopedia.com/)
- [Python量化投资](https://www.quantopian.com/)
- [风险管理](https://www.investopedia.com/terms/r/riskmanagement.asp)

---

**祝你投资顺利！** 📈

记住：**投资有风险，入市需谨慎！**
