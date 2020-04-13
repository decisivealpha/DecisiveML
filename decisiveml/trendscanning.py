import pandas as pd
import numpy as np
import statsmodels.api as sm1


def tValLinR(close):
    """tValue from a linear trend via SNIPPET 5.1 T-VALUE OF A LINEAR TREND

    Args:
        close (Series): close prices to search through

    Returns:
        float: t-value

    Example:
        >>> lookforward = 5
        >>> start = 0
        >>> stop = stop + lookforward
        >>> df1 = close.iloc[start:stop]
        >>> tValLinR(df1.values)

    """
    x = np.ones((close.shape[0], 2))
    x[:, 1] = np.arange(close.shape[0])
    ols = sm1.OLS(close, x).fit()
    return ols.tvalues[1]


def getBinsFromTrend(molecule, close, span):
    """Derive labels from the sign of t-value of linear trend via SNIPPET 5.2
    IMPLEMENTATION OF THE TREND-SCANNING METHOD

    Args:
        molecule (DatetimeIndex): start times of the event
        close (Series): close prices of your large df
        span (args for range): list: [start, stop, step]

    Returns:
        pd.DataFrame: trends
            - t1: End time for the identified trend
            - tVal: t-value associated with the estimated trend coefficient
            - bin: Sign of the trend

    Example:
        >>> df["mavg"] = df.close.rolling(10).mean()
        >>> df["entry"] = df[(df.close.shift(1) < df.mavg) & (df.close > df.mavg)].close
        >>> getBinsFromTrend(molecule=df["entry"].dropna().index, close=df.close, span=[5, 20, 5])
    """

    out = pd.DataFrame(index=molecule, columns=["t1", "tVal", "bin"])
    hrzns = range(*span)

    for dt0 in molecule:
        df0 = pd.Series()
        iloc0 = close.index.get_loc(dt0)
        if iloc0 + max(hrzns) > close.shape[0]:
            continue

        for hrzn in hrzns:
            dt1 = close.index[iloc0 + hrzn - 1]
            df1 = close.loc[dt0:dt1]
            df0.loc[dt1] = tValLinR(df1.values)

        dt1 = df0.replace([-np.inf, np.inf, np.nan], 0).abs().idxmax()
        out.loc[dt0, ["t1", "tVal", "bin"]] = (
            df0.index[-1],
            df0[dt1],
            np.sign(df0[dt1]),
        )  # prevent leakage

    out["t1"] = pd.to_datetime(out["t1"])
    out["bin"] = pd.to_numeric(out["bin"], downcast="signed")

    return out.dropna(subset=["bin"])
