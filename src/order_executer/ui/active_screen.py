import json
import math

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_metrics(executer_service):
    """
    Plots the different feature generators grouped by their type
    :param executer_service:
    :return:
    """
    metrics = feature_service_to_dataframe(executer_service)
    metrics_to_plot = [metric  for metric in metrics.columns if metric != "timestamp"]

    # Getting the metric type so that we can gather all of them in the same graph
    metrics_to_plot_pairs = [(metric.split("_")[0], metric) for metric in metrics_to_plot]
    metrics_types = np.unique([pairs[0] for pairs in metrics_to_plot_pairs])
    fig = make_subplots(rows=len(metrics_types), cols=1)

    index_with_type = enumerate(metrics_types, start=1)
    index_map = {k:v for v,k in index_with_type}

    for type, metric in metrics_to_plot_pairs:

        fig.append_trace(go.Scatter(
            x=metrics.timestamp,
            y=metrics[metric],
            name=metric
        ), row=index_map[type], col=1)

    fig.update_layout(template="plotly_dark", title="Metrics", height=len(metrics_types) * 500)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def feature_service_to_dataframe(executer_service):
    features_data = executer_service.feature_service.all_data
    min_len = math.inf
    # Getting the smallest length of a metric since they have different compute windows
    for array_measures in features_data.values():
        if len(array_measures) < min_len:
            min_len = len(array_measures)
    # Trimming the features to the smallest one
    features_data = {k: v[-min_len:] for k, v in features_data.items()}
    metrics = pd.DataFrame(features_data)
    return metrics
