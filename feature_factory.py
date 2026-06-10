# 🔧 FeatureFactory: Initial Implementation
# File: src/feature_factory/feature_factory.py
# Purpose: Compute core tick-level features (mid-price, spread, return, volume)

from typing import Dict, Any

class FeatureFactory:
    """
    Core Feature Factory for computing primary tick features.
    Maintains in-memory state (last mid-price) per symbol for return calculation.
    """

    def __init__(self):
        # Store last mid-price for each symbol to compute returns
        self._last_mid_price: Dict[str, float] = {}

    def compute_features(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        :param raw: A dict parsed from the raw Kafka message with keys:
                    'symbol', 'timestamp', 'bid', 'ask', 'volume' (optional)
        :return: A dict of computed features:
                 - symbol
                 - timestamp
                 - bid
                 - ask
                 - mid_price
                 - spread
                 - mid_return (0.0 on first tick)
                 - volume (if present)
        """
        symbol = raw.get('symbol')
        bid = float(raw['bid'])
        ask = float(raw['ask'])
        # mid price and spread
        mid = (bid + ask) / 2.0
        spread = ask - bid

        # compute return relative to the last mid price
        last_mid = self._last_mid_price.get(symbol)
        if last_mid is not None and last_mid > 0:
            mid_return = (mid - last_mid) / last_mid
        else:
            mid_return = 0.0

        # update stored mid price
        self._last_mid_price[symbol] = mid

        features = {
            'symbol': symbol,
            'timestamp': raw.get('timestamp'),
            'bid': bid,
            'ask': ask,
            'mid_price': mid,
            'spread': spread,
            'mid_return': mid_return,
        }

        # include volume if provided
        if 'volume' in raw:
            features['volume'] = float(raw['volume'])

        return features
