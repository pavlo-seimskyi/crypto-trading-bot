import numpy as np
import pandas as pd


def calculate_metrics(history, btc_price_data):
    output = {}
    returns = pct_change(history)
    btc_returns = btc_price_data.pct_change().dropna().to_numpy()

    output['return'] = cumulative_returns(returns)[-1]
    output['sharpe'] = sharpe_ratio(returns)
    output['sortino'] = sortino_ratio(returns)
    output['max_drawdown'] = max_drawdown(returns)
    output['btc_return'] = cumulative_returns(btc_returns)[-1]
    output['btc_sharpe'] = sharpe_ratio(btc_returns)

    return output


def pct_change(x):
    return np.diff(x, axis=0) / x[1:]


def cumulative_returns(returns):
    cumulative_returns = (returns + 1).cumprod(axis=0)
    return cumulative_returns


def sharpe_ratio(returns):
    cum_returns = cumulative_returns(returns)
    return (cum_returns[-1] - 1) / np.std(returns)


def sortino_ratio(returns):
    cum_returns = cumulative_returns(returns)
    return (cum_returns[-1] - 1) / np.std([ret for ret in returns if ret < 0])


def max_drawdown(returns):
    returns = pd.Series(returns)
    rolling_max = (returns + 1).cumprod().rolling(window=1440, min_periods=1).max()
    daily_value = (returns + 1).cumprod()
    return -(rolling_max - daily_value).max()


    # TODO research if this approach is better than the current one
    #     def sharpe_ratio(self, returns, N=60*24*365, risk_free_rate=0):
    #         mean = returns.mean() * N - risk_free_rate
    #         sigma = returns.std() * np.sqrt(N)
    #         return mean / sigma

    # TODO research if this approach is better than the current one
    #     def sortino_ratio(self, returns, N=60*24*365, risk_free_rate=0):
    #         mean = returns.mean() * N - risk_free_rate
    #         negative_std = returns[returns < 0].std() * np.sqrt(N)
    #         return mean / negative_std
