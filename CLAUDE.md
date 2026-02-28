# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Stock Picker (AI选股助手) - An intelligent A-share stock screening system based on multi-dimensional technical indicator analysis. The system evaluates stocks using a 100-point scoring system across 5 dimensions: trend (30%), volume (25%), volatility (20%), momentum (15%), and risk (10%).

## Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run demo
python examples/demo.py

# Analyze single stock (CLI)
python stock-analyzer/scripts/analyze_stock.py 600570

# Analyze multiple stocks
python stock-analyzer/scripts/analyze_stock.py 600570 600036 600519

# Generate HTML report
python stock-analyzer/scripts/analyze_stock.py 600570 -o html

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_analyzer.py -v
```

## Architecture

```
ai-stock-picker/
├── config.py              # Centralized configuration (weights, thresholds, parameters)
├── core/
│   ├── analyzer.py        # StockAnalyzer - multi-dimensional scoring engine
│   ├── data.py            # DataManager - baostock data fetching with fallback to simulated data
│   ├── screener.py        # StockScreener - batch analysis with parallel execution & caching
│   └── reporter.py        # ReportGenerator - HTML/text report generation
├── utils/
│   └── indicators.py      # Technical indicators (SMA, EMA, MACD, RSI, BOLL, KDJ, ATR, OBV, VWAP)
├── stock-analyzer/        # Claude skill module for stock analysis
└── tests/                 # Unit tests (pytest)
```

## Core Components

### StockAnalyzer (`core/analyzer.py`)
- Main scoring engine that analyzes OHLCV data
- Requires minimum 50 days of data
- Returns: scores (total + 5 dimensions), recommendation, signals, price info

### DataManager (`core/data.py`)
- Fetches real A-share data from baostock (free, no API key required)
- Thread-safe login handling for concurrent requests
- Falls back to simulated data if real data unavailable

### StockScreener (`core/screener.py`)
- Parallel batch screening with ThreadPoolExecutor
- JSON caching with 4-hour expiration
- Strategy presets: aggressive (80+), balanced (70+), conservative (65+ with risk filter)

## Scoring System

| Dimension | Max | Indicators |
|-----------|-----|------------|
| Trend | 30 | MA alignment, MACD, price vs MA |
| Volume | 25 | Volume change, price-volume correlation |
| Volatility | 20 | RSI, Bollinger Band position |
| Momentum | 15 | 5-day change, consecutive up days |
| Risk | 10 | Max drawdown, volume stability |

Recommendation thresholds: 90+ (strong buy), 80+ (buy), 70+ (consider), 60+ (watch), <60 (avoid)

## Configuration

All tunable parameters are in `config.py`:
- `SCORE_WEIGHTS` - dimension weights
- `INDICATOR_PARAMS` - MA periods, MACD/RSI/BOLL parameters
- `RECOMMENDATION_THRESHOLDS` - score cutoffs
- `STRATEGY_CONFIG` - preset strategy parameters

## Data Flow

1. `DataManager.get_data(symbol)` fetches OHLCV from baostock
2. `StockAnalyzer.analyze(data, symbol)` computes scores
3. `ReportGenerator.generate_html/text(result)` formats output
4. For batch: `StockScreener.screen(symbols)` parallelizes analysis

## Stock Code Format

A-share codes without prefix: `600570` (Shanghai), `000001` (Shenzhen). The DataManager adds `sh.` or `sz.` prefix automatically.
