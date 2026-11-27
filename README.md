# Crypto risk data (free CSV, CC BY 4.0)

Also on [Hugging Face](https://huggingface.co/datasets/SignalCheckerHQ/crypto-risk-data) and [Kaggle](https://www.kaggle.com/datasets/signalcheckerhq/crypto-leverage-survival-and-leaderboard-luck).

Two small datasets computed from public **Coinbase 1-hour prices**, made for people who want to check
trading claims with numbers instead of screenshots. Both files are plain CSV, free to use, share and adapt
with credit.

| File | Rows | What it shows |
|---|---|---|
| [`data/leverage-survival-by-coin-2026-11.csv`](data/leverage-survival-by-coin-2026-11.csv) | 288 | For 8 coins, how often each leverage from 2x to 100x would have been liquidated by normal price swings |
| [`data/random-traders-oct-nov-2026.csv`](data/random-traders-oct-nov-2026.csv) | 500 | 500 coin-flip traders over two months: how much of a leaderboard is luck |

## 1. Which leverage survived (`leverage-survival-by-coin-2026-11.csv`)

Coins: BTC, ETH, SOL, XRP, DOGE, ADA, AVAX, LINK. For each coin, every one of the last 1,000 closed hours
(Oct 15 – Nov 25, 2026) is taken as an entry at that hour's close, held **24 hours** or **168 hours** (one week),
long and short. A position counts as liquidated if the price moved against it by at least
`1/leverage − 0.5%` within the holding time (isolated margin, 0.5% maintenance margin), using each candle's
low (long) or high (short). Fees and funding are not included, so real liquidation can come a little earlier.

| Column | Meaning |
|---|---|
| `coin` | Coin symbol (priced in USD on Coinbase) |
| `side` | `long` or `short` |
| `hold_hours` | 24 or 168 |
| `leverage` | 2, 3, 5, 10, 20, 25, 50, 75 or 100 |
| `entries` | Number of hourly entries tested (1,000) |
| `share_liquidated` | Share of entries that would have been liquidated (0 to 1) |
| `first_entry_utc`, `last_entry_utc` | Date range of the entries |

Example: BTC long, held 24 hours: 0% liquidated at 5x, 1.1% at 10x, 21.1% at 25x, 57% at 50x.

## 2. Leaderboard luck (`random-traders-oct-nov-2026.csv`)

500 simulated traders with no skill at all, on real BTC-USD 1-hour prices. Each "month"
(Sep 26 – Oct 26 and Oct 26 – Nov 25, 2026, UTC) every trader makes 90 trades: a random 4-hour block,
long or short by coin flip, 3x leverage, 0.05% fee per side. Returns compound trade by trade.

| Column | Meaning |
|---|---|
| `trader_id` | 1–500 |
| `oct_return`, `nov_return` | Return for each month (0.25 = +25%) |
| `oct_rank`, `nov_rank` | Rank among the 500 that month (1 = best) |

What it shows: the October #1 made **+25.0%**, then finished November at **−48.2%** (rank 423 of 500).
Only 24 of 500 were in profit after fees in October. A leaderboard of random traders still has a "best trader".

## Rebuild the files

```bash
pip install numpy
python3 scripts/random_traders.py          # writes random-traders-oct-nov-2026.csv
python3 scripts/leverage_survival.py 2026-11-26T16:00   # writes leverage-survival-by-coin-2026-11.csv
```

The scripts download the candles from Coinbase's public API (no key). Coinbase sometimes revises old candles,
so a rerun can differ slightly from the published files: in a check on Nov 26, 2026 the October returns were
identical, November returns differed by at most 0.17 percentage points, and `share_liquidated` by at most
0.025. The headline results above were unchanged.

## License and credit

- Data (`data/`): [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0).
  Credit: "SignalCheckerHQ (signalcheckerhq.org/data/)".
- Scripts (`scripts/`): MIT License.

Past prices, not forecasts. Nothing here is financial advice.

Made by [SignalCheckerHQ](https://signalcheckerhq.org/data/). The same leverage check for any coin, live:
[leverage survival check](https://signalcheckerhq.org/leverage-survival-calculator/).
