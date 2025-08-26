import wizata_dsapi

import pandas
import numpy

import sklearn
import sklearn.linear_model
import sklearn.ensemble


def extract_target_feat(context: wizata_dsapi.Context, single: bool = True):
    """
    return a list of target_feat columns names if not single value or the single value target feat name
    raise an error if configuration mismatch
    """

    if "target_feat" not in context.properties:
        raise ValueError(f"training script requires a proper target_feat")

    target_feat = context.properties["target_feat"]
    if isinstance(target_feat, str):
        if single:
            return target_feat
        else:
            return [target_feat]
    elif isinstance(target_feat, list):
        if single:
            if len(target_feat) == 1:
                return target_feat[0]
            else:
                raise ValueError(f"expecting only one target_feat but found {len(target_feat)}")
        else:
            return [target_feat]
    else:
        raise TypeError(f'target_feat must be a str or a list of str but found {target_feat.__class__.__name__}')


def linear_regression(context: wizata_dsapi.Context):
    """
    generic linear regression
    - expects a valid single value target_feat
    """
    df = context.dataframe

    model_config = context.get_model_config()
    if not model_config.has_target_feat():
        raise ValueError(f'linear_regression requires a target feat')
    target_feat_name = context.properties["target_feat"]

    x = df.drop(columns=[target_feat_name])
    y = df[target_feat_name]

    model = sklearn.linear_model.LinearRegression()
    model.fit(x, y)

    context.set_model(model, x.columns)


def logistic_regression(context: wizata_dsapi.Context):
    """
    generic linear regression
    - expects a valid single value target_feat
    """
    df = context.dataframe

    model_config = context.get_model_config()
    if not model_config.has_target_feat():
        raise ValueError(f'logistic_regression requires a target feat')
    target_feat_name = context.properties["target_feat"]

    x = df.drop(columns=[target_feat_name])
    y = df[target_feat_name]

    model = sklearn.linear_model.LogisticRegression()
    model.fit(x, y.astype(int))

    context.set_model(model, x.columns)


def isolation_forest(context: wizata_dsapi.Context):
    """
    isolation forest anomaly detection
    - expects a no target feat model step
    """

    model_config = context.get_model_config()
    if model_config.has_target_feat():
        raise ValueError(f'isolation_forest does not requires a target feat')

    try:
        if context.properties['sensitivity'] is None:
            raise KeyError("sensitivity is none")
        sensitivity = int(context.properties['sensitivity'])
        sensitivities = [0.05, 0.15, 0.25, 0.35, 0.4]
        contamination = sensitivities[sensitivity - 1]
    except Exception as e:
        raise ValueError(f'cannot extract sensitivity integer from 0 to 4 due to {e}')

    df = context.dataframe.copy()
    model = sklearn.ensemble.IsolationForest(contamination=contamination)
    df['isolation_forest_predict'] = model.fit_predict(df)
    context.set_model(model, df.columns)
    return df


def gradiant_boost_classifier(context: wizata_dsapi.Context):
    """
    gradiant_boost_classifier
    :param context:
    :return:
    """
    df = context.dataframe

    model_config = context.get_model_config()
    if not model_config.has_target_feat():
        raise ValueError(f'gradiant_boost_classifier requires a target feat')
    target_feat_name = context.properties["target_feat"]

    x = df.drop(columns=[target_feat_name])
    y = df[target_feat_name]

    model = sklearn.ensemble.GradientBoostingClassifier(random_state=0).fit(x, y)
    context.set_model(model, df.columns)






