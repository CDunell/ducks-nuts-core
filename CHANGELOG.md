# Changelog

## [Phase 11] - Symbol Management

### Changes
- Replaced dynamic Binance top-10-by-volume selection with a pinned symbol list
- Removed DOGE, added HYPE (Hyperliquid) to the default symbol set
- Replaced `requests`-based `get_top_10_usdt_pairs()` with `realtime/symbols.py` as the single source of truth for all symbol tracking

### New: `realtime/symbols.py`
Persistent symbol store backed by `data/symbols.json` (auto-seeded from defaults on first run).  
Override store path via `SYMBOLS_PATH` env var.

| Function | Description |
|---|---|
| `load()` | Returns full list of `{symbol, enabled}` dicts |
| `active()` | Returns uppercase symbol strings for enabled entries only |
| `save(data)` | Persists the list back to disk |

Both the realtime tick processor (`tick_processor_zmq.py`) and the backfill runner (`batch.py`) call `active()` at startup — changes take effect on next process restart, no code edits required.

### New: CLI `symbols` sub-commands

```
python -m backfill.cli symbols list                  # show all symbols + enabled/disabled state
python -m backfill.cli symbols add <SYMBOL>          # add new symbol (enabled by default)
python -m backfill.cli symbols enable <SYMBOL>       # re-enable a disabled symbol
python -m backfill.cli symbols disable <SYMBOL>      # pause tracking without removing
python -m backfill.cli symbols remove <SYMBOL>       # permanent delete (prompts unless --yes)
```

### Audit fixes (Phase 11 cleanup)
- Removed unused `import asyncio` from `batch.py`
- Removed unused `active_symbols` import from `cli.py`
- Renamed `backfill_top_symbols` → `backfill_pinned_symbols` (function name was a misnomer)
- Removed stale `--limit` option from `bulk` CLI command
- Updated `bulk` command help text to reflect pinned-symbol behaviour
- Added `.gitignore` (excludes `.env`, `__pycache__`, `*.duckdb`, `data/`, etc.)

## [Phase 10] - RL Engine & Memory
- Added `rl_engine.py` and `rl_memory.py`
- Trade outcome reward logic complete
- Memory buffer ready for future Q-learning

## [Phase 9] - Cluster Integration
- Added `cluster_engine.py` and `cluster_config.py`
- Clustering snapshot logic fully integrated
- Enrichment and strategy routing fully patched