# DecisiveML
[![Build Status](https://travis-ci.com/decisivealpha/decisiveml.svg?branch=master)](https://travis-ci.com/decisivealpha/decisiveml)
[![PyPi](https://img.shields.io/pypi/v/decisiveml)](https://pypi.org/project/decisiveml/)
[![Python](https://img.shields.io/pypi/pyversions/decisiveml.svg)](https://pypi.org/project/decisiveml/)
[![Discord Chat](https://img.shields.io/discord/594866572104040498.svg)](https://discord.gg/zQRSUhF)

Machine learning end-to-end research and trade execution

## Install

pip install decisiveml

## Develop

Dependency management uses [poetry](https://github.com/python-poetry/poetry), test suite is [nose](https://github.com/nose-devs/nose), and code style is [black](https://github.com/psf/black).

To develop:

1. Initialize with `make install`
2. Run tests with: `make test`

## Examples

See [notebooks](https://github.com/decisivealpha/DecisiveML/tree/master/notebooks) for more

### Trend Scanning

See [docs](https://github.com/decisivealpha/DecisiveML/tree/master/docs/trend_scanning.md) for more on Trend Scanning

```python
import decisiveml as dml
import numpy as np
import pandas as pd

# Generate random price history
raw_frame = pd.DataFrame(index=pd.date_range("2018-12-01", "2019-07-01"))
raw_frame["equity"] = (np.random.randn(raw_frame.shape[0]) / 100).cumsum()
raw_frame["close"] = 48.76 * (1 + raw_frame["equity"])

# Use a cross-over signal as entry
df = raw_frame["2019-01-01":"2019-06-01"].copy()
df["mavg"] = df.close.rolling(10).mean()
m_crossabove = (df.close.shift(1) < df.mavg) & (df.close > df.mavg)
m_crossbelow = (df.close.shift(1) > df.mavg) & (df.close < df.mavg)
df["entry"] = df[m_crossabove | m_crossbelow].close

# Calculate trendscanning
trend = dml.getBinsFromTrend(
    molecule=df["entry"].dropna().index, close=df.close, span=[22, 44, 11],
)
```

### Monte Carlo

See [docs](https://github.com/decisivealpha/DecisiveML/tree/master/docs/monte_carlo.md) for more on Monte Carlo

```python
import decisiveml as dml

# set up margin requirements for instrument
margin = 5000
start_date = datetime.date(2016, 1, 1)
end_date = datetime.date(2018, 1, 1)

# list of trades
trades_list = random.sample(range(-2000, 2300), 100)

# Initialize
mc = dml.MonteCarlo(trades_list)

# We will sample with replacement the number of trades per year
# so we need the start and end date to determine how many trades at in a year on average
mc.settings(margin, start_date, end_date)

# Test different levels of equity starting at this value
trial_starting_equity = int(margin * 1.5)

# Run the Monte Carlo
results = mc.run(trial_starting_equity)

# Results:
# ========
# Recommend a starting equity of 15000.0, which has 5.9% Risk-of-Ruin, 81% Probability-of-Profit and a 1.65 Returns/Drawdown Ratio
# Risk Assessment: FAILED
# MC-Drawdown: 30.2% MC-1.5x-DD: 45.2%
# Average monthly net profit: 307.8
```

## Support

Discuss in [Discord](https://discord.gg/zQRSUhF)
