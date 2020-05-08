#!/usr/bin/env python3
import unittest
from nose.tools import eq_
import pandas as pd
import os
import decisiveml as dml

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestTradingHolidays(unittest.TestCase):
    def setUp(self):
        self.short_holiday = pd.read_csv(
            os.path.join(
                TEST_DIR, "test_data/holidays/Holidays_Daily_2019-01-02_2020-02-20.csv"
            ),
            index_col="Date",
        )

        self.long_holiday = self.short_holiday

    def test_trading_holidays_in_range(self):
        """Test that we can remove our own holidays"""
        holidays = dml.trading_holidays_in_range(start="2018-12-01", end="2018-12-31")
        eq_(len(holidays), 2)
        eq_(holidays[0], "2018-12-25")
        eq_(holidays[1], "2019-01-01")
        eq_("2018-12-05" not in holidays, True)

    def test_trading_holidays_in_range_with_short_holiday(self):
        """Test using HOLIDAY data and fix missing dates in pandas_market_calendar"""
        df = self.short_holiday
        holidays = dml.trading_holidays_in_range(start=df.index[0], end=df.index[-1])
        eq_("2020-01-20" in holidays, True)
        eq_("2020-02-17" in holidays, True)

    def test_tradingday_offset_short(self):
        """Test that we can offset a business day through a holiday"""
        offsets = dml.tradingday_offset(
            start="2017-04-10",
            end="2017-04-20",
            dates=["2017-04-17"],
            offsets=-1,
            roll="backward",
        )
        eq_(offsets[0], pd.to_datetime("2017-04-13"))

    def test_tradingday_offset_long(self):
        """Test that we can offset a business day through a holiday"""
        offsets = dml.tradingday_offset(
            start="2017-01-01",
            end="2017-05-01",
            dates=["2017-01-01", "2017-04-17"],
            offsets=-1,
            roll="backward",
        )
        eq_(offsets[0], pd.to_datetime("2016-12-29"))
        eq_(offsets[1], pd.to_datetime("2017-04-13"))
