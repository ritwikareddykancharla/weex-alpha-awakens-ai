# 🚀 The Ultimate Action Plan: EC2 & Kaggle

Here is your **Battle-Tested Checklist** to go from Zero to Live Trading.

---

## Phase 1: The "Recon" (On Your EC2) 🕵️‍♂️
**Goal**: Identify the best market to attack.

1.  **SSH into EC2**:
    ```bash
    ssh -i key.pem user@ec2-ip
    cd weex-alpha-awakens-ai
    git pull origin main
    ```

2.  **Fetch Data (Massive Dump)**:
    *This gets the last 6 months of data for ALL 8 competition pairs.*
    ```bash
    python scripts/fetch_training_data.py
    ```
    *Result*: A `data/` folder filled with CSVs (e.g., `data/weex_data_cmt_dogeusdt.csv`).

3.  **Analyze & Pick targets**:
    *The AI runs statistics to find the highest "Investability Score".*
    ```bash
    python scripts/analyze_pairs.py
    ```
    *Output*:
    > 🏆 TOP PICK: **cmt_dogeusdt** (Score: 8.5)
    > 🥈 RUNNER UP: **cmt_solusdt** (Score: 7.2)

    **ACTION**: Remember the "Top Pick". That is your target.

4.  **Exfiltrate Data**:
    Download the CSV of your **Top Pick** to your local computer (so you can upload to Kaggle).
    ```bash
    # Run this on your LOCAL machine
    scp -i key.pem user@ec2-ip:~/weex-alpha-awakens-ai/data/weex_data_cmt_dogeusdt.csv ./
    ```

---

## Phase 2: The "Gym" (On Kaggle) 🏋️‍♂️
**Goal**: Train the Brain on the specific target.

1.  **Open Kaggle Notebook**:
    *   New Notebook -> Settings -> **Accelerator: GPU T4 x2**.

2.  **Upload**:
    *   **Data**: Upload `weex_data_cmt_dogeusdt.csv`.
    *   **Code**: Copy-paste `agents/dqn.py` content into a cell (or upload script).

3.  **Train**:
    Run this code block:
    ```python
    import pandas as pd
    from dqn import WEEXDQNTradingBot
    
    # 1. Load Data
    df = pd.read_csv('/kaggle/input/your-dataset-name/weex_data_cmt_dogeusdt.csv')
    
    # 2. Train High-Performance Model
    # "Smart Leverage" learns best with more episodes
    bot = WEEXDQNTradingBot(symbol="DOGE/USDT") 
    metrics = bot.train(df, episodes=100) 
    
    # 3. Save
    bot.save_model("weex_dqn_doge.pth")
    ```

4.  **Download**:
    Download `weex_dqn_doge.pth`.

---

## Phase 3: The "Deep Strike" (Back to EC2) 🚀
**Goal**: Deploy the specialized agent.

1.  **Upload Brain**:
    ```bash
    # Run on LOCAL machine
    scp -i key.pem weex_dqn_doge.pth user@ec2-ip:~/weex-alpha-awakens-ai/models/weex_dqn.pth
    ```

2.  **Configure & Launch**:
    SSH back into EC2.
    *   Edit `src/main.py`: Set `symbol = "cmt_dogeusdt"` (Matches your training).
    *   **START THE ENGINE**:
    ```bash
    nohup python -m src.main > bot_output.log 2>&1 &
    ```

3.  **Verify**:
    ```bash
    tail -f ai_trading_log.json
    ```
    You should see confident trades executing with your Smart Leverage logic.
