# README

Machine learning exploration

## Install

pip install decisiveml

## Develop

Dependency management uses [poetry](https://github.com/python-poetry/poetry), and test suite is [nose](https://github.com/nose-devs/nose).

To develop:

1. Install requirements with: `poetry install` or `make install`
2. Run tests with: `nosetests` or `make test`

## Examples

See [notebooks](https://github.com/decisivealpha/DecisiveML/tree/master/notebooks) for more

### Trend Scanning

[Read user comments on reddit for Trend Scanning](https://www.reddit.com/r/algotrading/comments/g0idrl/trend_scanning_for_machine_learning_models/)

```
  import numpy as np
  import pandas as pd
  import decisiveml as dml
  
  # Generate random price history
  raw_frame = pd.DataFrame(index=pd.date_range("2018-12-01", "2019-07-01"))
  raw_frame["equity"] = (np.random.randn(raw_frame.shape[0])/100).cumsum()
  raw_frame["close"] = 48.76 * (1 + raw_frame["equity"])
  
  # Use a cross-over signal as entry
  df = raw_frame["2019-01-01":"2019-06-01"].copy()
  df["mavg"] = df.close.rolling(10).mean()
  m_crossabove = (df.close.shift(1) < df.mavg) & (df.close > df.mavg)
  m_crossbelow = (df.close.shift(1) > df.mavg) & (df.close < df.mavg)
  df["entry"] = df[m_crossabove | m_crossbelow].close

  # Calculate trendscanning
  trend = dml.getBinsFromTrend(
      molecule=df["entry"].dropna().index, 
      close=df.close, 
      span=[22, 44, 11],
  )
```

### Monte Carlo

[Read user comments on reddit for Monte Carlo](https://www.reddit.com/r/algotrading/comments/g2aqhw/identify_alpha_decay_with_monte_carlo/)

```
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
