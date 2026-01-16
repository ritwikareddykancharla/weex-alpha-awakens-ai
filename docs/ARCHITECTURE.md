# 🏗️ Neuro-Symbolic Agent Architecture

## 📂 The Structure

### `src/agents/` (The Brain Trust)
This is where the "Multi-Agent" magic happens.

*   **`coordinator.py` (The Boss)** 👮‍♂️
    *   **Role**: Orchestrates the team. It doesn't analyze; it *decides*.
    *   **Workflow**: `Coordinator` -> asks `Analyst` -> gets Signal -> asks `Risk` -> gets Approval -> Decision.
    *   **Analog**: The Hedge Fund Manager.

*   **`market_analyst.py` (The Brain)** 🧠
    *   **Role**: Pure Analysis.
    *   **Components**:
        *   **Eyes**: `RegimeClassifier` (Is the market safe? Calm? Crashing?)
        *   **Brain**: `AlphaEngine` (DQN/ML model predicting price direction).
    *   **Analog**: The Lead Quant Researcher.

*   **`risk_guardian.py` (The Shield)** 🛡️
    *   **Role**: Absolute VETO power.
    *   **Logic**: "I don't care how good the signal is; if we are down 5%, we stop."
    *   **Analog**: The Compliance Officer.

### `src/api/` (The Hands)
*   **`weex_client.py`**: Talk to WEEX (REST API).
*   **`websocket_client.py`**: Listen to WEEX (Real-time Stream).

### `src/strategy/` (The Toolkit)
*   Helper math and signal calculation libraries used by the Analyst.

---

## 🚀 Data Flow Diagram

```mermaid
graph TD
    Market[WEEX Market Data] --> Analyst(Market Analyst Agent)
    Analyst -->|Signal + Confidence| Coordinator(Coordinator Agent)
    
    Coordinator -->|Proposed Trade| Risk(Risk Guardian Agent)
    
    Risk -->|Approved/Veto| Coordinator
    
    Coordinator -->|Final Order| Executor[WEEX API]
```
