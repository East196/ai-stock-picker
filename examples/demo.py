"""
AI选股助手示例
演示如何使用AI选股助手
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import StockAnalyzer
from core.screener import StockScreener
from core.reporter import ReportGenerator
from core.data import DataManager


def single_stock_analysis():
    """单股分析示例"""
    print("\n" + "="*80)
    print("示例1: 单股分析")
    print("="*80 + "\n")
    
    # 创建分析器
    analyzer = StockAnalyzer()
    data_manager = DataManager()
    
    # 获取真实数据
    symbol = '600570'
    data = data_manager.get_data(symbol, use_real=True)
    
    # 分析
    result = analyzer.analyze(data, symbol)
    
    # 打印结果
    print(f"股票代码: {result['symbol']}")
    print(f"综合得分: {result['scores']['total']}分")
    print(f"推荐等级: {result['recommendation']['level']}")
    print(f"操作建议: {result['recommendation']['action']}")
    print(f"最新价: ¥{result['latest_price']:.2f}")
    print(f"涨跌幅: {result['price_change']:+.2f}%")
    print()
    
    # 生成报告
    reporter = ReportGenerator()
    text_report = reporter.generate_text(result)
    print(text_report)
    
    # 保存HTML报告
    html_file = reporter.generate_html(result)
    print(f"\nHTML报告已保存: {html_file}")


def batch_screening():
    """批量选股示例"""
    print("\n" + "="*80)
    print("示例2: 批量选股")
    print("="*80 + "\n")
    
    # 创建筛选器
    screener = StockScreener()
    
    # 股票池
    symbols = ['600000', '600036', '600519', '600887', '600941',
               '601318', '601398', '601939', '601988', '603259']
    
    # 筛选
    results = screener.screen(symbols, min_score=70, top_n=5)
    
    # 生成报告
    report = screener.generate_report(results)
    print(report)


def strategy_screening():
    """策略选股示例"""
    print("\n" + "="*80)
    print("示例3: 策略选股")
    print("="*80 + "\n")
    
    screener = StockScreener()
    
    symbols = ['000001', '000002', '000333', '000651', '000858']
    
    # 激进策略
    print("【激进策略】")
    aggressive = screener.screen_by_strategy(symbols, strategy='aggressive')
    for stock in aggressive[:3]:
        print(f"  {stock['symbol']}: {stock['scores']['total']}分 - {stock['recommendation']['level']}")
    
    print("\n【平衡策略】")
    balanced = screener.screen_by_strategy(symbols, strategy='balanced')
    for stock in balanced[:3]:
        print(f"  {stock['symbol']}: {stock['scores']['total']}分 - {stock['recommendation']['level']}")
    
    print("\n【保守策略】")
    conservative = screener.screen_by_strategy(symbols, strategy='conservative')
    for stock in conservative[:3]:
        print(f"  {stock['symbol']}: {stock['scores']['total']}分 - {stock['recommendation']['level']}")


def dimension_ranking():
    """维度排名示例"""
    print("\n" + "="*80)
    print("示例4: 按维度排名")
    print("="*80 + "\n")
    
    screener = StockScreener()
    
    symbols = ['600570', '600000', '600036', '600519', '600887']
    
    # 按趋势排名
    print("【趋势最强TOP3】")
    top_trend = screener.get_top_stocks_by_dimension(symbols, dimension='trend', top_n=3)
    for i, stock in enumerate(top_trend, 1):
        print(f"  {i}. {stock['symbol']}: {stock['scores']['trend']}/30")
    
    # 按量能排名
    print("\n【量能最强TOP3】")
    top_volume = screener.get_top_stocks_by_dimension(symbols, dimension='volume', top_n=3)
    for i, stock in enumerate(top_volume, 1):
        print(f"  {i}. {stock['symbol']}: {stock['scores']['volume']}/25")
    
    # 按风险排名（风险分越高越安全）
    print("\n【最安全TOP3】")
    top_risk = screener.get_top_stocks_by_dimension(symbols, dimension='risk', top_n=3)
    for i, stock in enumerate(top_risk, 1):
        print(f"  {i}. {stock['symbol']}: {stock['scores']['risk']}/10")


def main():
    """主函数"""
    print("\n" + "🤖 "*30)
    print(" "*30 + "AI选股助手")
    print(" "*30 + "演示程序")
    print("🤖 "*30)
    
    # 运行所有示例
    single_stock_analysis()
    batch_screening()
    strategy_screening()
    dimension_ranking()
    
    print("\n" + "="*80)
    print("✅ 演示完成！")
    print("="*80)


if __name__ == "__main__":
    main()
