import numpy as np
import src.config as config
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.backtest import metrics


def plot_returns(history, price_data, cryptos_to_plot=['BTC'], show=True):
    """
    Plot the strategy returns vs. holding different cryptos.
    :param history: wallet worth history
    :param price_data: pd.DataFrame with index of exact time and columns of each crypto returns to plot
    """
    returns = metrics.pct_change(history)
    cum_returns = np.append(1, metrics.cumulative_returns(returns))

    dates = price_data['exact_time'].values
    price_data = price_data[[f'{crypto}{config.CURRENCY_TO_SELL}_Close' for crypto in cryptos_to_plot]]

    fig = make_subplots(rows=1)
    # Current strategy that is being tested
    fig.add_trace(
        go.Scatter(x=dates, y=cum_returns, name="Strategy"), row=1, col=1
    )

    # Holding different cryptos
    for tic in cryptos_to_plot:
        tic_price_data = price_data[f'{tic}{config.CURRENCY_TO_SELL}_Close']
        tic_returns = tic_price_data.pct_change().dropna().to_numpy()
        tic_cum_returns = np.append(1, metrics.cumulative_returns(tic_returns))
        fig.add_trace(
            go.Scatter(x=dates, y=tic_cum_returns, name=tic), row=1, col=1
        )

    # Horizontal line along ROI=1
    fig.add_shape(
        type="line", x0=dates[0], x1=dates[-1], y0=1, y1=1,
        line_width=2, line_dash="dot", line_color="grey"
    )

    if show:
        fig.show()

    else:
        return fig
