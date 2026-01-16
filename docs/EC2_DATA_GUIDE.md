# 📡 How to Pull Real WEEX Data on EC2

You asked: *"How to pull data from weex on ec2 ??"*

The WEEX API (`api-contract.weex.com`) blocks local IPs.
You MUST run the *Data Fetcher* on your EC2 instance.

---

## Step 1: Push Code to EC2
Run this **PowerShell** command from your Desktop folder (`weex-alpha-awakens-ai`):

```powershell
# 1. Zip your code (Optional but easier, or just copy the folder)
# Or just copy the scripts folder + src folder
scp -r -i "C:\path\to\your-key.pem" .\scripts ubuntu@<EC2-IP>:~/weex-bot/
scp -r -i "C:\path\to\your-key.pem" .\src ubuntu@<EC2-IP>:~/weex-bot/
scp -i "C:\path\to\your-key.pem" .\requirements.txt ubuntu@<EC2-IP>:~/weex-bot/
```

*(Replace `<EC2-IP>` with your actual AWS IP Address)*

---

## Step 2: Run the Fetcher on EC2
Login to your server:

```powershell
ssh -i "C:\path\to\your-key.pem" ubuntu@<EC2-IP>
```

Then run the fetcher:

```bash
# 1. Go to folder
cd ~/weex-bot

# 2. Install deps (if not done)
pip install -r requirements.txt

# 3. RUN THE FETCHER
python scripts/fetch_training_data.py
```

### What happens?
*   The script will connect to WEEX (No 521 Error).
*   It will download **180 Days** of 15-minute candles.
*   It saves files to the `data/` folder:
    *   `data/cmt_dogeusdt.csv`
    *   `data/cmt_solusdt.csv`
    *   ... (All 8 Pairs)

---

## Step 3: Run the Screener (Strategies)
Now that you have *Real Data*, run the screener to see what the bot would trade **Right Now**:

```bash
python scripts/market_screener.py
```

*   **Output**: It will print the **Top 3 Assets** based on Real Volatility ($S = \sigma \times |F|$).

---

## Step 4: Pull Data Back (Optional)
If you want to analyze the CSVs on your laptop:

```powershell
# Run this on your LOCAL Windows Machine
scp -r -i "C:\path\to\your-key.pem" ubuntu@<EC2-IP>:~/weex-bot/data .\data_from_ec2
```
