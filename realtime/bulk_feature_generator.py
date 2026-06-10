#!/usr/bin/env python3
# REFINED & EXPANDED
# Date: 2025-07-21
# Task: Generates over 800 feature permutations with improved organization
# Source: Enhanced version based on technical analysis best practices

import pandas_ta as ta
import logging
from .feature_registry import FeatureRegistry
from itertools import product
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('BulkFeatureGenerator')

def generate_bulk_features(registry: FeatureRegistry):
    """Generates comprehensive technical analysis features with parameter variations"""
    logger.info("Starting bulk generation of enhanced feature set...")
    feature_count = 0

    # Enhanced parameter ranges
    short_periods = [3, 5, 8, 10, 14, 21]
    medium_periods = [30, 50, 65, 75]
    long_periods = [100, 150, 200, 250]
    all_periods = sorted(list(set(short_periods + medium_periods + long_periods)))
    std_devs = [1, 1.5, 2, 2.5, 3]
    smoothing_periods = [3, 5, 8, 10]
    drift_periods = [1, 2, 3]
    
    # --- Single Parameter Indicators (Enhanced) ---
    single_param_indicators = {
        "momentum": {
            "rsi": all_periods,
            "cci": all_periods,
            "roc": all_periods,
            "willr": all_periods,
            "mom": all_periods,
            "mfi": all_periods,
            "efi": all_periods,
            "stochrsi": short_periods,
            "tsi": medium_periods,
            "uo": all_periods,
            "kvo": medium_periods,
            "pvo": medium_periods,
            "fisher": medium_periods
        },
        "trend": {
            "sma": all_periods,
            "ema": all_periods,
            "dema": all_periods,
            "tema": all_periods,
            "wma": all_periods,
            "hma": all_periods,
            "jma": all_periods,
            "kama": all_periods,
            "zlma": all_periods,
            "vidya": all_periods,
            "sinwma": all_periods
        },
        "volatility": {
            "atr": all_periods,
            "natr": all_periods,
            "rvi": all_periods,
            "thermo": medium_periods,
            "mass": medium_periods
        },
        "volume": {
            "cmf": all_periods,
            "eom": medium_periods,
            "nvi": long_periods,
            "pvi": long_periods
        }
    }

    # Generate single-param features
    for category, indicators in single_param_indicators.items():
        for func_name, periods in indicators.items():
            for length in periods:
                name = f"{func_name}_l{length}"
                description = f"{func_name.upper()} over {length} periods"
                code = f"df.ta.{func_name}(length={length}, append=True)"
                registry.add_feature_idea(name, description, category, code)
                feature_count += 1
                
    # --- Multi-Parameter Indicators (Expanded) ---
    
    # MACD Variations
    fast_periods = [8, 12, 15, 20]
    slow_periods = [21, 26, 35, 50]
    signal_periods = [5, 9, 12, 16]
    for fast, slow, signal in product(fast_periods, slow_periods, signal_periods):
        if fast >= slow: continue
        name = f"macd_f{fast}_s{slow}_sig{signal}"
        description = f"MACD(fast={fast}, slow={slow}, signal={signal})"
        code = f"df.ta.macd(fast={fast}, slow={slow}, signal={signal}, append=True)"
        registry.add_feature_idea(name, description, 'momentum', code)
        feature_count += 1

    # Bollinger Bands with more variations
    for length, std in product(long_periods, std_devs):
        name = f"bbands_l{length}_s{std}"
        description = f"Bollinger Bands({length} periods, {std} std dev)"
        code = f"df.ta.bbands(length={length}, std={std}, append=True)"
        registry.add_feature_idea(name, description, 'volatility', code)
        feature_count += 1

    # Stochastic with additional parameters
    k_periods = [10, 14, 20, 25]
    d_periods = [3, 5, 7]
    smooth_k_periods = [3, 5, 8]
    for k, d, smooth_k in product(k_periods, d_periods, smooth_k_periods):
        name = f"stoch_k{k}_d{d}_s{smooth_k}"
        description = f"Stochastic(k={k}, d={d}, smooth_k={smooth_k})"
        code = f"df.ta.stoch(k={k}, d={d}, smooth_k={smooth_k}, append=True)"
        registry.add_feature_idea(name, description, 'momentum', code)
        feature_count += 1

    # ADX with Wilder smoothing
    for length in [10, 14, 20, 25, 30]:
        name = f"adx_l{length}"
        description = f"ADX with {length}-period Wilder smoothing"
        code = f"df.ta.adx(length={length}, lensig={length}, append=True)"
        registry.add_feature_idea(name, description, 'trend', code)
        feature_count += 1

    # Aroon Indicator
    for length in [14, 20, 25, 30]:
        name = f"aroon_l{length}"
        description = f"Aroon({length} periods)"
        code = f"df.ta.aroon(length={length}, append=True)"
        registry.add_feature_idea(name, description, 'trend', code)
        feature_count += 1

    # SuperTrend with multiple variations
    periods = [7, 10, 14, 20, 25]
    multipliers = [2, 3, 4, 5]
    for period, multiplier in product(periods, multipliers):
        name = f"supertrend_p{period}_m{multiplier}"
        description = f"SuperTrend(period={period}, multiplier={multiplier})"
        code = f"df.ta.supertrend(period={period}, multiplier={multiplier}, append=True)"
        registry.add_feature_idea(name, description, 'trend', code)
        feature_count += 1

    # Vortex Indicator
    for length in [14, 20, 25, 30]:
        name = f"vortex_l{length}"
        description = f"Vortex({length} periods)"
        code = f"df.ta.vortex(length={length}, append=True)"
        registry.add_feature_idea(name, description, 'trend', code)
        feature_count += 1

    # KST Oscillator with variations
    roc_periods = [(10,15), (10,20), (15,20), (20,30)]
    sma_periods = [(10,10), (10,15), (15,15)]
    signal_periods = [9, 12, 15]
    for roc, sma, signal in product(roc_periods, sma_periods, signal_periods):
        name = f"kst_roc{roc[0]}_{roc[1]}_sma{sma[0]}_{sma[1]}_sig{signal}"
        description = f"KST(ROC={roc}, SMA={sma}, signal={signal})"
        code = f"""df.ta.kst(
    roc1={roc[0]}, roc2={roc[1]}, roc3={roc[0]}, roc4={roc[1]}, 
    sma1={sma[0]}, sma2={sma[1]}, sma3={sma[0]}, sma4={sma[1]}, 
    signal={signal}, append=True
)"""
        registry.add_feature_idea(name, description, 'momentum', code)
        feature_count += 1

    # Donchian Channel
    for length in [20, 30, 40, 50]:
        name = f"donchian_l{length}"
        description = f"Donchian Channel({length} periods)"
        code = f"df.ta.donchian(lower_length={length}, upper_length={length}, append=True)"
        registry.add_feature_idea(name, description, 'volatility', code)
        feature_count += 1

    # --- Parameter-less Indicators (Expanded) ---
    zero_param_indicators = [
        ('obv', 'On-Balance Volume', 'volume'),
        ('pvi', 'Positive Volume Index', 'volume'),
        ('nvi', 'Negative Volume Index', 'volume'),
        ('ad', 'Accumulation/Distribution', 'volume'),
        ('vp', 'Volume Profile', 'volume'),
        ('vpt', 'Volume Price Trend', 'volume'),
        ('pvol', 'Price Volume', 'volume'),
        ('pvt', 'Price Volume Trend', 'volume'),
        ('true_range', 'True Range', 'volatility'),
        ('entropy', 'Spectral Entropy', 'momentum'),
        ('inertia', 'Inertia Indicator', 'momentum'),
        ('kjs', 'Kurtosis, Jensen-Shannon', 'statistical')
    ]
    
    for name, desc, category in zero_param_indicators:
        registry.add_feature_idea(name, desc, category, f"df.ta.{name}(append=True)")
        feature_count += 1

    # --- Advanced Indicators (New) ---
    
    # Fractal Energy Bands
    for length in [10, 14, 20, 30]:
        name = f"fractal_l{length}"
        description = f"Fractal Energy Bands({length} periods)"
        code = f"df.ta.fractal(length={length}, append=True)"
        registry.add_feature_idea(name, description, 'volatility', code)
        feature_count += 1

    # Elastic Volume Weighted MA
    for length in [10, 20, 30, 50]:
        name = f"evwma_l{length}"
        description = f"Elastic Volume Weighted MA({length} periods)"
        code = f"df.ta.ewma(volume, length={length}, append=True)"
        registry.add_feature_idea(name, description, 'trend', code)
        feature_count += 1

    # Chande Kroll Stop
    periods = [10, 14, 20]
    multipliers = [2, 3, 4]
    for period, multiplier in product(periods, multipliers):
        name = f"cks_p{period}_m{multiplier}"
        description = f"Chande Kroll Stop({period} periods, {multiplier}xATR)"
        code = f"df.ta.cks(period={period}, multiplier={multiplier}, append=True)"
        registry.add_feature_idea(name, description, 'trend', code)
        feature_count += 1

    # Gann High-Low Activator
    for length in [5, 10, 14, 20]:
        name = f"ghla_l{length}"
        description = f"Gann HiLo Activator({length} periods)"
        code = f"df.ta.ghla(length={length}, append=True)"
        registry.add_feature_idea(name, description, 'trend', code)
        feature_count += 1

    logger.info(f"Generated and added {feature_count} technical features to the registry")

if __name__ == '__main__':
    db_connection_params = {
        "dbname": "cta_db", "user": "postgre", "password": "a",
        "host": "localhost", "port": "5432"
    }
    registry = None
    try:
        registry = FeatureRegistry(db_params=db_connection_params)
        generate_bulk_features(registry)
    except Exception as e:
        logger.error(f"Feature generation error: {e}", exc_info=True)
    finally:
        if registry:
            registry.close()