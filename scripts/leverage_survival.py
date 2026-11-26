"""Rebuild data/leverage-survival-by-coin-2026-11.csv from public Coinbase 1-hour candles.

For each coin, each of the last 1,000 closed hours is taken as an entry (close price).
A position "is liquidated" if, within the holding time (24 h or 168 h), the price moved
against it by at least 1/leverage - 0.5% (isolated margin, 0.5% maintenance margin),
using each candle's low (long) or high (short).

Usage: python3 leverage_survival.py [END_UTC]   e.g. 2026-11-26T16:00
END_UTC is the first hour NOT used (the published file used 2026-11-26T16:00).
"""
import csv, json, sys, time, urllib.request, datetime as dt
import numpy as np

COINS = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 'LINK']
LEVS = [2, 3, 5, 10, 20, 25, 50, 75, 100]
MM = 0.005
end_arg = sys.argv[1] if len(sys.argv) > 1 else '2026-11-26T16:00'
NOW = int(dt.datetime.strptime(end_arg, '%Y-%m-%dT%H:%M').replace(tzinfo=dt.timezone.utc).timestamp()) // 3600 * 3600


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def candles(coin):
    """1,500 closed hourly candles before NOW: [time, low, high, open, close, volume]."""
    out, end = {}, NOW
    for _ in range(5):
        start = end - 300 * 3600
        url = f'https://api.exchange.coinbase.com/products/{coin}-USD/candles?granularity=3600&start={iso(start)}&end={iso(end)}'
        for row in json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'crypto-risk-data'}))):
            if row[0] < NOW:
                out[row[0]] = row
        end = start
        time.sleep(0.4)
    return [out[t] for t in sorted(out)]


rows = []
for coin in COINS:
    cs = candles(coin)
    for hold in (24, 168):
        n = min(1000, len(cs) - hold)
        off = len(cs) - hold - n
        for side in ('long', 'short'):
            worst = []
            for i in range(n):
                entry = cs[off + i][4]
                m = 0.0
                for k in range(1, hold + 1):
                    b = cs[off + i + k]
                    m = max(m, (entry - b[1]) / entry if side == 'long' else (b[2] - entry) / entry)
                worst.append(m)
            worst = np.array(worst)
            for lev in LEVS:
                need = 1 / lev - MM
                share = float((worst >= need).mean()) if need > 0 else 1.0
                rows.append([coin, side, hold, lev, n, round(share, 4),
                             dt.datetime.fromtimestamp(cs[off][0], dt.timezone.utc).date(),
                             dt.datetime.fromtimestamp(cs[off + n - 1][0], dt.timezone.utc).date()])
    print(coin, len(cs), 'candles')

with open('leverage-survival-by-coin-2026-11.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['coin', 'side', 'hold_hours', 'leverage', 'entries', 'share_liquidated', 'first_entry_utc', 'last_entry_utc'])
    w.writerows(rows)
print(len(rows), 'rows written')
