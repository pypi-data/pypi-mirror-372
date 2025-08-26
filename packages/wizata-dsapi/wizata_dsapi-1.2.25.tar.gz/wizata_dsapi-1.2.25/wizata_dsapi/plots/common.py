import pandas
import wizata_dsapi
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sklearn.metrics


def check_single_column_and_target_feat(context: wizata_dsapi.Context):
    """
    check_single_column_and_target_feat
    :param context:
    :return:
    """
    input_io = context.step.get_unique_input()
    if input_io.dataframe not in context.dataframes or input_io.dataframe + '.reference' not in context.dataframes:
        raise ValueError(f'impossible to find {input_io.dataframe} dataframe and reference inside the context ')

    predict_df = context.dataframes[input_io.dataframe]
    ref_df = context.dataframes[input_io.dataframe + ".reference"]
    if ref_df.ndim != 1:
        raise ValueError('please use a model that predict only one serie/dimension.')

    if "output_columns_names" not in context.properties:
        raise RuntimeError('there is no output columns in properties, r squared cannot find results')

    column_name = context.properties["output_columns_names"]
    if not isinstance(column_name, str):
        if isinstance(column_name, list) and len(column_name) == 1:
            column_name = column_name[0]
        elif isinstance(column_name, list):
            raise ValueError('please use a model that predict only one serie/dimension - mulitple column names')
        else:
            raise TypeError(f'column_name is not a str or a list {column_name.__class__.__name__}')

    if not isinstance(predict_df, pandas.DataFrame):
        raise TypeError(f'predicted dataframe is not a dataframe {predict_df.__class__.__name__}')
    predict_df = predict_df.copy()
    predict_df = predict_df[[column_name]]

    if isinstance(ref_df, pandas.Series):
        ref_df = pandas.DataFrame(ref_df, index=predict_df.index)
    return predict_df, ref_df


def confusion_matrix(context: wizata_dsapi.Context):
    """
    confusion_matrix
    :param context:
    :return:
    """
    predict_df, ref_df = check_single_column_and_target_feat(context)
    cm = sklearn.metrics.confusion_matrix(ref_df, predict_df)
    inverted_cm = np.flip(cm, axis=1)

    fig = go.Figure(data=go.Heatmap(
        z=inverted_cm,
        x=['Positive', 'Negative'],
        y=['Negative', 'Positive'],
        colorscale='RdBu',
        colorbar=dict(title='Count')
    ))

    for i in range(len(inverted_cm)):
        for j in range(len(inverted_cm[i])):
            fig.add_annotation(
                x=j,
                y=i,
                text=str(inverted_cm[i][j]),
                showarrow=False,
                font=dict(color='black' if inverted_cm[i][j] < np.max(inverted_cm) / 2 else 'white')
            )

    fig.update_layout(
        xaxis=dict(title='Predicted'),
        yaxis=dict(title='Actual')
    )

    context.set_plot(
        figure=fig,
        name="confusion_matrix"
    )


def r_squared(context: wizata_dsapi.Context):
    """
    In statistics, the coefficient of determination, denoted R2 or r2 and pronounced "R squared", is the proportion of
    the variation in the dependent variable that is predictable from the independent variable(s).
    """
    predict_df, ref_df = check_single_column_and_target_feat(context)

    r_squared = sklearn.metrics.r2_score(ref_df, predict_df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ref_df.values.flatten(), y=predict_df.values.flatten(),
                             mode='markers', name='Data Points'))

    min_value = min(ref_df.values.min(), predict_df.values.min())
    max_value = max(ref_df.values.max(), predict_df.values.max())
    fig.add_trace(go.Scatter(x=[min_value, max_value], y=[min_value, max_value],
                             mode='lines', line=dict(color='black', dash='dash'), showlegend=False))

    fig.add_annotation(
        x=min_value,
        y=max_value,
        text=f'R^2 = {r_squared:.4f}',
        showarrow=False,
        font=dict(color='black', size=12),
        bgcolor='lightgrey',
        bordercolor='black',
        borderwidth=1,
        borderpad=4,
        opacity=0.8
    )

    fig.update_layout(
        xaxis=dict(title='Actual'),
        yaxis=dict(title='Predicted')
    )

    context.set_plot(
        figure=fig,
        name="r_squared"
    )


def ts_chart(context: wizata_dsapi.Context):
    """
    ts_chart
    :param context:
    :return:
    """
    df = context.dataframe
    traces = []
    for column in df.columns:
        trace = go.Scatter(x=df.index, y=df[column], mode='lines', name=column)
        traces.append(trace)

    fig = go.Figure(traces)
    context.set_plot(
        figure=fig,
        name="ts_chart"
    )


def anomalies_chart(context: wizata_dsapi.Context):
    """
    anomalies_chart
    :param context:
    :return:
    """
    df = context.dataframe

    # Add Signals
    traces = []
    for column in df.columns:
        if column != "anomalies_type":
            trace = go.Scatter(x=df.index, y=df[column], mode='lines', name=column)
            traces.append(trace)
    fig = go.Figure(traces)

    # Add Anomalies as Highlighted
    anomalies_list = context.dataframe.copy()
    anomalies_list['anomaly'] = np.where(anomalies_list['anomalies_type'] != 0, 1, 0)
    anomalies_list['new_occurrence'] = np.where(
        (anomalies_list['anomaly'] != anomalies_list['anomaly'].shift(1)) |
        (anomalies_list['anomalies_type'] != anomalies_list['anomalies_type'].shift(1)), 1, 0)
    anomalies_list['new_occurrence_index'] = anomalies_list['new_occurrence'].cumsum()
    anomalies_occurrences = anomalies_list[anomalies_list['anomaly'] != 0].reset_index(). \
        groupby(['new_occurrence_index']). \
        agg({'Timestamp': ['first', 'last'], 'anomalies_type': 'first'})
    anomalies_occurrences.columns = ['from', 'to', 'anomaly_group']
    for i in anomalies_occurrences.index:
        fig.add_vrect(x0=anomalies_occurrences['from'][i], x1=anomalies_occurrences['to'][i], line_width=0,
                      fillcolor="red", opacity=0.2)

    context.set_plot(
        figure=fig,
        name="anomalies_chart"
    )


def parallel_coordinates(context: wizata_dsapi.Context):
    """
    parallel_coordinates
    :param context:
    :return:
    """
    df = context.dataframe

    fig = px.parallel_coordinates(df,
                                  color='anomalies_type',
                                  dimensions=df,
                                  color_continuous_scale=px.colors.diverging.Portland)
    context.set_plot(
        figure=fig,
        name="parallel_coordinates"
    )

