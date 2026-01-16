# 🧠 Component Spec: Alpha Engine (Layer 2)

**File**: `src/ai/alpha_engine.py` (Model: `quant_momentum_dqn.pth`)
**Role**: Signal Generation & Confidence Scoring.

---

## 1. The Objective
The Alpha Engine answers the question: **"Which direction do we go?"**
It analyzes the price action of the selected assets and outputs a Signal (`LONG`, `SHORT`, `NEUTRAL`) with a probability score.

## 2. The Model: Universal Deep Q-Network
Unlike "Basic Bots" that learn a specific coin (e.g., "BTC Bot"), this is a **Universal Approximator**.

### Key Innovation: Z-Score Normalization
To train on *all* coins at once, we must make them mathematically identical.
$$z = \frac{x - \mu}{\sigma}$$
*   **Input**: BTC price (\$95,000) and DOGE price (\$0.35).
*   **Transformation**: Both are converted to "Standard Deviations from Mean" (e.g., +2.0 or -1.5).
*   **Result**: The Neural Network sees **Patterns**, not Prices. A "Pump" looks the same on BTC as it does on PEPE.

## 3. Neural Architecture
1.  **Input Layer (15 Neurons)**:
    *   RSI (14), MACD, Bollinger Band Width.
    *   Volume Delta, Funding Rate.
2.  **Hidden Layers**:
    *   Layer 1: 128 Neurons (ReLU Activation).
    *   Layer 2: 128 Neurons (ReLU Activation).
3.  **Output Layer (3 Neurons)**:
    *   Q-Values for `[LONG, NEUTRAL, SHORT]`.

## 4. Signal Logic
The model outputs raw Q-Values (expected future rewards). We convert this to a decision:
1.  **Softmax**: Convert Q-Values to Probabilities (e.g., Long: 0.85).
2.  **Threshold Check**:
    *   If Confidence > 0.60 $\rightarrow$ **SIGNAL** (Long/Short).
    *   If Confidence < 0.60 $\rightarrow$ **NOISE** (Stay Neutral).

## 5. Why This Works
*   **Data Richness**: By training on the combined history of 8 pairs, the model sees 8x more market scenarios than a single-pair model.
*   **Generalization**: It learns "Market Physics" (e.g., Mean Reversion logic), so it can trade a new coin (like PEPE) effectively even if it hasn't seen it much.

**Status**: Implemented & Universal Model Trained.
