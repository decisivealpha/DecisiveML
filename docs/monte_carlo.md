# Monte Carlo for Algotrading

Subject: Identify Alpha Decay with Monte Carlo

The code is here: [Link](https://github.com/decisivealpha/DecisiveML/blob/master/notebooks/2.0-DVR-MonteCarloRiskOfRuin.ipynb)

There are many ways to use Monte Carlo in algotrading, from generating random price series for backtesting to risk managing in live trading.

I'll talk about Monte Carlo in sizing your portfolio and identifying alpha decay. Monte Carlo can answer these questions:

- How much equity should I allocate to this strategy?
- When does a strategy stop working (alpha decay)?


## Equity

The Monte Carlo analysis will calculate your median drawdown, plus a buffer, which you can add on to your instrument margin for your starting equity:

If you're starting out with futures, you're probably trading 1 lot.  So your minimum equity (i.e. equity at failure) should be the margin of the account.  The additional equity is to allow for the expected drawdown to not knock you out.

Since your drawdown is a function of your starting equity, you want to *maximize* it to avoid "ruin" (i.e. hitting your minimum equity) and *minimize it* to increase opportunity cost (i.e. dead money)

## Alpha Decay

The Monte Carlo analysis adds a buffer to your expected (i.e. median) drawdown that you saw in research.

Your strategy will observe alpha decay when the market has changed from your research/backtesting, and gives you a heads up to turn off your strategy.  The code above uses 1.5x the median monte carlo drawdown for alpha decay detection, but of course, you can use any other.  Here is a screenshot of this in practice -- the red line is when you will turn off the strategy due to alpha decay:
https://i.imgur.com/bfz3ti7.png


## Conclusion

Don't undersize your strategy starting equity.  Let your edge play out by giving it enough equity to handle the expected drawdowns.

Here's a screenshot of the Monte Carlo table:
https://i.imgur.com/8OsRrDO.png

The code is here: [Link](https://github.com/decisivealpha/DecisiveML/blob/master/notebooks/2.0-DVR-MonteCarloRiskOfRuin.ipynb)


