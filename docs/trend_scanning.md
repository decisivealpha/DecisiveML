# Trend Scanning 
   
Subject: Trend Scanning for Machine Learning Models (alternative to symmetric barriers re:Meta Labeling)

Here's a link to the notebook: [Link](https://github.com/decisivealpha/DecisiveML/blob/master/1.1-DVR-Research-TrendScanning.ipynb)

The Trend Scanning idea from Marcos Lopez de Prado, is released in his newest book here (free DL until May).  He first mentioned it earlier last year, and added a few code snippets in his [book Machine Learning for Asset managers](https://www.cambridge.org/core/elements/machine-learning-for-asset-managers/6D9211305EA2E425D33A9F38D0AE3545).  

MLdP code snippets are sparse, likely to fit it on printed page, so I added docstrings to make it easier to see (see link [here](https://github.com/decisivealpha/DecisiveML/blob/master/trendscanning.py))

Trend Scanning is not a trading model in itself, but extended to form a model. A few ideas for a trading model: 

- Classify trend for recent history. If probability of "long" is > 50% and your entry signal is long, enter. Exit with your favorite stop loss method.
- Classify trend for two products, e.g. S&P and Gold. Enter on S&P crossover, exit when Gold trend changes
- Use "t1" output as a feature for meta-labeling (i.e. a lagged trend as a feature)

Here's a screenshot:

[https://i.imgur.com/wrOMx5J.png](https://i.imgur.com/wrOMx5J.png)
