#!/bin/bash

echo "🤖 AI选股助手"
echo "================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q pandas numpy jinja2

echo ""
echo "✅ 环境准备完成！"
echo ""
echo "可用的命令："
echo "  1. python examples/demo.py        # 运行完整演示"
echo "  2. python -c 'from core import *; help(StockAnalyzer)'  # 查看帮助"
echo ""
echo "快速开始："
echo "  python examples/demo.py"
echo ""
