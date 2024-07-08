import os
import re
import pandas as pd
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
from qstrader.asset.equity import Equity
from qstrader.asset.universe.static import StaticUniverse
from qstrader.data.backtest_data_handler import BacktestDataHandler
from qstrader.data.daily_bar_csv import CSVDailyBarDataSource
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.trading.backtest import BacktestTradingSession
from qstrader.data.yfloader import Yfloader
from qstrader.utils.helper import normalize_value

if __name__ == "__main__":
    # start_date = "2023-10-31"
    start_date = "2023-5-30"
    start_date = "2024-6-22"
    end_date = "2024-11-30"

    market_selection = "US" # "TW"
    benchmark_ticker = "SPY"

    # M7
    # strategy_symbols_allocation = {'EQ:SPY': 1.0}
    strategy_symbols_allocation = {
        "EQ:AAPU": 5,
        "EQ:TQQQ": 1.5,
        # "EQ:GGLL": 1.1,
        "EQ:AMZU": 1.55,
        "EQ:MSFU": 1.12,
        "EQ:FBL": 1.47,
    }

    # high volatile
    strategy_symbols_allocation = {
        "EQ:NVDL": 10,
        "EQ:AMDL": 2,
        "EQ:ANET": 1.4,
    }

    # TW market -- verified
    if market_selection == "TW":
        benchmark_ticker = "2330.TW"
        strategy_symbols_allocation = {"EQ:2330.TW": 1.0}
        # comparable performance and reduced draw-down.
        strategy_symbols_allocation = {"EQ:00713.TW": 1.0, "EQ:00631L.TW": 0.5}

    strategy_symbols = [k.replace("EQ:", "") for k in strategy_symbols_allocation] + [
        benchmark_ticker
    ]
    strategy_title = str(strategy_symbols_allocation)

    # normalize allocation
    strategy_symbols_allocation = normalize_value(strategy_symbols_allocation)

    start_dt = pd.Timestamp(f"{start_date} 14:30:00", tz=pytz.UTC)
    end_dt = pd.Timestamp(f"{end_date} 23:59:00", tz=pytz.UTC)
    # Construct the symbols and assets necessary for the backtest
    Yfloader().load_as_csv(start_dt, end_dt, strategy_symbols)
    strategy_assets = ["EQ:%s" % symbol for symbol in strategy_symbols]
    strategy_universe = StaticUniverse(strategy_assets)

    # To avoid loading all CSV files in the directory, set the
    # data source to load only those provided symbols
    csv_dir = os.environ.get("QSTRADER_CSV_DATA_DIR", ".")
    data_source = CSVDailyBarDataSource(csv_dir, Equity, csv_symbols=strategy_symbols)
    data_handler = BacktestDataHandler(strategy_universe, data_sources=[data_source])

    # Construct an Alpha Model that simply provides
    # static allocations to a universe of assets
    # In this case 60% SPY ETF, 40% AGG ETF,
    # rebalanced at the end of each month
    strategy_alpha_model = FixedSignalsAlphaModel(strategy_symbols_allocation)
    strategy_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        strategy_universe,
        strategy_alpha_model,
        rebalance="end_of_month",
        long_only=True,
        cash_buffer_percentage=0.01,
        data_handler=data_handler,
    )
    strategy_backtest.run()

    # Construct benchmark assets (buy & hold SPY)
    # benchmark_ticker = "SPY"
    benchmark_assets = [f"EQ:{benchmark_ticker}"]
    benchmark_universe = StaticUniverse(benchmark_assets)

    # Construct a benchmark Alpha Model that provides
    # 100% static allocation to the SPY ETF, with no rebalance
    benchmark_alpha_model = FixedSignalsAlphaModel({f"EQ:{benchmark_ticker}": 1.0})
    benchmark_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        benchmark_universe,
        benchmark_alpha_model,
        rebalance="buy_and_hold",
        long_only=True,
        cash_buffer_percentage=0.01,
        data_handler=data_handler,
    )
    benchmark_backtest.run()

    # Performance Output
    tearsheet = TearsheetStatistics(
        strategy_equity=strategy_backtest.get_equity_curve(),
        benchmark_equity=benchmark_backtest.get_equity_curve(),
        title=strategy_title,
    )
    export_name = (
        re.sub(r"[\{,\},EQ:,\']", "", strategy_title)
        .replace(".TW", "")
        .replace(" ", "-")
        + ".pdf"
    )
    tearsheet.plot_results(export_name)
