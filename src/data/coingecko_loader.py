import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger("CoinGeckoLoader")

class CoinGeckoLoader:
    def __init__(self, vs_currency='usd'):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.vs_currency = vs_currency
        self.session = requests.Session()
        # Simple cache to avoid rate limits
        self._market_cache = None
        self._last_fetch = 0
        self.cache_ttl = 60  # seconds

    def _request(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API Error: {e}")
            return None

    def get_market_data(self, page=1, per_page=100):
        """Fetch market data (price, vol, change) for top coins."""
        endpoint = "/coins/markets"
        params = {
            "vs_currency": self.vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        return self._request(endpoint, params)

    def scan_market_opportunities(self, top_n=200):
        """
        Scans top coins to find high-volatility opportunities.
        Returns a DataFrame of potential candidates with high 24h volatility.
        """
        # Check cache
        if self._market_cache is not None and (time.time() - self._last_fetch < self.cache_ttl):
            return self._market_cache

        logger.info("Scanning CoinGecko markets for opportunities...")
        all_coins = []
        
        # Fetch first 2 pages (top 200 coins)
        for page in range(1, 3):
            data = self.get_market_data(page=page)
            if data:
                all_coins.extend(data)
            time.sleep(1.5) # Compliance with free tier rate limits (Approx 10-30 req/min)

        if not all_coins:
            return pd.DataFrame()

        df = pd.DataFrame(all_coins)
        
        # Filter relevant columns
        cols = ['id', 'symbol', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']
        if not set(cols).issubset(df.columns):
            logger.warning("Missing columns in CoinGecko data")
            return pd.DataFrame()
            
        df = df[cols]
        
        # Calculate a simple 'Volatility Score' (abs change)
        df['volatility_score'] = df['price_change_percentage_24h'].abs()
        
        # Filter for logic:
        # 1. Volume must be > 1M (liquidity check)
        # 2. Volatility score > 3% (needs movement)
        opportunities = df[
            (df['total_volume'] > 1_000_000) & 
            (df['volatility_score'] > 3.0)
        ].sort_values(by='volatility_score', ascending=False)

        self._market_cache = opportunities
        self._last_fetch = time.time()
        
        return opportunities

    def get_historical_prices(self, coin_id, days=30):
        """Fetch basic OHLC for backtesting (free tier limitation: daily candles mostly)."""
        endpoint = f"/coins/{coin_id}/ohlc"
        params = {"vs_currency": self.vs_currency, "days": days}
        data = self._request(endpoint, params)
        
        if not data:
            return None
            
        # Format: [time, open, high, low, close]
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

if __name__ == "__main__":
    # Test Run
    logging.basicConfig(level=logging.INFO)
    cg = CoinGeckoLoader()
    opps = cg.scan_market_opportunities()
    print("Top Opportunities found:")
    print(opps.head(5))
