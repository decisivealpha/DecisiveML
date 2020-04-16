from nose.tools import eq_
import numpy as np
import pandas as pd
import decisiveml as dml


def test_trendscanning():
    """Test trend scanning"""
    # Generate random price history
    raw_frame = pd.DataFrame(index=pd.date_range("2018-12-01", "2019-07-01"))
    np.random.seed(0)
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
    eq_(trend.iloc[1].bin, 1)
    eq_(trend.iloc[-1].bin, -1)
    eq_(trend.bin.sum(), 12)
