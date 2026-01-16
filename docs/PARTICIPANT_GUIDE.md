# AI Wars: WEEX Alpha Awakens - Participant Guide

## Introduction
**Welcome to the Arena: The Path to Alpha Awakening**
AI Wars: WEEX Alpha Awakens – Global AI Trading Hackathon!

In this ultimate showdown, top developers, quants, and traders from around the world will unleash their algorithms in real-market battles, competing for one of the richest prize pools in AI crypto trading history: **880,000 USD**, including a Bentley Bentayga S for the champion.

Follow the path and start your journey:
`Register & Form Your Team → Pass API Testing → Model Tuning → Official Start`

---

## Step 1｜Register, Create & Submit Your BUIDL
**Goal:** Complete your official registration, create or join a team (BUIDL), and pass the review to receive your dedicated API key.

### 1.1 Visit the Event Page
Visit [WEEX AI Trading Event Page](https://www.weex.com/events/ai-trading) and click **"Submit BUIDL"**.

### 1.2 Find a Team or Build Your Own
A BUIDL is the basic participating unit.
- **Profile:** BUIDL name, logo, vision, GitHub.
- **Submission:** WEEX UID (KYC required), IP Address, Programming Languages, Strategy details.

> **Tip:** Solo participation is allowed, but 2–5 member teams are recommended.

### 1.3 Missing Information?
WEEX team will review within one business day and contact you via DoraHacks or WEEX messaging if info is missing.

### 1.4 Your Starter Kit
Once approved, you will receive:
- **API Key**
- **Secret Key**
- **Passphrase**
- **API Testing Page Link**

---

## Step 2｜Pass the Gateway: Complete Your API Testing
**Goal:** Ensure your system can successfully interact with the WEEX API.

### 2.1 Instructions
- Participants who pass API testing obtain eligibility.
- Failing API testing means disqualification.

### 2.2 Connect and Test
**Integration Preparation:**
Access [Official API Docs](https://www.weex.com/api-doc/ai/intro).

**Test Command:**
```bash
curl -s --max-time 10 "https://api-contract.weex.com/capi/v2/market/time"
```

**Status Codes:**
- `200`: Success
- `521`: **Web Server is Down – IP not whitelisted** (Make sure to whitelist your IP!)

### 2.3 Required API Tests (Python Example)
Run the following tests on `cmt_btcusdt`:
1.  **Check Account Balance** (`/capi/v2/account/assets`)
2.  **Get Asset Price** (`/capi/v2/market/ticker`)
3.  **Set Leverage** (`/capi/v2/account/leverage`) - Max 20x.
4.  **Place Order** (`/capi/v2/order/placeOrder`) - ~10 USDT on `cmt_btcusdt`.
5.  **Get Trade Details** (`/capi/v2/order/fills`)

> **Note:** The `manual_api_verification.py` script in this repo implements these exact steps.

---

## 2.3 Funding & Model Testing
After passing, you receive initial test funds. Valid until Jan 5, 2026.

## 2.4 Pre-Competition Preparation
Account reset before official start. Funds reset to 1,000 USDT.

---

## Timeline
- **Pre-Registration:** Now – Dec 30, 2025
- **Pre-Season:** Early Jan 2026
- **Finals:** Late Feb 2026
- **Awarding:** March 2026 (Dubai)

---

## Reference Code (Python)
*Based on Official Demo Code*

```python
import time
import hmac
import hashlib
import base64
import requests
import json

# Replace with your actual keys
api_key = ""
secret_key = ""
access_passphrase = ""
base_url = "https://api-contract.weex.com"

def generate_signature(secret_key, timestamp, method, request_path, query_string, body):
    message = timestamp + method.upper() + request_path + query_string + str(body)
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def send_request_post(method, request_path, query_string, body):
    timestamp = str(int(time.time() * 1000))
    body_json = json.dumps(body)
    signature = generate_signature(secret_key, timestamp, method, request_path, query_string, body_json)
    
    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": access_passphrase,
        "Content-Type": "application/json",
        "locale": "en-US"
    }
    
    url = base_url + request_path
    response = requests.post(url, headers=headers, data=body_json)
    return response

# Example Usage
# leverage()
# placeOrder()
```
