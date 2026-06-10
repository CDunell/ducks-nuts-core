def select_strategy(signal: dict) -> str:
    if "pattern_cluster" in signal:
        cluster = signal["pattern_cluster"]
        if cluster == 0:
            return "rsi_filtered_ma"
        elif cluster == 1:
            return "ema_trend_pullback"
        elif cluster == 2:
            return "volume_spike_fade"
        else:
            return "zscore_mean_reversion"
    return "default_strategy"