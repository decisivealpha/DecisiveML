import pandas as pd
import random
import statistics
import logging

logger = logging.getLogger(__name__)

# MonkeyPatch Python 3.6 choices into random 3.5.5
import bisect as _bisect
import itertools as _itertools


def choices(population, weights=None, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with
replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    if cum_weights is None:
        if weights is None:
            total = len(population)
            return [population[int(random.random() * total)] for i in range(k)]
        cum_weights = list(_itertools.accumulate(weights))
    elif weights is not None:
        raise TypeError("Cannot specify both weights and cumulative weights")
    if len(cum_weights) != len(population):
        raise ValueError("The number of weights does not match the population")
    bisect = _bisect.bisect
    total = cum_weights[-1]
    hi = len(cum_weights) - 1
    return [population[bisect(cum_weights, random() * total, 0, hi)] for i in range(k)]


random.choices = choices


class ExcessiveBaseEquity(Exception):
    pass


class MonteCarlo(object):
    def __init__(self, trades_list):
        self.trades_list = trades_list
        self.num_trades_total = len(self.trades_list)
        self.num_trades_per_year = None
        self.ruin_equity = None
        self.runs = None

        self._MONTECARLO_RUNS = 2500
        logger.info(
            "Initialize \t| Trades: {} \t| MC Runs: {}".format(
                self.num_trades_total, self._MONTECARLO_RUNS
            )
        )

    def settings(self, ruin_equity, start_date, end_date):
        self._set_ruin_equity(ruin_equity)
        self._set_trades_per_year(start_date, end_date)
        logger.info(
            "Settings \t| Ruin: {} \t| Trades Per Year: {}".format(
                self.ruin_equity, self.num_trades_per_year
            )
        )

    def _set_ruin_equity(self, ruin_equity):
        self.ruin_equity = ruin_equity

    def _set_trades_per_year(self, start_date, end_date):
        td = end_date - start_date
        self.num_trades_per_year = int(self.num_trades_total * 365 / td.days)
        logger.debug("TimeDelta: {} {} trades/yr".format(td, self.num_trades_per_year))

    def _random_trade(self, starting_equity):
        assert self.num_trades_per_year
        assert self.ruin_equity

        trades = random.choices(self.trades_list, k=self.num_trades_per_year)
        # logger.debug("{} {}".format(len(trades), trades))

        # Check for ruin at any point in the trades list
        is_ruined = 0
        equity = starting_equity
        for trade in trades:
            equity = equity + trade
            if equity < self.ruin_equity:
                is_ruined = 1
                break

        stats = {
            "profit": sum(trades),
            "returns_pct": int(
                100 * ((starting_equity + sum(trades)) / starting_equity - 1)
            ),
            "drawdown_pct": self._drawdown(starting_equity, trades),
            "is_ruined": is_ruined,
            "is_profitable": 1 if sum(trades) >= 0 else 0,
        }
        try:
            stats["returns_per_drawdown"] = stats["returns_pct"] / stats["drawdown_pct"]
        except ZeroDivisionError:
            stats["returns_per_drawdown"] = 0
        logger.debug(stats)
        return stats

    def _drawdown(self, starting_equity, trades):
        """Returns the maximum drawdown in a set of trades"""
        equity = starting_equity
        hwm = starting_equity
        max_drawdown_pct = 0
        drawdown_pct = 0

        for trade in trades:
            equity = equity + trade

            # Set High Water Mark
            if equity > hwm:
                hwm = equity

            # Look for drawdown
            if equity < hwm:
                drawdown_pct = 100 * (1 - (equity / hwm))
                if drawdown_pct > max_drawdown_pct:
                    max_drawdown_pct = drawdown_pct

            # logger.debug("{} eq:{} \t hwm:{} \t dd:{} mdd:{}".format(trade, equity, hwm, drawdown_pct, max_drawdown_pct))
        return max_drawdown_pct

    def _median_stats_run(self, starting_equity):
        montecarlo = {}
        median_montecarlo = {}

        # runs
        for _ in range(self._MONTECARLO_RUNS):

            # make the list for every key
            stats = self._random_trade(starting_equity)
            for k, v in stats.items():
                if k not in montecarlo.keys():
                    montecarlo[k] = []
                montecarlo[k].append(v)

        # run statistics on all the lists of every key
        for k, v in montecarlo.items():
            # ignore non-median stats
            if k != "is_ruined" or k != "is_profitable":
                median_montecarlo[k] = statistics.median(montecarlo[k])

        logger.debug((montecarlo["profit"]))
        logger.debug((montecarlo["is_ruined"]))
        logger.debug(sum(montecarlo["is_ruined"]))
        median_montecarlo["is_ruined"] = (
            100 * sum(montecarlo["is_ruined"]) / self._MONTECARLO_RUNS
        )
        median_montecarlo["is_profitable"] = (
            100 * sum(montecarlo["is_profitable"]) / self._MONTECARLO_RUNS
        )
        median_montecarlo["equity"] = starting_equity

        # calculate risk of ruin
        logger.debug("Median {}: {}".format(starting_equity, median_montecarlo))

        return median_montecarlo

    def run(self, base_equity, steps=11):
        """Create the results for the MonteCarlo, adding equity to the
        base_equity

        Args:
            base_equity (int): starting equity to add to
            steps (:obj:`int`, optional). Default is 11 runs.

        Returns:
            pd.DataFrame: results for each run with various starting equities

        Example:
            >>> mc = dvm.MonteCarlo(trade_list)
            >>> start_date = trade_list.index[0].to_pydatetime()
            >>> end_date = trade_list.index[-1].to_pydatetime()
            >>> mc.settings(ruin_equity=5000, start_date=start_date, end_date=end_date)
            >>> results = mc.run(base_equity=starting_equity)

        """
        step_size = int(base_equity / 4)
        end_eq = base_equity + step_size * steps
        starting_equities_list = range(base_equity, end_eq, step_size)
        results = self._run_equity_list(starting_equities_list)
        df = pd.DataFrame(results)
        return df

    def _run_equity_list(self, starting_equities_list):
        runs = []
        for starting_equity in starting_equities_list:
            runs.append(self._median_stats_run(starting_equity))
        self.runs = runs
        return runs

    def best_run(self, target_risk_of_ruin_pct=10):
        assert self.runs
        for run in self.runs:
            if run["is_ruined"] < target_risk_of_ruin_pct:
                return run
        return None

    def recommendation(self, start_date, end_date):
        """Create a recommendation from the best run

        Args:
            start_date (datetime): trade start date
            end_date (datetime): trade end date

        Returns:
            pd.Series: recommendation categories

        Example:
            >>> mc = dvm.MonteCarlo(trade_list)
            >>> start_date = trade_list.index[0].to_pydatetime()
            >>> end_date = trade_list.index[-1].to_pydatetime()
            >>> mc.settings(ruin_equity=5000, start_date=start_date, end_date=end_date)
            >>> results = mc.run(base_equity=starting_equity)
            >>> my_rec = mc.recommendation(start_date, end_date)
        """

        # Get the recommended values
        best = self.best_run()
        my_rec = pd.Series(best)

        if my_rec.empty:
            raise ExcessiveBaseEquity(f"No best run found")

        # Determine result
        if my_rec["is_ruined"] > 10 or my_rec["returns_per_drawdown"] < 2.0:
            logger.info("MonteCarlo Risk Assessment: FAILED")
            my_rec["is_pass"] = False
        else:
            logger.info("MonteCarlo Risk Assessment: PASSED")
            my_rec["is_pass"] = True

        # Add additional calculations
        my_rec["start_date"] = start_date
        my_rec["end_date"] = end_date
        my_rec["months"] = (end_date - start_date).days / 30
        my_rec["avg_monthly_profit"] = my_rec["profit"] / my_rec["months"]

        return my_rec
