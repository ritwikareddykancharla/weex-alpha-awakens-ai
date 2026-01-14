# 🧪 The Scientific Workflow (Exact Pipeline)

This is your Step-by-Step Laboratory Manual. Follow it exactly to guarantee results.

---

##  PHASE 1: Data Extraction (The "Dig")
**Where**: EC2 Instance
**Why**: Only EC2 is whitelisted to talk to WEEX. You must dig the gold (data) here.

1.  **SSH into EC2**:
    ```bash
    ssh -i "your-key.pem" ec2-user@your-server-ip
    cd weex-alpha-awakens-ai
    ```
2.  **Run the Fetcher**:
    *   This script downloads 6 months of data for the top pair (e.g. BTC & DOGE).
    ```bash
    python scripts/fetch_training_data.py
    ```
3.  **Verify**:
    ```bash
    ls data/
    # You should see: weex_data_cmt_btcusdt.csv, weex_data_cmt_dogeusdt.csv
    ```

---

## PHASE 2: Secure Transport (The "Armored Truck")
**Where**: Your Local Computer (Laptop)
**Why**: GitHub has a 100MB limit. **Do NOT push CSVs to GitHub.** Use SCP (Secure Copy) to download data directly to your laptop, then upload to Kaggle.

1.  **Open Local Terminal (PowerShell)**:
    ```powershell
    # Download DOGE data from EC2 to your Desktop
    scp -i "path/to/key.pem" ec2-user@your-server-ip:~/weex-alpha-awakens-ai/data/weex_data_cmt_dogeusdt.csv ./Desktop/
    ```

---

## PHASE 3: The Laboratory (Training & Visualization)
**Where**: **Kaggle** (Web Browser)
**Why**: Kaggle has Free GPUs (T4 x2) and **Jupyter Notebooks** which let you *see* the charts.

1.  **Create New Notebook**: Go to Kaggle -> Create -> New Notebook.
2.  **Upload Data**: Click "Add Input" -> Upload -> Select `weex_data_cmt_dogeusdt.csv`.
3.  **Upload Code**: Copy-paste the content of `agents/dqn.py` into the first cell.
4.  **Run Experiment (Training)**:
    ```python
    # Cell 2: Training
    import pandas as pd
    import matplotlib.pyplot as plt
    from dqn import WEEXDQNTradingBot  # The class you pasted
    
    # Load Data
    df = pd.read_csv('/kaggle/input/weex_data_cmt_dogeusdt.csv')
    
    # Initialize & Train
    bot = WEEXDQNTradingBot(symbol="DOGE/USDT")
    metrics = bot.train(df, episodes=50) # Train for 50 episodes
    
    # SAVE THE BRAIN
    bot.save_model("weex_doge_brain.pth")
    ```
5.  **Run Visualization (The "Proof")**:
    *   This is why we use Kaggle. Visual verification.
    ```python
    # Cell 3: Plotting
    plt.plot(metrics['rewards'])
    plt.title("AI Learning Curve")
    plt.xlabel("Episode")
    plt.ylabel("Profit")
    plt.show() # If line goes up, AI is smart. If down, AI is dumb.
    ```

---

## PHASE 4: Deployment (The "Launch")
**Where**: EC2 Instance
**Why**: Now we move the "Educated Brain" back to the production server.

1.  **Download Model**: In Kaggle, look at "Output" section -> Download `weex_doge_brain.pth`.
2.  **Upload to EC2**:
    ```powershell
    # Run on Local Terminal
    scp -i "key.pem" ~/Downloads/weex_doge_brain.pth ec2-user@ip:~/weex-alpha-awakens-ai/models/
    ```
3.  **Start the Bot**:
    *   SSH back into EC2.
    ```bash
    # Run the backtest first to confirm the brain works on the server
    python scripts/backtest_strategy.py
    
    # If ROI is positive, LAUNCH LIVE
    nohup python -m src.main > logs/live_trading.log 2>&1 &
    ```

---

## Summary Checklist
*   [ ] **EC2**: `fetch_training_data.py` (Get Data)
*   [ ] **Local**: `scp` Download CSV
*   [ ] **Kaggle**: Upload CSV -> Train -> **Visualize Plots**
*   [ ] **Local**: Download `.pth` model
*   [ ] **EC2**: `scp` Upload `.pth` -> `python -m src.main`

**Security Note**: Never push `data/*.csv` or `models/*.pth` to GitHub. They are too big and clutter the repo. Use SCP.
