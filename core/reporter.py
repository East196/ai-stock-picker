"""
报告生成器
生成HTML和文本格式的分析报告
"""
from jinja2 import Template
from datetime import datetime
from typing import Dict, List
import os


class ReportGenerator:
    """
    报告生成器
    """
    
    def __init__(self, output_dir: str = None):
        """
        初始化
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), '../reports')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_html(self, result: Dict, filename: str = None) -> str:
        """
        生成HTML报告
        
        Args:
            result: 分析结果
            filename: 文件名
            
        Returns:
            文件路径
        """
        if not filename:
            filename = f"report_{result['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
        filepath = os.path.join(self.output_dir, filename)
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI选股助手 - {{ symbol }} 分析报告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .score-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .total-score {
            font-size: 48px;
            font-weight: bold;
            color: {{ 'green' if scores.total >= 80 else 'orange' if scores.total >= 70 else 'red' }};
        }
        .score-bar {
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            margin: 10px 0;
        }
        .score-fill {
            height: 100%;
            background: {{ 'green' if scores.total >= 80 else 'orange' if scores.total >= 70 else 'red' }};
            border-radius: 10px;
            width: {{ scores.total }}%;
        }
        .dimension {
            margin: 10px 0;
        }
        .dimension-label {
            display: flex;
            justify-content: space-between;
        }
        .recommendation {
            background: {{ '#e8f5e9' if recommendation.level != '不推荐' else '#ffebee' }};
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .stars {
            font-size: 24px;
        }
        .signals {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .signal-tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            margin: 5px;
        }
        .warning {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI选股助手</h1>
        <p>股票代码: {{ symbol }}</p>
        <p>分析时间: {{ analyze_time }}</p>
    </div>
    
    <div class="score-card">
        <h2>综合评分</h2>
        <div class="total-score">{{ scores.total }}</div>
        <div class="score-bar">
            <div class="score-fill"></div>
        </div>
        <div class="stars">{{ recommendation.stars }}</div>
        
        <h3>分项得分</h3>
        <div class="dimension">
            <div class="dimension-label">
                <span>趋势指标</span>
                <span>{{ scores.trend }}/30</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {{ scores.trend / 30 * 100 }}%; background: #4CAF50;"></div>
            </div>
        </div>
        
        <div class="dimension">
            <div class="dimension-label">
                <span>量能指标</span>
                <span>{{ scores.volume }}/25</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {{ scores.volume / 25 * 100 }}%; background: #2196F3;"></div>
            </div>
        </div>
        
        <div class="dimension">
            <div class="dimension-label">
                <span>波动指标</span>
                <span>{{ scores.volatility }}/20</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {{ scores.volatility / 20 * 100 }}%; background: #FF9800;"></div>
            </div>
        </div>
        
        <div class="dimension">
            <div class="dimension-label">
                <span>动量指标</span>
                <span>{{ scores.momentum }}/15</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {{ scores.momentum / 15 * 100 }}%; background: #9C27B0;"></div>
            </div>
        </div>
        
        <div class="dimension">
            <div class="dimension-label">
                <span>风险指标</span>
                <span>{{ scores.risk }}/10</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {{ scores.risk / 10 * 100 }}%; background: #F44336;"></div>
            </div>
        </div>
    </div>
    
    <div class="recommendation">
        <h3>💡 投资建议</h3>
        <p><strong>推荐等级:</strong> {{ recommendation.level }}</p>
        <p><strong>操作建议:</strong> {{ recommendation.action }}</p>
        <p><strong>详细说明:</strong> {{ recommendation.description }}</p>
        <p><strong>最新价:</strong> ¥{{ latest_price }}</p>
        <p><strong>涨跌幅:</strong> {{ price_change }}%</p>
    </div>
    
    <div class="signals">
        <h3>📊 技术信号</h3>
        {% for signal in signals.signals %}
        <span class="signal-tag">{{ signal }}</span>
        {% endfor %}
        <p><strong>趋势:</strong> {{ signals.trend }}</p>
        <p><strong>强度:</strong> {{ signals.strength }}</p>
    </div>
    
    <div class="warning">
        ⚠️ <strong>风险提示:</strong> 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。
    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #999;">
        <p>AI选股助手 v1.0 | 由AI驱动</p>
    </footer>
</body>
</html>
        """
        
        template = Template(html_template)
        html = template.render(**result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return filepath
    
    def generate_text(self, result: Dict) -> str:
        """
        生成文本报告
        
        Args:
            result: 分析结果
            
        Returns:
            报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("AI选股助手 - 分析报告")
        lines.append("=" * 80)
        lines.append(f"股票代码: {result['symbol']}")
        lines.append(f"分析时间: {result['analyze_time']}")
        lines.append("")
        
        scores = result['scores']
        rec = result['recommendation']
        
        lines.append(f"综合得分: {scores['total']}分 {rec['stars']}")
        lines.append(f"推荐等级: {rec['level']}")
        lines.append(f"操作建议: {rec['action']}")
        lines.append(f"最新价: ¥{result['latest_price']:.2f}")
        lines.append(f"涨跌幅: {result['price_change']:+.2f}%")
        lines.append("")
        
        lines.append("分项得分:")
        lines.append(f"  趋势指标: {scores['trend']}/30")
        lines.append(f"  量能指标: {scores['volume']}/25")
        lines.append(f"  波动指标: {scores['volatility']}/20")
        lines.append(f"  动量指标: {scores['momentum']}/15")
        lines.append(f"  风险指标: {scores['risk']}/10")
        lines.append("")
        
        lines.append("技术信号:")
        for signal in result['signals']['signals']:
            lines.append(f"  - {signal}")
        lines.append("")
        
        lines.append(f"分析建议: {rec['description']}")
        lines.append("")
        lines.append("=" * 80)
        lines.append("⚠️  风险提示: 本报告仅供参考，不构成投资建议")
        lines.append("=" * 80)
        
        return "\n".join(lines)
