#!/usr/bin/env python3
"""
AI选股分析脚本
用法: python analyze_stock.py <股票代码> [--output html|text]
"""
import sys
import os

# 添加项目根目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from core.analyzer import StockAnalyzer
from core.data import DataManager
from core.reporter import ReportGenerator


def analyze_stock(symbol: str, output_format: str = "text") -> dict:
    """
    分析单只股票

    Args:
        symbol: 股票代码（如 600570, 000001）
        output_format: 输出格式 (text 或 html)

    Returns:
        分析结果字典
    """
    # 初始化组件
    analyzer = StockAnalyzer()
    data_manager = DataManager()
    reporter = ReportGenerator()

    # 获取真实数据
    print(f"正在获取 {symbol} 的数据...")
    data = data_manager.get_data(symbol, use_real=True)

    # 执行分析
    print(f"正在分析 {symbol}...")
    result = analyzer.analyze(data, symbol)

    # 生成报告
    if output_format == "html":
        output = reporter.generate_html(result)
        print(f"\nHTML报告已保存: {output}")
    else:
        output = reporter.generate_text(result)
        print(output)

    return result


def analyze_multiple(symbols: list, min_score: float = 0) -> list:
    """
    批量分析多只股票

    Args:
        symbols: 股票代码列表
        min_score: 最低分数过滤

    Returns:
        分析结果列表
    """
    from core.screener import StockScreener

    screener = StockScreener()
    results = screener.screen(symbols, min_score=min_score, top_n=len(symbols))

    if results:
        report = screener.generate_report(results)
        print(report)
    else:
        print("未找到符合条件的股票")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AI选股分析工具")
    parser.add_argument("symbols", nargs="+", help="股票代码（支持多个）")
    parser.add_argument("--output", "-o", choices=["text", "html"], default="text",
                        help="输出格式")
    parser.add_argument("--min-score", "-m", type=float, default=0,
                        help="最低分数过滤（批量分析时）")

    args = parser.parse_args()

    if len(args.symbols) == 1:
        analyze_stock(args.symbols[0], args.output)
    else:
        analyze_multiple(args.symbols, args.min_score)


if __name__ == "__main__":
    main()
