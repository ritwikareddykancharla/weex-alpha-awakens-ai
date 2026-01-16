#!/bin/bash
echo "🧠 Starting DQN Training..."
export PYTHONPATH=.
echo "Usage: ./train_brain.sh [SYMBOL] [DATA_CSV]"
echo "Example: ./train_brain.sh cmt_btcusdt data/btc_15m.csv"

if [ -z "$1" ]; then
    echo "❌ Error: Missing Symbol and Data arguments."
    echo "Defaulting to: cmt_btcusdt (assuming data exists)"
    python3 scripts/train_dqn.py --symbol cmt_btcusdt --data data/btc_15m.csv
else
    python3 scripts/train_dqn.py --symbol $1 --data $2
fi
