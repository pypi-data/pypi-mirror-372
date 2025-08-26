import wizata_dsapi

import pandas
import numpy

import sklearn
import sklearn.cluster
import sklearn.metrics
import sklearn.ensemble


def filter_df(context: wizata_dsapi.Context):
    """
    filter a dataframe
    :param context:
    :return:
    """

    if "filters" not in context.properties or not isinstance(context.properties['filters'], list):
        raise ValueError(f'there is no list *filters* in properties - please set them on context or config')

    df = context.dataframe.copy()

    filters = context.properties['filters']
    for filter_row in filters:
        try:
            df = df.query(filter_row)
        except pandas.errors.ParserError as e:
            raise ValueError(f"error parsing filter string '{filter_row}': {e}")

    return df


def clustering(context: wizata_dsapi.Context):
    """
    clustering
    :param context:
    :return:
    """
    df = context.dataframe.copy()
    scaler = sklearn.preprocessing.StandardScaler()
    df_clustering_scaler = scaler.fit_transform(df)

    range_n_clusters = list(range(2, min(10, df_clustering_scaler.shape[0])))
    silhouette_avg = []
    for num_clusters in range_n_clusters:
        kmeans = sklearn.cluster.KMeans(n_clusters=num_clusters)
        kmeans.fit(df_clustering_scaler)
        cluster_labels = kmeans.labels_
        unique, counts = numpy.unique(cluster_labels, return_counts=True)

        if len(unique) >= 2:
            silhouette_avg.append(sklearn.metrics.silhouette_score(df_clustering_scaler, cluster_labels))
        else:
            silhouette_avg.append(numpy.nan)

    if numpy.isnan(silhouette_avg).all():
        df['cluster_labels'] = 0
    else:
        best_nb_clusters = silhouette_avg.index(max(silhouette_avg)) + 2
        kmeans = sklearn.cluster.KMeans(n_clusters=best_nb_clusters)
        kmeans.fit(df_clustering_scaler)
        cluster_labels = kmeans.labels_
        df['cluster_labels'] = cluster_labels
        df['cluster_labels'] = df['cluster_labels'].apply(lambda x: int(x + 1))

    return df


def merge(context: wizata_dsapi.Context):
    """
    merge
    :param context:
    :return:
    """
    dataframes = context.current_dataframes()
    if len(dataframes) <= 1:
        raise ValueError(f'there is not enough dataframes to concat')

    how = "outer"
    if "how" in context.properties:
        how = context.properties["how"]

    df = None
    for key in dataframes:
        if df is None:
            df = dataframes[key]
        else:
            df = df.merge(dataframes[key], how=how, left_index=True, right_index=True)
    return df


def fillna(context: wizata_dsapi.Context):
    """
    fillna
    :param context:
    :return:
    """
    df = context.dataframe

    if "fillna" not in context.properties:
        raise KeyError(f'please set a property dict fillna')

    for key in context.properties["fillna"]:
        df[key] = df[key].fillna(value=context.properties["fillna"][key])

    return df


def target_feat_to_binary(context: wizata_dsapi.Context):
    """
    target_feat_to_binary
    :param context:
    :return:
    """
    df = context.dataframe

    if "target_feat" not in context.properties:
        raise KeyError(f'please set a target feature to transform to binary class')

    target_feat = context.properties["target_feat"]["sensor"]
    operator = context.properties["target_feat"]["operator"]
    threshold = context.properties["target_feat"]["threshold"]

    if operator == 'lt':
        df[target_feat] = numpy.where(df[target_feat] < threshold, 1, 0)
    elif operator == 'lte':
        df[target_feat] = numpy.where(df[target_feat] <= threshold, 1, 0)
    elif operator == 'gt':
        df[target_feat] = numpy.where(df[target_feat] > threshold, 1, 0)
    elif operator == 'gte':
        df[target_feat] = numpy.where(df[target_feat] >= threshold, 1, 0)
    else:
        raise KeyError(f'operator type for binarisation not know')

    # Check if at least 1 value of each class
    if df[target_feat].nunique() == 1:
        raise KeyError(f'classification model requires 2 classes, only one was detected')
    elif df[target_feat].nunique() > 2:
        raise KeyError(f'classification model requires 2 classes, more than 2 were detected')

    return df
