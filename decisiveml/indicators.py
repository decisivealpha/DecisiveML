#!/usr/bin/env python3
import numpy as np
import pandas as pd
import logging
from decisiveml.helpers import tradingday_offset

logger = logging.getLogger(__name__)


def indicator_volatility_daily(df_daily, price_col="close"):
    """Create rolling volatility using EWM of 36 which matches a rolling stdev of 25

    Args:
        df_daily (frame): contains "close" column
        price_col (str): "close" is default

    Returns:
        frame: index = index of df_daily, adds colum called vol36

    """
    df = df_daily[[price_col]].copy()
    df["pct_returns"] = df[price_col].pct_change()
    df["vol36"] = df.pct_returns.ewm(span=36, adjust=False).std()
    df.drop(["pct_returns", price_col], axis=1, inplace=True)
    df.dropna(inplace=True)
    return df


def indicator_bollinger(df_t, lookback=20):
    """Creates columns for bollinger channel.  Requires columns "high" and "low" in intraday_df

    Args:
        df (pd.DataFrame): OHLCV intraday dataframe, only needs close
        lookback (:obj:int, optional): rolling window.  Default is 20

    Returns:
        pd.DataFrame: columns are:
            - bollinger_high
            - bollinger_low
    """
    df = df_t[["close"]].copy()
    df["bb_ma"] = df.close.rolling(window=lookback).mean()
    df["bb_std"] = df.close.rolling(window=lookback).std()
    df["bollinger_high"] = df.bb_ma + df.bb_std
    df["bollinger_low"] = df.bb_ma - df.bb_std
    df = df.drop(["close", "bb_ma", "bb_std"], axis=1)
    return df


def indicator_volbands(df_t, lookback=20, multiplier=0.3):
    """Create bands around a mean based on volatility

    Args:
        df_t (frame): requires "close" and "vol36" -- which is daily volatility
        lookback (`obj`:int, optional): lookback for moving average
        multiplier (`obj`:float, optional): multiplier for the daily volatility. 0.3 works well for about a 30T timeframe

    Returns:
        frame: vol_high and vol_low, which is the daily volatility above a moving average
    """
    df = df_t[["close", "vol36"]].copy()
    df["vol_ma"] = df.close.rolling(window=lookback).mean()
    df["vol_width"] = df.close * df.vol36 * multiplier
    df["vol_high"] = df.vol_ma + df.vol_width
    df["vol_low"] = df.vol_ma - df.vol_width
    return df[["vol_high", "vol_low"]]


def indicator_donchian(df, lookback=20):
    """Creates columns for donchian channel.  Requires columns "high" and "low" in intraday_df

    Args:
        df (pd.DataFrame): OHLCV intraday dataframe, only needs two columns:
            - high: used for hold-high
            - low: used for hold-low
        lookback (:obj:int, optional): rolling window.  Default is 20

    Returns:
        pd.DataFrame: columns are:
            - donchian_high
            - donchian_low

    Example:
        >>> df = processed_df.copy()
        >>> donchian = dvind.indicator_donchian(df, lookback=1380*3)
        >>> df = pd.merge(df, donchian, left_index=True, right_index=True)
    """
    df = df[["high", "low"]].copy()
    df = df.dropna()
    df["donchian_high"] = df.high.rolling(lookback).max()
    df["donchian_low"] = df.high.rolling(lookback).min()
    df = df.drop(["high", "low"], axis=1)
    return df


def indicator_atr(df, lookback=20):
    """Creates average true range

    Args:
        df (pd.DataFrame): OHLCV intraday dataframe, only needs high, low, close
        lookback (:obj:int, optional): rolling window.  Default is 20

    Returns:
        pd.DataFrame: columns with true_range and atr

    Example:
    """
    df = df[["high", "low", "close"]].copy()

    # true range
    df["highlow"] = abs(df["high"] - df["low"])
    df["highclose"] = abs(df["high"] - df["close"].shift(1))
    df["lowclose"] = abs(df["low"] - df["close"].shift(1))
    df["true_range"] = df[["highlow", "highclose", "lowclose"]].max(axis=1)

    # average
    df["atr"] = df["true_range"].rolling(lookback).mean()

    return df[["atr", "true_range"]]


def indicator_pp_daily(intraday_df):
    """Create a daily dataframe from EST data

    Args:
        intraday_df (pd.DataFrame): EST, left-indexed, i.e. starts at YYYY-MM-DD 18:00

    Returns:
        pd.DataFrame: index are pd.Timestamp of session-closing dates for the session pivot point,
            i.e. 2020-02-03 refers to 2020-02-02 18:00 to 2020-02-03 17:00

    Example:
        >>> ppframe_daily = indicator_pp_daily(df_all)
        >>> assert trading_gaps(ppframe_daily.index).empty
        >>> ppframe = set_index_to_intraday_start(ppframe_daily)
        >>> df_all[ppframe.columns] = ppframe
        >>> df_all[ppframe.columns] = df_all[ppframe.columns].fillna(method="ffill")
    """

    # Convert EST into session closing dates (no HH:MM)
    df = intraday_df.resample("24H", label="right", base=18).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )
    df.dropna(inplace=True)
    df.index = df.index.date

    # Add one day to the end before we shift
    start = intraday_df.index[0].strftime("%Y-%m-%d")
    end = intraday_df.index[-1].strftime("%Y-%m-%d")
    additional_day = tradingday_offset(
        start=start, end=end, dates=df.index[-1], offsets=1, roll="forward"
    )
    df.loc[additional_day] = np.nan

    # Convert to timestamp and shift
    df.index = pd.to_datetime(df.index)
    prev_day = df.shift(1)

    # Calculate pivot points use the previous day values
    pivot_df = pd.DataFrame()
    pivot_df["pp"] = (prev_day["high"] + prev_day["low"] + prev_day["close"]) / 3
    pivot_df["r1"] = 2 * pivot_df["pp"] - prev_day["low"]
    pivot_df["s1"] = 2 * pivot_df["pp"] - prev_day["high"]
    pivot_df["r2"] = pivot_df["pp"] + pivot_df["r1"] - pivot_df["s1"]
    pivot_df["s2"] = pivot_df["pp"] + pivot_df["s1"] - pivot_df["r1"]
    pivot_df["r3"] = pivot_df["pp"] - pivot_df["s2"] + pivot_df["r2"]
    pivot_df["s3"] = pivot_df["pp"] - pivot_df["r2"] + pivot_df["s2"]

    return pivot_df
