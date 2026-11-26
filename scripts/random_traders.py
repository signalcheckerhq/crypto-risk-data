"""Rebuild data/random-traders-oct-nov-2026.csv: 500 coin-flip traders on real BTC prices.

Prices: Coinbase BTC-USD 1-hour candles. Two "months": Sep 26 - Oct 26 and Oct 26 - Nov 25, 2026 (UTC).
Each month, every trader makes 90 trades. A trade takes one random, non-overlapping 4-hour block,
goes long or short by coin flip at 3x leverage, enters at the block's open, exits at its close,
and pays a 0.05% fee per side (on the leveraged size). Returns compound trade by trade.
The random generator is numpy default_rng(seed=1), as in the published file.
"""
import csv, json, time, urllib.request, datetime as dt
import numpy as np

LEV, FEE, HOLD, NTR, N = 3.0, 0.0005, 4, 90, 500


def ts(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp())


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


A0, A1, B1 = ts('2026-09-26'), ts('2026-10-26'), ts('2026-11-25')
bars, start = {}, A0
while start < B1:
    end = min(start + 300 * 3600, B1)
    url = f'https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600&start={iso(start)}&end={iso(end)}'
    for r in json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'crypto-risk-data'}))):
        if A0 <= r[0] < B1:
            bars[r[0]] = r
    start = end
    time.sleep(0.4)
t = np.array(sorted(bars))
o = np.array([bars[k][3] for k in t], float)
c = np.array([bars[k][4] for k in t], float)
ia = np.where((t >= A0) & (t < A1))[0]
ib = np.where((t >= A1) & (t < B1))[0]


def month(idx, rng):
    nb = len(idx) // HOLD
    blocks = np.sort(rng.choice(nb, NTR, replace=False))
    side = rng.choice([-1, 1], NTR)
    e = 1.0
    for b, s in zip(blocks, side):
        first, last = idx[b * HOLD], idx[b * HOLD + HOLD - 1]
        e = e * (1 - LEV * FEE) * (1 + s * LEV * (c[last] / o[first] - 1)) * (1 - LEV * FEE)
    return e - 1


rng = np.random.default_rng(1)
fa = np.array([month(ia, rng) for _ in range(N)])
fb = np.array([month(ib, rng) for _ in range(N)])
ra = (-fa).argsort().argsort() + 1
rb = (-fb).argsort().argsort() + 1
with open('random-traders-oct-nov-2026.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['trader_id', 'oct_return', 'nov_return', 'oct_rank', 'nov_rank'])
    for i in range(N):
        w.writerow([i + 1, round(fa[i], 4), round(fb[i], 4), int(ra[i]), int(rb[i])])
top = int(np.argmax(fa))
print(f'Oct #1: {fa[top]:+.1%} in Oct, {fb[top]:+.1%} in Nov (rank {rb[top]} of {N})')
