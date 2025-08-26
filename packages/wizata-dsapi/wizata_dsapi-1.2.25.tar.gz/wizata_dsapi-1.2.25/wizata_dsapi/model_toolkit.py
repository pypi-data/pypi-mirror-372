import pandas
from .mlmodel import MLModel


def predict(df: pandas.DataFrame, ml_model: MLModel, mapping_table=None):
    """
    Execute a Machine Learning models locally.
    :param df: dataframe to use as input.
    :param ml_model: trained machine learning model.
    :param mapping_table: Optional mapping table.
    :return: output dataframe with predicted values.
    """
    if ml_model is None or ml_model.trained_model is None or ml_model.input_columns is None:
        raise ValueError("Please download your model from DS API before using it.")
    old_index = df.index
    df.index = pandas.to_datetime(df.index)
    df_result = pandas.DataFrame(index=df.index)
    features = ml_model.input_columns
    if ml_model.has_target_feat is True:
        df_result['result'] = ml_model.trained_model.detect(df[features]).astype(float)
    else:
        df_result['result'] = ml_model.trained_model.predict(df[features]).astype(float)
    if ml_model.label_counts != 0:
        df_result[__generate_label_columns(ml_model.label_counts)] = \
            ml_model.trained_model.predict_proba(df[features]).astype(float)
    df_result = df_result.set_index(old_index)
    return df_result


def __generate_label_columns(label_count):
    """
    Generate a list of columns based on number of desired labels.
    :param label_count: Number of desired labels.
    :return: list of labels generated.
    """
    i = 0
    columns = []
    while i < label_count:
        columns.append("prob_" + str(i) + "_label")
        i = i + 1
    return columns
