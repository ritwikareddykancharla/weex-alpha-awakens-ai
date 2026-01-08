# WEEX AI Trading Hackathon Strategy

A production-ready AI-powered trading strategy for the WEEX Alpha Awakens hackathon.

## Features

- **AI-Powered Trend Following**: Combines ML predictions with technical indicators
- **Risk Management**: Implements Kelly Criterion, stop-loss, take-profit, daily limits
- **Multi-Asset Trading**: Supports all 8 competition pairs
- **WEEX API Integration**: Full integration with WEEX trading APIs
- **AI Logging**: Generates required logs for competition submission
- **Backtesting**: Historical data analysis and strategy validation

## Quick Start

### 1. Prerequisites
- Python 3.9+
- WEEX API credentials (after registration approval)
- Cloud server with static IP (recommended)

### 2. Installation
```bash
# Clone repository
git clone https://github.com/yourusername/weex-ai-trading.git
cd weex-ai-trading

# Install dependencies
pip install -r requirements.txt

# Install TA-LIB (technical analysis library)
# On Ubuntu/Debian:
sudo apt-get update
sudo apt-get install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
pip install TA-Lib

# On macOS:
brew install ta-lib
pip install TA-Lib
