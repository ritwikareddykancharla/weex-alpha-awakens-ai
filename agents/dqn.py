import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque, namedtuple
import random
from typing import Dict, List
import json

# Hackathon-focused hyperparameters (aggressive convergence)
HACKATHON_CONFIG = {
    # Model Architecture
    "hidden_size": 256,  # Sufficient for 24h crypto patterns
    "num_layers": 3,
    
    # Training Stability
    "learning_rate": 3e-4,  # Adam default sweet spot
    "batch_size": 128,  # Larger for crypto volatility
    "buffer_size": 50000,  # 2 weeks of minute data
    "target_update": 1000,  # Hard update (more stable than polyak)
    
    # Exploration (fast decay for hackathon)
    "epsilon_start": 1.0,
    "epsilon_min": 0.05,  # Never fully exploit in crypto
    "epsilon_decay": 0.995,  # ~500 steps to reach min
    "warmup_steps": 1000,  # Fill buffer before training
    
    # Convergence Accelerators
    "double_dqn": True,  # Reduce overestimation
    "dueling_dqn": True,  # Better state value estimation
    "gradient_clip": 10.0,  # Prevent crypto volatility explosions
    
    # Trading Realism
    "transaction_cost": 0.001,  # 0.1% (taker fee)
    "slippage": 0.0005,  # 0.05% slippage
    "risk_penalty": 0.001,  # Punish position changes
}

class TradingFeatureEngineer:
    """Pragmatic features that work on limited hackathon data"""
    @staticmethod
    def compute_features(df: pd.DataFrame, lookback: int = 60) -> np.ndarray:
        """
        Compute robust features that don't leak future info
        Works even with 1 week of minute data
        """
        features = []
        
        # Core price features (always available)
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Momentum (shorter periods for crypto)
        for period in [5, 15, 30]:
            df[f'roc_{period}'] = df['close'].pct_change(period)
            features.append(df[f'roc_{period}'])
        
        # Volatility (realized variance)
        for period in [15, 30, 60]:
            df[f'vol_{period}'] = df['returns'].rolling(period).std() * np.sqrt(period)
            features.append(df[f'vol_{period}'])
        
        # Simple technical indicators (no lookahead bias)
        # EMAs
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        features.append((df['ema_12'] / df['close']) - 1)
        features.append((df['ema_26'] / df['close']) - 1)
        
        # RSI approximation (momentum-based)
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / (loss + 1e-8)
        df['rsi'] = 100 - (100 / (1 + rs))
        features.append(df['rsi'] / 100 - 0.5)  # Center at 0
        
        # Volume features
        df['volume_ma'] = df['volume'].rolling(20).mean()
        features.append((df['volume'] / df['volume_ma']) - 1)
        
        # Market microstructure
        df['spread'] = (df['high'] - df['low']) / df['close']
        features.append(df['spread'])
        
        # Concatenate and fill NaN with 0 (hackathon-safe)
        feature_matrix = pd.concat(features, axis=1).fillna(0).values
        
        # Z-score normalization (robust to outliers)
        mean = feature_matrix.mean(axis=0)
        std = feature_matrix.std(axis=0) + 1e-8
        normalized = (feature_matrix - mean) / std
        
        return normalized.astype(np.float32)


class DuelingQNetwork(nn.Module):
    """Dueling architecture - better for sparse crypto rewards"""
    def __init__(self, state_dim: int, action_dim: int, config: Dict):
        super().__init__()
        
        # Shared feature extractor
        self.feature_extractor = nn.Sequential(
            nn.Linear(state_dim, config["hidden_size"]),
            nn.ReLU(),
            nn.Dropout(0.2),  # Prevent overfitting on small data
            nn.Linear(config["hidden_size"], config["hidden_size"]),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Value stream (state value)
        self.value_stream = nn.Sequential(
            nn.Linear(config["hidden_size"], config["hidden_size"] // 2),
            nn.ReLU(),
            nn.Linear(config["hidden_size"] // 2, 1)
        )
        
        # Advantage stream (action advantage)
        self.advantage_stream = nn.Sequential(
            nn.Linear(config["hidden_size"], config["hidden_size"] // 2),
            nn.ReLU(),
            nn.Linear(config["hidden_size"] // 2, action_dim)
        )
        
    def forward(self, x):
        features = self.feature_extractor(x)
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        
        # Q = V + A - mean(A) (dicing trick for stability)
        q_values = value + advantage - advantage.mean(dim=-1, keepdim=True)
        return q_values


class PrioritizedReplayBuffer:
    """Proportional sampling for faster learning"""
    def __init__(self, capacity: int, alpha: float = 0.6):
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.alpha = alpha
        self.Transition = namedtuple('Transition', 
                                   ('state', 'action', 'reward', 'next_state', 'done'))
    
    def push(self, *args):
        """Add transition with max priority"""
        self.buffer.append(self.Transition(*args))
        # New experiences get max priority (always sampled)
        max_prio = max(self.priorities) if self.priorities else 1.0
        self.priorities.append(max_prio)
    
    def sample(self, batch_size: int, beta: float = 0.4):
        """Sample with probability proportional to priority"""
        if len(self.buffer) < batch_size:
            return None
        
        # Compute probabilities
        probs = np.array(self.priorities) ** self.alpha
        probs /= probs.sum()
        
        # Sample indices
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        
        # Compute importance-sampling weights
        weights = (len(self.buffer) * probs[indices]) ** (-beta)
        weights /= weights.max()  # Normalize for stability
        
        # Get transitions
        batch = [self.buffer[i] for i in indices]
        
        return batch, indices, weights
    
    def update_priorities(self, indices: List[int], td_errors: np.ndarray):
        """Update priorities based on TD error"""
        for i, td_error in zip(indices, td_errors):
            self.priorities[i] = abs(td_error) + 1e-6
    
    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    """Hackathon-optimized DQN agent with warm-start capability"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict, device: str = "cpu"):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config
        self.device = device
        
        # Networks
        self.q_network = DuelingQNetwork(state_dim, action_dim, config).to(device)
        self.target_network = DuelingQNetwork(state_dim, action_dim, config).to(device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer (Adam with weight decay for stability)
        self.optimizer = optim.Adam(
            self.q_network.parameters(), 
            lr=config["learning_rate"],
            weight_decay=1e-5
        )
        
        # Replay buffer
        self.memory = PrioritizedReplayBuffer(
            config["buffer_size"],
            alpha=0.6
        )
        
        # State
        self.epsilon = config["epsilon_start"]
        self.training_step = 0
        self.episode_rewards = []
        
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Epsilon-greedy with decay"""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def store_transition(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)
    
    def update(self) -> float:
        """Train step with Double DQN loss"""
        if len(self.memory) < self.config["batch_size"]:
            return 0.0
        
        # Sample with priorities
        batch_data = self.memory.sample(self.config["batch_size"], beta=0.4)
        if batch_data is None:
            return 0.0
        
        batch, indices, weights = batch_data
        
        # Unpack
        states = torch.FloatTensor([t.state for t in batch]).to(self.device)
        actions = torch.LongTensor([t.action for t in batch]).to(self.device)
        rewards = torch.FloatTensor([t.reward for t in batch]).to(self.device)
        next_states = torch.FloatTensor([t.next_state for t in batch]).to(self.device)
        dones = torch.BoolTensor([t.done for t in batch]).to(self.device)
        weights = torch.FloatTensor(weights).to(self.device)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze()
        
        # Double DQN target
        with torch.no_grad():
            if self.config["double_dqn"]:
                # Use Q-network to select actions
                next_actions = self.q_network(next_states).argmax(1)
                # Use target network to evaluate
                next_q_values = self.target_network(next_states).gather(1, next_actions.unsqueeze(1)).squeeze()
            else:
                next_q_values = self.target_network(next_states).max(1)[0]
            
            # Zero out terminal states
            next_q_values[dones] = 0.0
            
            # Discounted return
            target_q_values = rewards + self.config.get("gamma", 0.99) * next_q_values
        
        # TD error for prioritized replay
        td_errors = (current_q_values - target_q_values).detach().cpu().numpy()
        
        # Update priorities
        self.memory.update_priorities(indices, np.abs(td_errors))
        
        # Loss with importance sampling
        loss = (weights * (current_q_values - target_q_values).pow(2)).mean()
        
        # Optimize with gradient clipping
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), self.config["gradient_clip"])
        self.optimizer.step()
        
        # Update target network (hard update for stability)
        self.training_step += 1
        if self.training_step % self.config["target_update"] == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.config["epsilon_min"], 
                          self.epsilon * self.config["epsilon_decay"])
        
        return loss.item()
    
    def warm_start(self, demonstration_data: List[Dict], epochs: int = 10):
        """
        Pre-train on demonstration data for faster hackathon convergence
        demonstration_data: List of {state, action, reward, next_state, done}
        """
        print(f"Warm-starting with {len(demonstration_data)} demonstrations...")
        
        # Add all demonstrations to buffer
        for demo in demonstration_data:
            self.memory.push(
                demo['state'], demo['action'], demo['reward'], 
                demo['next_state'], demo['done']
            )
        
        # Pre-train
        self.q_network.train()
        for epoch in range(epochs):
            total_loss = 0
            for _ in range(100):  # 100 updates per epoch
                loss = self.update()
                total_loss += loss
            
            avg_loss = total_loss / 100
            print(f"Warm-start Epoch {epoch+1}/{epochs}, Avg Loss: {avg_loss:.4f}")
        
        print("Warm-start completed!")
        return self
    

class CryptoTradingEnv:
    """WEEX-compatible trading environment"""
    
    # Action space: 0=HOLD, 1=BUY, 2=SELL
    ACTION_SPACE = {0: "HOLD", 1: "BUY", 2: "SELL"}
    
    def __init__(self, df: pd.DataFrame, initial_balance: float = 10000.0, 
                 transaction_cost: float = 0.001, slippage: float = 0.0005):
        self.features = TradingFeatureEngineer.compute_features(df)
        self.prices = df['close'].values
        self.volumes = df['volume'].values
        
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        
        self.reset()
    
    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0.0  # Crypto amount held
        self.entry_price = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        # Portfolio value tracking
        self.portfolio_value = self.initial_balance
        self.max_portfolio_value = self.initial_balance
        
        return self._get_state()
    
    def _get_state(self):
        """Get current state vector"""
        market_state = self.features[self.current_step]
        
        # Add portfolio context (crucial for crypto)
        portfolio_context = np.array([
            self.balance / self.initial_balance,  # Normalized balance
            self.position * self.prices[self.current_step] / self.initial_balance,  # Position value
            float(self.position > 0),  # Position flag
            self.portfolio_value / self.initial_balance - 1.0,  # PnL
        ], dtype=np.float32)
        
        return np.concatenate([market_state, portfolio_context])
    
    def step(self, action: int):
        """Execute action and return next_state, reward, done, info"""
        current_price = self.prices[self.current_step]
        current_value = self._compute_portfolio_value(current_price)
        
        # Execute trade
        trade_executed = False
        reward = 0.0
        
        if action == 1 and self.position == 0:  # BUY
            # Calculate max position with slippage
            effective_price = current_price * (1 + self.slippage)
            cost = self.transaction_cost * self.balance
            self.position = (self.balance - cost) / effective_price
            self.entry_price = effective_price
            self.balance = 0.0
            self.total_trades += 1
            trade_executed = True
            
        elif action == 2 and self.position > 0:  # SELL
            # Sell with slippage
            effective_price = current_price * (1 - self.slippage)
            value = self.position * effective_price
            cost = self.transaction_cost * value
            self.balance = value - cost
            self.position = 0.0
            
            # Reward is realized profit
            reward = (value - cost) / self.entry_price - 1.0
            if reward > 0:
                self.winning_trades += 1
            self.total_trades += 1
            trade_executed = True
            
        # Penalize position changes (reduce overtrading)
        if action in [1, 2] and not trade_executed:
            reward = -0.001  # Small penalty for invalid actions
        
        # Move to next step
        self.current_step += 1
        done = self.current_step >= len(self.features) - 1
        
        # Compute new portfolio value
        next_price = self.prices[min(self.current_step, len(self.prices) - 1)]
        next_value = self._compute_portfolio_value(next_price)
        
        # Risk-adjusted reward
        if not trade_executed and action == 0:
            # Reward for holding with momentum
            price_change = (next_price - current_price) / current_price
            if self.position > 0:  # Long position benefits from upward move
                reward = price_change
            else:  # Cash position avoids volatility (small penalty)
                reward = -abs(price_change) * 0.1
        
        # Sharpe-like penalty for drawdown (crypto-specific)
        self.max_portfolio_value = max(self.max_portfolio_value, next_value)
        drawdown = (self.max_portfolio_value - next_value) / self.max_portfolio_value
        reward -= drawdown * 0.5  # Punish drawdowns
        
        # Update tracking
        self.portfolio_value = next_value
        
        # Info for monitoring
        info = {
            'portfolio_value': next_value,
            'balance': self.balance,
            'position': self.position,
            'total_trades': self.total_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
            'current_price': next_price,
        }
        
        return self._get_state(), reward, done, info
    
    def _compute_portfolio_value(self, price: float) -> float:
        """Total portfolio value in quote currency"""
        return self.balance + self.position * price


# WEEX Hackathon Integration
class WEEXDQNTradingBot:
    """Ready-to-deploy bot for WEEX AI Hackathon"""
    
    def __init__(self, symbol: str = "BTC/USDT", leverage: int = 1):
        self.config = HACKATHON_CONFIG.copy()
        self.config['gamma'] = 0.99
        
        self.symbol = symbol
        self.leverage = leverage
        
        # Model placeholders
        self.agent = None
        self.scaler = None
        
        # Performance tracking
        self.episodes_reward = []
        
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and validate OHLCV data from WEEX API"""
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        assert all(col in df.columns for col in required_cols), "Missing required columns"
        
        # Ensure proper sorting
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Basic validation
        assert not df[required_cols].isnull().any().any(), "NaN values detected"
        
        return df
    
    def create_demonstration_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Generate demonstration data for warm-start
        Simple momentum-based strategy for pre-training
        """
        features = TradingFeatureEngineer.compute_features(df)
        prices = df['close'].values
        
        demonstrations = []
        
        for i in range(60, len(features) - 10):  # Skip first 60 for feature calc
            # Momentum signal
            returns_5 = (prices[i] - prices[i-5]) / prices[i-5]
            returns_15 = (prices[i] - prices[i-15]) / prices[i-15]
            returns_30 = (prices[i] - prices[i-30]) / prices[i-30]
            
            # Simple rule: strong upward momentum = BUY, strong down = SELL
            if returns_5 > 0.002 and returns_15 > 0 and returns_30 > 0:
                action = 1  # BUY
            elif returns_5 < -0.002 and returns_15 < 0 and returns_30 < 0:
                action = 2  # SELL
            else:
                action = 0  # HOLD
            
            # Compute reward (next 5-step return)
            future_return = (prices[i+5] - prices[i]) / prices[i]
            
            demonstrations.append({
                'state': features[i],
                'action': action,
                'reward': future_return,
                'next_state': features[i+1],
                'done': False
            })
        
        return demonstrations
    
    def train(self, train_df: pd.DataFrame, episodes: int = 50, 
              val_df: pd.DataFrame = None) -> Dict[str, List[float]]:
        """
        Train DQN agent with warm-start and validation
        episodes: Number of episodes (reduce to 20-30 for hackathon if needed)
        """
        # Prepare data
        train_df = self.prepare_data(train_df)
        
        # Create environment
        env = CryptoTradingEnv(train_df, transaction_cost=self.config["transaction_cost"])
        
        # Initialize agent
        state_dim = len(env._get_state())
        self.agent = DQNAgent(state_dim, len(self.ACTION_SPACE), self.config, device="cpu")
        
        # Warm-start if possible
        demonstration_data = self.create_demonstration_data(train_df)
        if len(demonstration_data) > 100:
            self.agent.warm_start(demonstration_data, epochs=5)
        
        # Training metrics
        metrics = {
            'episode_rewards': [],
            'episode_portfolio_values': [],
            'episode_win_rates': [],
            'losses': []
        }
        
        print(f"Starting training for {episodes} episodes...")
        
        for episode in range(episodes):
            state = env.reset()
            episode_reward = 0
            episode_loss = 0
            update_count = 0
            
            while True:
                # Action selection
                action = self.agent.select_action(state, training=True)
                
                # Environment step
                next_state, reward, done, info = env.step(action)
                
                # Store transition
                self.agent.store_transition(state, action, reward, next_state, done)
                
                # Update network (skip early steps)
                if self.agent.training_step > self.config["warmup_steps"]:
                    loss = self.agent.update()
                    episode_loss += loss
                    update_count += 1
                
                state = next_state
                episode_reward += reward
                
                if done:
                    break
            
            # Episode metrics
            avg_loss = episode_loss / max(update_count, 1)
            final_value = info['portfolio_value']
            win_rate = info['win_rate']
            
            metrics['episode_rewards'].append(episode_reward)
            metrics['episode_portfolio_values'].append(final_value)
            metrics['episode_win_rates'].append(win_rate)
            metrics['losses'].append(avg_loss)
            
            # Progress
            if (episode + 1) % 5 == 0:
                print(f"Episode {episode+1}/{episodes} | "
                      f"Portfolio: ${final_value:,.2f} | "
                      f"Reward: {episode_reward:.4f} | "
                      f"Win Rate: {win_rate:.2%} | "
                      f"Loss: {avg_loss:.4f} | "
                      f"Epsilon: {self.agent.epsilon:.3f}")
        
        # Validation
        if val_df is not None:
            val_performance = self.validate(val_df)
            metrics['validation'] = val_performance
        
        return metrics
    
    def validate(self, val_df: pd.DataFrame) -> Dict:
        """Validate on unseen data"""
        val_df = self.prepare_data(val_df)
        env = CryptoTradingEnv(val_df, transaction_cost=self.config["transaction_cost"])
        
        state = env.reset()
        done = False
        portfolio_values = []
        
        while not done:
            action = self.agent.select_action(state, training=False)
            state, _, done, info = env.step(action)
            portfolio_values.append(info['portfolio_value'])
        
        return {
            'final_portfolio_value': info['portfolio_value'],
            'total_return': (info['portfolio_value'] - env.initial_balance) / env.initial_balance,
            'win_rate': info['win_rate'],
            'total_trades': info['total_trades'],
            'max_portfolio': max(portfolio_values),
            'min_portfolio': min(portfolio_values)
        }
    
    def predict(self, current_features: np.ndarray, balance: float, 
                position: float, current_price: float) -> Dict:
        """
        Predict action for live trading
        current_features: Pre-computed feature vector (same as training)
        balance, position: Current portfolio state
        current_price: Current market price
        """
        if self.agent is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Construct state (must match training format)
        portfolio_context = np.array([
            balance / 10000.0,  # Normalize
            position * current_price / 10000.0,
            float(position > 0),
            0.0,  # PnL not available in live
        ], dtype=np.float32)
        
        state = np.concatenate([current_features, portfolio_context])
        
        # Get action
        action = self.agent.select_action(state, training=False)
        action_name = self.ACTION_SPACE[action]
        
        # Get Q-values for confidence
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.agent.q_network(state_tensor).squeeze()
            confidence = torch.softmax(q_values, dim=0)[action].item()
        
        return {
            'action': action_name,
            'action_id': action,
            'confidence': confidence,
            'q_values': q_values.numpy(),
            'position_recommended': action_name
        }
    
    def save_model(self, filepath: str):
        """Save model state for WEEX submission"""
        if self.agent is None:
            raise ValueError("No model to save")
        
        torch.save({
            'q_network_state_dict': self.agent.q_network.state_dict(),
            'config': self.config,
            'training_metrics': self.episodes_reward,
        }, filepath)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load pre-trained model"""
        checkpoint = torch.load(filepath, map_location='cpu')
        
        # Create dummy agent (state_dim will be inferred later)
        self.config = checkpoint['config']
        
        # Note: You'll need to initialize env first to get state_dim
        print(f"Model loaded from {filepath}. Initialize agent with env before using.")


# Example Usage for Hackathon
if __name__ == "__main__":
    # Load your WEEX data (OHLCV format)
    # train_df = pd.read_csv('weex_btc_train.csv')
    # val_df = pd.read_csv('weex_btc_val.csv')
    
    # Minimal example
    np.random.seed(42)
    timestamps = pd.date_range('2024-01-01', periods=10080, freq='1min')  # 1 week
    train_df = pd.DataFrame({
        'timestamp': timestamps,
        'open': 100 + np.random.randn(10080).cumsum() * 0.1,
        'high': 100 + np.random.randn(10080).cumsum() * 0.1 + 0.5,
        'low': 100 + np.random.randn(10080).cumsum() * 0.1 - 0.5,
        'close': 100 + np.random.randn(10080).cumsum() * 0.1,
        'volume': np.random.randint(1000, 10000, 10080)
    })
    
    # Initialize bot
    bot = WEEXDQNTradingBot(symbol="BTC/USDT")
    
    # Train with warm-start (aim for 30-50 episodes in hackathon)
    print("=== Training Phase ===")
    metrics = bot.train(train_df, episodes=20)
    
    # Save model
    bot.save_model("weex_hackathon_dqn.pth")
    
    # Simulate prediction
    features = TradingFeatureEngineer.compute_features(train_df)
    current_state = features[-1]  # Latest features
    
    prediction = bot.predict(
        current_features=current_state,
        balance=10000.0,
        position=0.0,
        current_price=train_df['close'].iloc[-1]
    )
    
    print("\n=== Live Prediction ===")
    print(f"Recommended Action: {prediction['action']}")
    print(f"Confidence: {prediction['confidence']:.2%}")
    print(f"Q-values: {prediction['q_values']}")
