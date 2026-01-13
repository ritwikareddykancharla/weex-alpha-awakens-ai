# WEEX AI Trading Hackathon Strategy

## 🏆 Complete Setup Canvas for "AI Wars: WEEX Alpha Awakens"

### 📋 **Project Overview**
A production-ready AI-powered trading system for the WEEX Alpha Awakens competition, featuring:
- **AI Trend Following**: Gradient Boosting + technical indicators
- **Competition Compliance**: Full WEEX API integration, AI logging
- **Risk Management**: Kelly Criterion, dynamic stop-loss, daily limits
- **8 Trading Pairs**: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, LTC

### 🚀 **Immediate Next Steps**
1. **Complete Registration**: Submit BUIDL on WEEX platform with your cloud server IP
2. **API Testing**: Pass mandatory ~10 USDT test trade on `cmt_btcusdt`
3. **Deploy to Cloud**: Set up 24/7 operation on AWS/Azure/Alibaba Cloud
4. **Monitor AI Logs**: Ensure proper log generation for competition verification

---

## 🛠 **Complete Cloud Server Setup Guide**

### **Step 1: Launch Cloud Instance**
Recommended: **Amazon Linux 2023** (Stable, optimized for AWS) or Ubuntu 22.04.
Connect via SSH:
```bash
ssh -i "your-key.pem" ec2-user@your-server-ip
```

### **Step 2: System Initialization (Amazon Linux 2023)**
For Ubuntu, replace `dnf` with `apt` and package names accordingly.

```bash
# Update system
sudo dnf update -y

# Install essential packages
sudo dnf install -y git python3-pip python3-devel gcc
# (Optional) Install tmux/htop if available in repositories
sudo dnf install -y tmux htop
```

### **Step 3: Install TA-LIB (Required for Technical Indicators)**
```bash
# Install TA-LIB dependencies
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
pip install TA-Lib
```

### **Step 4: Clone and Setup Project**
```bash
# Clone your repository
git clone https://github.com/ritwikareddykancharla/weex-alpha-awakens-ai.git
cd weex-alpha-awakens-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 5: Configure Environment**
```bash
# Copy and edit configuration
cp .env.example .env
nano .env

# Add your WEEX API credentials (after registration approval):
WEEX_API_KEY=your_api_key_here
WEEX_SECRET_KEY=your_secret_key_here
WEEX_PASSPHRASE=your_passphrase_here

# Important: Use this IP for WEEX registration
curl https://ipinfo.io/ip
```

### **Step 6: Setup as System Service (24/7 Operation)**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/weex-trading.service
```

Add this service configuration:
```ini
[Unit]
Description=WEEX AI Trading Bot
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=ec2-user  # CHANGE THIS (use 'ubuntu' for Ubuntu, 'ec2-user' for Amazon Linux)
WorkingDirectory=/home/ec2-user/weex-alpha-awakens-ai
Environment="PATH=/home/ec2-user/weex-alpha-awakens-ai/venv/bin"
ExecStart=/home/ec2-user/weex-alpha-awakens-ai/venv/bin/python src/main.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=weex-trading

[Install]
WantedBy=multi-user.target
```

### **Step 7: Start and Monitor**
```bash
# Enable service
sudo systemctl daemon-reload
sudo systemctl enable weex-trading.service
sudo systemctl start weex-trading.service

# Check status
sudo systemctl status weex-trading.service

# Monitor logs
sudo journalctl -u weex-trading.service -f --since "5 minutes ago"

# View AI logs (competition requirement)
tail -f logs/ai_trading.log
```

---

## 📊 **Model Training & Strategy Development**

### **Initial Model Training**
```bash
# Train the AI model with historical data
python scripts/train_model.py

# Expected output:
# - models/trend_classifier.pkl (trained model)
# - models/scaler.pkl (feature scaler)
# - Training accuracy report
```

### **Training Configuration**
Modify `config/settings.py` for different behaviors:
```python
# Adjust these parameters based on testing:

# Risk Management
MAX_LEVERAGE = 5  # Start conservative (max allowed: 20)
DAILY_LOSS_LIMIT = 0.05  # 5% daily loss limit
STOP_LOSS_PCT = 0.02  # 2% stop loss

# AI Model
CONFIDENCE_THRESHOLD = 0.65  # Minimum confidence to trade
LOOKBACK_PERIOD = 100  # Candles for analysis

# Trading Frequency
MIN_TRADE_AMOUNT = 10.0  # USDT minimum per trade
```

### **Backtesting Your Strategy**
```bash
# Run backtest on historical data
python scripts/backtest.py --symbol cmt_btcusdt --days 30 --initial-capital 1000

# Analyze results:
# - Total Return %
# - Sharpe Ratio
# - Max Drawdown
# - Win Rate
# - Number of Trades
```

### **Paper Trading (Critical Step)**
```bash
# 1. Enable test mode in config/settings.py:
USE_TESTNET = True  # Use test environment

# 2. Run in observation mode first:
python scripts/paper_trade.py --observe-only --duration 24h

# 3. Validate:
# - API connectivity
# - Order execution
# - AI log generation
# - Risk management rules
```

---

## 🏗️ **Project Structure & Key Files**

```
weex-alpha-awakens-ai/
├── src/
│   ├── api/
│   │   ├── weex_client.py          # WEEX API wrapper (MOST IMPORTANT)
│   │   └── auth.py                 # Authentication & signing
│   ├── strategy/
│   │   ├── ai_trend_follower.py    # Main trading logic
│   │   ├── risk_manager.py         # Risk management (KEY FOR COMPETITION)
│   │   └── signals/ai_model.py     # AI/ML predictions
│   ├── utils/
│   │   └── logger.py              # AI log generator (REQUIRED BY WEEX)
│   └── main.py                    # Entry point
├── config/
│   └── settings.py                # All tunable parameters
├── models/                        # Trained AI models
├── scripts/
│   ├── train_model.py            # Model training
│   ├── backtest.py               # Historical testing
│   └── paper_trade.py            # Live testing without real money
├── logs/                         # AI logs (competition requirement)
├── tests/                        # Unit tests
└── requirements.txt             # Python dependencies
```

### **Critical Files for Competition Compliance**

1. **`src/utils/logger.py`** - Generates AI logs in WEEX required format
2. **`src/api/weex_client.py`** - Handles all API communication
3. **`src/strategy/risk_manager.py`** - Enforces competition rules (leverage limits, etc.)
4. **`logs/ai_trading.log`** - Output file for competition verification

---

## 🎯 **Competition-Specific Configuration**

### **Minimum Requirements Check**
Ensure your strategy meets these competition rules:

```python
# In risk_manager.py, these validations are enforced:

1. Minimum 10 trades: strategy must be active enough
2. Maximum 20x leverage: code enforces conservative 5x default
3. No gambling-style trading: risk limits prevent overexposure
4. AI logs generated: automatic logging for verification
```

### **Performance Optimization for 2-Week Preliminary**
```python
# Optimize for short competition period:

# 1. Increase trading frequency (but maintain quality)
MIN_TRADE_AMOUNT = 15.0  # Slightly higher minimum
CONFIDENCE_THRESHOLD = 0.60  # Accept slightly lower confidence

# 2. Aggressive but controlled risk
DAILY_LOSS_LIMIT = 0.08  # 8% daily (higher for competition)
TAKE_PROFIT_RATIO = 1.5  # 1:1.5 risk-reward (faster exits)

# 3. Monitor all 8 pairs actively
TRADING_PAIRS = [
    "cmt_btcusdt", "cmt_ethusdt", "cmt_bnbusdt",
    "cmt_solusdt", "cmt_xrpusdt", "cmt_adausdt",
    "cmt_dogeusdt", "cmt_ltcusdt"
]
```

### **AI Log Verification (Mandatory)**
```bash
# Check your AI logs meet WEEX requirements:
python -c "
from src.utils.logger import AILogger
logger = AILogger()
summary = logger.get_log_summary()
print('Log Summary:', summary)
"

# Expected output includes:
# - Total entries
# - Number of signals
# - Number of orders (must be ≥10)
# - Error count
```

---

## 🔧 **Testing & Validation Checklist**

### **Pre-Competition Testing**
```bash
# Run complete test suite
pytest tests/ -v

# Test individual components:
python -m pytest tests/test_api.py -v           # API connectivity
python -m pytest tests/test_strategy.py -v      # Strategy logic
python -m pytest tests/test_risk.py -v          # Risk management
python -m pytest tests/test_logger.py -v        # AI logging
```

### **API Connectivity Test**
```bash
# Manual API test (same as competition requirement):
python scripts/test_api_connection.py

# Should output:
# [✓] API Connection Successful
# [✓] Authentication Working
# [✓] Can Fetch Market Data
# [✓] Can Place/Cancel Orders
# [✓] AI Logs Being Generated
```

### **Performance Metrics Monitoring**
```bash
# Monitor strategy performance
python scripts/performance_monitor.py --interval 1h

# Key metrics to track:
# - Daily P&L
# - Win Rate
# - Sharpe Ratio
# - Maximum Drawdown
# - Number of Trades (ensure ≥10)
```

---

## 🚀 **Deployment Workflow for Competition**

### **Phase 1: Preparation (Before Jan 18)**
1. ✅ Clone and setup project on cloud server
2. ✅ Complete WEEX registration with server IP
3. ✅ Pass API test (~10 USDT trade)
4. ✅ Train initial AI models
5. ✅ Run backtests on all 8 pairs

### **Phase 2: Paper Trading (Jan 19-21)**
1. Run strategy in observation mode
2. Verify AI log generation
3. Adjust parameters based on live market
4. Ensure 24/7 uptime

### **Phase 3: Competition (Jan 19 - Feb 2)**
1. Start with conservative settings
2. Monitor logs hourly
3. Check daily: P&L, trade count, risk metrics
4. Be ready to intervene if needed

### **Emergency Procedures**
```bash
# If something goes wrong:

# 1. Check status
sudo systemctl status weex-trading.service

# 2. View recent errors
sudo journalctl -u weex-trading.service --since "1 hour ago" | grep ERROR

# 3. Restart if needed
sudo systemctl restart weex-trading.service

# 4. Check API connectivity
curl -s "https://api-contract.weex.com/capi/v2/market/time"

# 5. Verify AI logs are still being written
tail -n 5 logs/ai_trading.log
```

---

## 📈 **Strategy Improvements & Next Steps**

### **Short-term Improvements (During Competition)**
1. **Dynamic Parameter Adjustment**
   ```python
   # In risk_manager.py, add market-condition based adjustments:
   def adjust_for_volatility(self, current_volatility):
       if current_volatility > 0.03:  # High volatility
           self.STOP_LOSS_PCT *= 1.5
           self.POSITION_SIZE *= 0.7
   ```

2. **Correlation Analysis**
   ```python
   # Avoid taking similar positions in correlated pairs
   CORRELATED_PAIRS = {
       'cmt_btcusdt': ['cmt_ethusdt', 'cmt_bnbusdt'],
       'cmt_solusdt': ['cmt_adausdt']
   }
   ```

### **Medium-term Improvements**
1. **Multiple Timeframe Analysis**
   - Combine 5min, 15min, 1h signals
   - Weight signals based on timeframe consistency

2. **Ensemble Models**
   ```python
   # Combine predictions from multiple models
   models = {
       'gradient_boosting': load_model('gb.pkl'),
       'random_forest': load_model('rf.pkl'),
       'lstm': load_model('lstm.h5')
   }
   ```

3. **Advanced Risk Management**
   - Value at Risk (VaR) calculations
   - Portfolio optimization
   - Dynamic position sizing based on market regime

### **Long-term Enhancements**
1. **Reinforcement Learning**
   - Use PPO or DQN for parameter optimization
   - Learn optimal stop-loss/take-profit levels

2. **Alternative Data Integration**
   - Social media sentiment
   - On-chain metrics
   - Order flow analysis

3. **High-frequency Enhancements**
   - Microstructure analysis
   - Latency optimization
   - Smart order routing

---

## 🆘 **Troubleshooting Guide**

### **Common Issues & Solutions**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| API Connection Failed | `521 Web Server is Down` | 1. Check IP whitelist in WEEX dashboard<br>2. Verify API keys in .env file<br>3. Test with `curl` command |
| No Trades Being Placed | 0 trades after several hours | 1. Check `CONFIDENCE_THRESHOLD`<br>2. Verify market data fetching<br>3. Check `MIN_TRADE_AMOUNT` |
| AI Logs Not Generated | Empty `logs/` directory | 1. Check directory permissions<br>2. Verify logger initialization<br>3. Check disk space |
| High Error Rate | Frequent restarts | 1. Check API rate limits<br>2. Add error handling in strategy<br>3. Implement retry logic |

### **Debug Commands**
```bash
# Check system health
htop                          # CPU/Memory usage
nvtop                         # GPU usage (if using)
df -h                         # Disk space
sudo systemctl status weex*   # Service status

# Check trading activity
grep "ORDER" logs/ai_trading.log | tail -10
grep "ERROR" logs/ai_trading.log | tail -5

# Monitor API calls
sudo tcpdump -i eth0 port 443 -c 100  # Monitor HTTPS traffic
```

---

## 📚 **Resources & Support**

### **Official Documentation**
- [WEEX API Documentation](https://www.weex.com/api-doc/ai/intro)
- [Participant Guide](https://www.weex.com/api-doc/ai/introduction/ParticipantGuide)
- [Competition Rules](https://www.weex.com/events/ai-trading)

### **Community Support**
- Telegram: [@weexaiwars](https://t.me/weexaiwars)
- Technical Questions: [Telegram Group](https://t.me/weexaiwars/1)
- Twitter: [@weex_ai](https://x.com/weex_ai)

### **Useful Tools**
- IP Check: `curl https://ipinfo.io/ip`
- Time Sync: `sudo timedatectl set-ntp true`
- Log Rotation: Configure in `/etc/logrotate.d/`

---

## ⚠️ **Important Competition Notes**

### **Critical Deadlines**
1. **Forked Entry Registration**: Jan 18, 23:59 (UTC+8)
2. **Preliminary Round**: Jan 19 - Feb 2
3. **Minimum 10 Trades**: Must complete during preliminary
4. **AI Log Submission**: Continuous throughout competition

### **Competition Rules Compliance**
- ✅ Maximum 20x leverage (code enforces 5x default)
- ✅ Minimum 10 trades (monitor via logs)
- ✅ AI logs generated (automatic)
- ✅ No gambling-style trading (risk-managed)
- ✅ Trade only designated 8 pairs (enforced in code)

### **Success Metrics**
The competition ranks by **account balance**. Focus on:
1. **Consistent positive returns** (avoid large drawdowns)
2. **Risk-adjusted performance** (not just highest returns)
3. **Reliability** (24/7 uptime, no crashes)
4. **Rule compliance** (proper logging, leverage limits)

---

## 🎉 **Getting Started Quick Script**

Copy this to your cloud server and run:

```bash
#!/bin/bash
# WEEX AI Trading Setup Script

echo "=== WEEX AI Trading Competition Setup ==="

# 1. Update system
# Amazon Linux 2023:
sudo dnf update -y
# Ubuntu:
# sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
# Amazon Linux 2023:
sudo dnf install -y git python3-pip python3-devel gcc
# Ubuntu:
# sudo apt install -y python3.9 python3-pip python3.9-venv git

# 3. Clone repository
git clone https://github.com/ritwikareddykancharla/weex-alpha-awakens-ai.git
cd weex-alpha-awakens-ai

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install requirements
pip install -r requirements.txt

# 6. Get server IP for WEEX registration
echo "Your server IP for WEEX registration:"
curl -s https://ipinfo.io/ip

echo "=== Setup Complete ==="
echo "1. Add above IP to WEEX whitelist"
echo "2. Copy .env.example to .env and add API keys"
echo "3. Run: python scripts/train_model.py"
echo "4. Start: python src/main.py"
```

---

## 📞 **Emergency Contact & Support**

### **During Competition Hours (UTC+8)**
- **Technical Support**: 9:00–22:00 via Telegram
- **Urgent Issues**: Tag @SmallWZ in Telegram group
- **API Problems**: Provide error codes and timestamps

### **Monitoring Dashboard Setup**
Consider setting up a simple monitoring dashboard:

```python
# scripts/monitor_dashboard.py
from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    with open('logs/ai_trading.log', 'r') as f:
        logs = f.readlines()[-100:]  # Last 100 lines
    return render_template('dashboard.html', logs=logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Access via: `http://your-server-ip:5000`

---

**Good luck in the competition! May your alpha awaken! 🚀**

*Last Updated: For AI Wars: WEEX Alpha Awakens (Jan 19 - Feb 2, 2026)*
```
