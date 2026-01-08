import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import joblib
from datetime import datetime, timedelta

from src.strategy.base_strategy import BaseStrategy
from src.strategy.risk_manager import RiskManager
from src.strategy.signals.trend_signals import TrendSignals
from src.strategy.signals.ai_model import AIModel
from src.api.weex_client import WeexAPIClient
from config.settings import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AITrendFollower(BaseStrategy):
    """AI-powered trend following strategy"""
    
    def __init__(self, api_client: WeexAPIClient):
        super().__init__(api_client)
        self.risk_manager = RiskManager(api_client)
        self.trend_signals = TrendSignals()
        self.ai_model = AIModel()
        
        # Load trained models
        self.classifier = joblib.load(config.MODEL_PATH)
        self.scaler = joblib.load(config.SCALER_PATH)
        
        # State tracking
        self.positions = {}
        self.signals_history = []
        self.pair_states = {}
        
        # Initialize pair states
        for pair in config.TRADING_PAIRS:
            self.pair_states[pair] = {
                'current_signal': 'NEUTRAL',
                'signal_strength': 0.0,
                'last_signal_time': None,
                'consecutive_signals': 0
            }
    
    def analyze_market(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        Analyze market data and generate trading signals
        
        Returns:
            Dict with signal details
        """
        if len(data) < config.LOOKBACK_PERIOD:
            return {'signal': 'NEUTRAL', 'confidence': 0.0}
        
        # 1. Calculate technical indicators
        indicators = self.trend_signals.calculate_all_indicators(data)
        
        # 2. Prepare features for AI model
        features = self._prepare_features(data, indicators)
        
        # 3. Get AI prediction
        ai_prediction, confidence = self.ai_model.predict(
            features, self.classifier, self.scaler
        )
        
        # 4. Combine AI with traditional signals
        final_signal = self._combine_signals(
            ai_prediction, indicators, confidence
        )
        
        # 5. Apply trend confirmation
        if final_signal != 'NEUTRAL':
            confirmed = self._confirm_trend(symbol, final_signal, data)
            if not confirmed:
                final_signal = 'NEUTRAL'
                confidence *= 0.5
        
        return {
            'symbol': symbol,
            'signal': final_signal,
            'confidence': confidence,
            'indicators': indicators,
            'timestamp': datetime.now().isoformat()
        }
    
    def _prepare_features(self, data: pd.DataFrame, 
                         indicators: Dict) -> pd.DataFrame:
        """Prepare features for AI model"""
        features = {}
        
        # Price features
        features['returns_1'] = data['close'].pct_change(1).iloc[-1]
        features['returns_5'] = data['close'].pct_change(5).iloc[-1]
        features['returns_20'] = data['close'].pct_change(20).iloc[-1]
        
        # Volatility features
        features['volatility_20'] = data['close'].pct_change().rolling(20).std().iloc[-1]
        features['atr_ratio'] = indicators['atr'] / data['close'].iloc[-1]
        
        # Volume features
        features['volume_ratio'] = (data['volume'].iloc[-1] / 
                                   data['volume'].rolling(20).mean().iloc[-1])
        
        # Indicator features
        features['rsi'] = indicators['rsi']
        features['macd'] = indicators['macd']
        features['macd_signal'] = indicators['macd_signal']
        features['bb_position'] = indicators['bb_position']
        features['adx'] = indicators['adx']
        
        return pd.DataFrame([features])
    
    def _combine_signals(self, ai_signal: str, 
                        indicators: Dict, 
                        confidence: float) -> str:
        """Combine AI signal with traditional indicators"""
        
        # Get traditional signals
        trad_signals = []
        
        # RSI signals
        if indicators['rsi'] < 30:
            trad_signals.append(('BUY', 0.3))
        elif indicators['rsi'] > 70:
            trad_signals.append(('SELL', 0.3))
        
        # MACD signals
        if indicators['macd'] > indicators['macd_signal']:
            trad_signals.append(('BUY', 0.4))
        else:
            trad_signals.append(('SELL', 0.4))
        
        # ADX trend strength
        if indicators['adx'] > 25:
            # Strong trend, trust AI more
            ai_weight = 0.7
        else:
            # Weak trend, be more conservative
            ai_weight = 0.5
        
        # Weighted combination
        if confidence < config.CONFIDENCE_THRESHOLD:
            return 'NEUTRAL'
        
        # For simplicity in this example, use AI signal when confident
        # In production, implement proper ensemble voting
        return ai_signal if confidence > 0.7 else 'NEUTRAL'
    
    def _confirm_trend(self, symbol: str, signal: str, 
                      data: pd.DataFrame) -> bool:
        """Confirm trend with multiple timeframes"""
        state = self.pair_states[symbol]
        
        if state['current_signal'] == signal:
            state['consecutive_signals'] += 1
        else:
            state['current_signal'] = signal
            state['consecutive_signals'] = 1
        
        state['last_signal_time'] = datetime.now()
        
        # Require multiple confirmations
        return state['consecutive_signals'] >= config.TREND_CONFIRMATION_BARS
    
    async def execute_strategy(self):
        """Main strategy execution loop"""
        logger.info("Starting AI Trend Follower strategy")
        
        while True:
            try:
                # 1. Check account balance and risk limits
                if not self.risk_manager.check_daily_limit():
                    logger.warning("Daily loss limit reached. Pausing trading.")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue
                
                # 2. Analyze each trading pair
                for symbol in config.TRADING_PAIRS:
                    try:
                        # Fetch recent data
                        klines = self.api_client.get_klines(
                            symbol, interval="5min", limit=100
                        )
                        
                        if not klines:
                            continue
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(klines, columns=[
                            'timestamp', 'open', 'high', 'low', 
                            'close', 'volume'
                        ])
                        df['close'] = pd.to_numeric(df['close'])
                        df['volume'] = pd.to_numeric(df['volume'])
                        
                        # Analyze market
                        signal_data = self.analyze_market(symbol, df)
                        
                        # Log signal
                        self.signals_history.append(signal_data)
                        logger.info(
                            f"{symbol}: {signal_data['signal']} "
                            f"(Confidence: {signal_data['confidence']:.2%})"
                        )
                        
                        # Check for trading opportunity
                        if (signal_data['signal'] != 'NEUTRAL' and 
                            signal_data['confidence'] > config.CONFIDENCE_THRESHOLD):
                            
                            await self._execute_trade(symbol, signal_data)
                            
                    except Exception as e:
                        logger.error(f"Error analyzing {symbol}: {e}")
                        continue
                
                # 3. Manage existing positions
                await self._manage_positions()
                
                # 4. Wait before next analysis
                await asyncio.sleep(60)  # Analyze every minute
                
            except Exception as e:
                logger.error(f"Strategy execution error: {e}")
                await asyncio.sleep(30)
    
    async def _execute_trade(self, symbol: str, signal_data: Dict):
        """Execute trade based on signal"""
        try:
            # 1. Check if we already have a position
            positions = self.api_client.get_positions(symbol)
            has_position = any(
                float(p['positionAmt']) != 0 
                for p in positions if p['symbol'] == symbol
            )
            
            if has_position:
                logger.info(f"Already have position in {symbol}. Skipping.")
                return
            
            # 2. Calculate position size using risk management
            position_size = self.risk_manager.calculate_position_size(
                symbol, signal_data['confidence']
            )
            
            if position_size < config.MIN_TRADE_AMOUNT:
                logger.info(f"Position size too small for {symbol}")
                return
            
            # 3. Get current price
            ticker = self.api_client.get_ticker(symbol)
            current_price = float(ticker['last'])
            
            # 4. Determine order parameters
            side = 'BUY' if signal_data['signal'] == 'BUY' else 'SELL'
            
            # Use limit order near current price
            if side == 'BUY':
                order_price = current_price * 0.998  # 0.2% below
            else:
                order_price = current_price * 1.002  # 0.2% above
            
            # Calculate quantity
            quantity = position_size / order_price
            
            # 5. Set leverage (conservative)
            leverage = min(5, config.MAX_LEVERAGE)  # Start with 5x
            self.api_client.set_leverage(symbol, leverage)
            
            # 6. Place order
            order = self.api_client.place_order(
                symbol=symbol,
                side=side,
                order_type="LIMIT",
                quantity=quantity,
                price=order_price,
                client_order_id=f"AI_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            logger.info(
                f"Placed {side} order for {symbol}: "
                f"{quantity:.6f} @ {order_price:.2f}"
            )
            
            # 7. Set stop loss and take profit
            stop_loss, take_profit = self.risk_manager.calculate_sl_tp(
                order_price, side, signal_data['confidence']
            )
            
            # In production, you'd place these as separate orders
            self.positions[symbol] = {
                'order_id': order['orderId'],
                'side': side,
                'entry_price': order_price,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'signal_data': signal_data
            }
            
        except Exception as e:
            logger.error(f"Trade execution failed for {symbol}: {e}")
    
    async def _manage_positions(self):
        """Manage existing positions (trailing stops, etc.)"""
        for symbol, position in list(self.positions.items()):
            try:
                # Check if order is filled
                order_status = self.api_client.get_order_status(
                    symbol, position['order_id']
                )
                
                if order_status['status'] != 'FILLED':
                    # Cancel if too old
                    order_time = datetime.fromtimestamp(
                        order_status['updateTime'] / 1000
                    )
                    if datetime.now() - order_time > timedelta(minutes=5):
                        self.api_client.cancel_order(symbol, position['order_id'])
                        del self.positions[symbol]
                    continue
                
                # Monitor position for exit conditions
                ticker = self.api_client.get_ticker(symbol)
                current_price = float(ticker['last'])
                
                # Check stop loss
                if ((position['side'] == 'BUY' and 
                     current_price <= position['stop_loss']) or
                    (position['side'] == 'SELL' and 
                     current_price >= position['stop_loss'])):
                    
                    # Exit position
                    exit_side = 'SELL' if position['side'] == 'BUY' else 'BUY'
                    self.api_client.place_order(
                        symbol=symbol,
                        side=exit_side,
                        order_type="MARKET",
                        quantity=position['quantity']
                    )
                    
                    logger.info(
                        f"Stop loss triggered for {symbol}: "
                        f"P&L = {(current_price - position['entry_price']) * position['quantity']:.2f}"
                    )
                    
                    del self.positions[symbol]
                
                # Check take profit
                elif ((position['side'] == 'BUY' and 
                       current_price >= position['take_profit']) or
                      (position['side'] == 'SELL' and 
                       current_price <= position['take_profit'])):
                    
                    exit_side = 'SELL' if position['side'] == 'BUY' else 'BUY'
                    self.api_client.place_order(
                        symbol=symbol,
                        side=exit_side,
                        order_type="MARKET",
                        quantity=position['quantity']
                    )
                    
                    logger.info(
                        f"Take profit hit for {symbol}: "
                        f"P&L = {(current_price - position['entry_price']) * position['quantity']:.2f}"
                    )
                    
                    del self.positions[symbol]
                    
            except Exception as e:
                logger.error(f"Error managing position {symbol}: {e}")
