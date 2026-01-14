# 🦅 The Master Training Manual: How to Train the Entire Stack
*Exact instructions. No guessing.*

You asked: *"Which files do I run? Did you implement all of this?"*
**Answer: YES. Here is the map of the Machine.**

---

## 🗺️ The Stack Architecture (By File)

| Component Name | Technical Role | The File You Run | Status |
| :--- | :--- | :--- | :--- |
| **1. The Screener** | **Asset Selection** | `scripts/market_screener.py` | ✅ Ready |
| **2. The Optimizer** | **Hyperparameter Tuning** | `scripts/risk_optimizer.py` | ✅ Ready |
| **3. The Alpha Brain** | **Signal Generation (DQN)** | `agents/dqn.py` (Training) | ✅ Ready |
| **4. The Executor** | **Live Trading** | `src/main.py` | ✅ Ready |

---

## 🚀 The Execution Pipeline (Do exactly this)

### 1️⃣ PHASE 1: The Setup (On EC2)
*Goal: Get the data and pick the target.*

1.  **Get Data**:
    ```bash
    python scripts/fetch_training_data.py
    # RESULT: Downloads 'data/weex_data_cmt_dogeusdt.csv' (+ 7 others)
    ```

2.  **Run Screener**:
    ```bash
    python scripts/market_screener.py
    # RESULT: Output "RECOMMENDED PAIR: DOGE" (or similar)
    ```

3.  **Run Optimizer** (Tunes the Risk Engine):
    ```bash
    python scripts/risk_optimizer.py
    # RESULT: Output "Best Kelly=0.3, Best SL=1.5"
    # ACTION: Write these numbers down.
    ```

### 2️⃣ PHASE 2: The Training (On Kaggle)
*Goal: Teach the Neural Network to trade ALL pairs.*

1.  **Transfer Data**:
    *   **Do NOT move one file.** Move the whole folder.
    ```powershell
    # On Local Terminal
    scp -r -i "key.pem" ec2-user@ip:~/weex-alpha-awakens-ai/data/ ./Desktop/weex_data/
    ```
2.  **Upload to Kaggle**: Create a new dataset in Kaggle and upload ALL 8 CSV files.
3.  **Train (The Universal Brain)**:
    *   Run this code. It merges ALL pair data to train one Super-Model.
    ```python
    # In Kaggle Cell
    import os
    import pandas as pd
    from dqn import WEEXDQNTradingBot
    
    # 1. Load ALL CSVs
    all_dfs = []
    files = [f for f in os.listdir("/kaggle/input/your-dataset/") if f.endswith('.csv')]
    
    print(f"Stats: Found {len(files)} pairs.")
    for filename in files:
        df = pd.read_csv(f"/kaggle/input/your-dataset/{filename}")
        all_dfs.append(df)
        
    # 2. Merge into one massive dataset
    universal_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Training on {len(universal_df)} total candles...")
    
    # 3. Train Universal Brain
    bot = WEEXDQNTradingBot(symbol="UNIVERSAL")
    bot.train(universal_df, episodes=60) # More data needs more episodes
    
    # 4. Save (Professional Naming)
    bot.save_model("quant_momentum_dqn.pth")
    print("✅ Universal Brain Trained!")
    ```
4.  **Download**: Download the file `quant_momentum_dqn.pth`.

### 3️⃣ PHASE 3: The Launch (On EC2)
*Goal: Turn it on.*

1.  **Transfer Brain**: SCP the model to EC2.
    ```bash
    scp -i "key.pem" ~/Downloads/quant_momentum_dqn.pth ec2-user@ip:~/weex-alpha-awakens-ai/models/
    ```
2.  **Update Config**:
    *   Open `src/execution/risk_engine.py` and update settings.
3.  **IGNITION**:
    ```bash
    python -m src.main
    ```
    ```bash
    python -m src.main
    ```

---

## ❓ FAQ
*   **"Why do I run `optimize_strategy.py`?"**
    *   To find the perfect **Safety Settings** (Stop Loss / Position Size) for *current* market volatility.
*   **"Why do I run Kaggle?"**
    *   To find the perfect **Entry/Exit Signals** (DQN Weights).
*   **"What happens if I skip a step?"**
    *   Skip Phase 1: You trade the wrong coin.
    *   Skip Phase 2: Your bot guesses randomly.
    *   Skip Phase 3: You don't make money.

**You are ready. Start Phase 1.**
