import json
import uuid
from .api_dto import ApiDto
from enum import Enum


def get_bool(obj, name: str):
    if isinstance(obj[name], str) and obj[name].lower() == "false":
        return False
    else:
        return bool(obj[name])


class MLModelConfig(ApiDto):
    """
    a model config defines execution properties within a pipeline.
    usually to define how a pipeline should train and predict with your model.

    :ivar bool by_twin: define if pipeline need to train and use different model by twin item.
    :ivar bool by_property: define if pipeline need to train and use different model based on 'property_name'.
    :ivar list features: datapoint list to refine columns if necessary.
    :ivar str function: name of the function used instead of 'predict' on model inference.
    :ivar str model_key: key of the model to store (or use story property if dynamic).
    :ivar str model_type: reserved for 'mlflow' defines model flavor such as 'sklearn' or 'pyfunc'.
    :ivar str model_alias: reserved for 'mlflow' set the alias to target and use inside a pipeline.
    :ivar dict properties_mapping: dict to map properties expected by the script with the properties from the context.
    :ivar str property_name: define which property is looked for when using 'by_property'.
    :ivar str source: define name of model storage to use 'wizata'.
    :ivar str|list target_feat: target feature name(s) to remove from df in 'predict' mode.
    :ivar str train_script: name of function referencing the script to train the model.
    :ivar float train_test_split_pct: percentage repartition to split the data for training and scoring.
    :ivar str train_test_split_type: type of splitting desired to split the train dataframe.
    :ivar bool output_append: true - default - append output to input dataframe. false to retrieve only 'predict' column(s).
    :ivar list output_columns_names: name list to rename columns inside output dataframe.
    :ivar str output_prefix: set a prefix to put before output column names (default or custom).
    """

    def __init__(self,
                 train_script=None,
                 train_test_split_pct: float = 1.0,
                 train_test_split_type: str = "ignore",
                 function: str = "predict",
                 properties_mapping=None,
                 target_feat=None,
                 output_append: bool = True,
                 output_columns_names: list = None,
                 output_prefix: str = None,
                 features: list = None,
                 model_key: str = None,
                 model_type: str = None,
                 model_alias: str = None,
                 by_twin: bool = False,
                 by_property: bool = False,
                 property_name: str = None,
                 source: str = "wizata"
                 ):

        # training
        self.train_script = train_script
        self.train_test_split_pct = train_test_split_pct
        self.train_test_split_type = train_test_split_type
        self.function = function
        self.properties_mapping = properties_mapping

        # features management
        self.target_feat = target_feat
        self.features = features
        self.output_columns_names = output_columns_names
        self.output_append = output_append
        self.output_prefix = output_prefix

        # key and identification
        self.model_key = model_key
        self.by_twin = by_twin
        self.by_property = by_property
        self.property_name = property_name

        # source
        self.source = source
        self.model_type = model_type
        self.model_alias = model_alias

    def from_json(self, obj):

        # Managed deprecated fields
        if "model_key_type" in obj.keys() and obj["model_key_type"] is not None:
            if obj["model_key_type"] == "template":
                self.by_twin = True
            elif obj["model_key_type"] == "variable":
                self.by_property = True
                if "model_key" not in obj.keys() or obj["model_key"] is None:
                    raise KeyError('model_key must be declared in the config.')
                self.property_name = obj["model_key"]

        # training info
        if "train_script" in obj.keys() and obj["train_script"] is not None:
            self.train_script = obj["train_script"]
        if "train_test_split_pct" in obj.keys() and obj["train_test_split_pct"] is not None:
            self.train_test_split_pct = float(obj["train_test_split_pct"])
        if "train_test_split_type" in obj.keys() and obj["train_test_split_type"] is not None:
            self.train_test_split_type = obj["train_test_split_type"]
        if "function" in obj.keys() and obj["function"] is not None:
            self.function = obj["function"]
        if "properties_mapping" in obj:
            self.properties_mapping = obj["properties_mapping"]

        # features info
        if "target_feat" in obj.keys() and obj["target_feat"] is not None:
            if isinstance(obj["target_feat"], str) or isinstance(obj["target_feat"], list):
                self.target_feat = obj["target_feat"]
            else:
                raise ValueError(f'target_feat should be a str or a list with columns name to remove.')

        if "features" in obj.keys() and obj["features"] is not None:
            self.features = obj["features"]

        # output management
        if "output_append" in obj.keys():
            self.output_append = get_bool(obj, name="output_append")

        if "output_prefix" in obj.keys() and obj["output_prefix"] is not None:
            self.output_prefix = obj["output_prefix"]
        if "output_columns_names" in obj.keys() and obj["output_columns_names"] is not None:
            if isinstance(obj["output_columns_names"], str):
                self.output_columns_names = [obj["output_columns_names"]]
            elif isinstance(obj["output_columns_names"], list):
                self.output_columns_names = obj["output_columns_names"]
            else:
                raise ValueError(f'output_property or output_columns_names should be a list or a string')
        elif "output_property" in obj.keys() and obj["output_property"] is not None \
                and obj["output_property"] != "result":
            if isinstance(obj["output_property"], str):
                self.output_columns_names = [obj["output_property"]]
            elif isinstance(obj["output_property"], list):
                self.output_columns_names = obj["output_property"]
            else:
                raise ValueError(f'output_property or output_columns_names should be a list or a string')

        # source
        if "source" in obj.keys() and obj["source"] is not None:
            self.source = obj["source"]
            if self.source not in ["wizata", "mlflow"]:
                raise ValueError("source must be wizata or mlflow")

        # key and target
        if "model_key" not in obj.keys() or obj["model_key"] is None:
            raise KeyError('model_key must be declared in the config.')
        self.model_key = obj["model_key"]
        if "by_twin" in obj.keys():
            self.by_twin = get_bool(obj, name="by_twin")
        if "by_property" in obj.keys():
            self.by_property = get_bool(obj, name="by_property")
        if "property_name" in obj.keys() and obj["property_name"] is not None:
            self.property_name = obj["property_name"]
        if "model_type" in obj.keys() and obj["model_type"] is not None:
            self.model_type = obj["model_type"]
        if "model_alias" in obj.keys() and obj["model_alias"] is not None:
            self.model_alias = obj["model_alias"]

    def to_json(self, target: str = None):
        obj = {
            "source": self.source
        }

        # training info
        if self.train_script is not None:
            obj["train_script"] = str(self.train_script)
        if self.train_test_split_pct is not None:
            obj["train_test_split_pct"] = float(self.train_test_split_pct)
        if self.train_test_split_type is not None:
            obj["train_test_split_type"] = str(self.train_test_split_type)
        if self.features is not None:
            obj["features"] = self.features
        if self.properties_mapping is not None and isinstance(self.properties_mapping, dict):
            obj["properties_mapping"] = self.properties_mapping

        # features info
        if self.target_feat is not None:
            obj["target_feat"] = self.target_feat
        if self.output_append is not None:
            obj["output_append"] = str(self.output_append)
        if self.output_columns_names is not None:
            obj["output_columns_names"] = self.output_columns_names
        if self.output_prefix is not None:
            obj["output_prefix"] = self.output_prefix
        if self.function is not None:
            obj["function"] = self.function

        # key and target
        if self.model_key is not None:
            obj["model_key"] = self.model_key
        if self.model_type is not None:
            obj["model_type"] = self.model_type
        if self.model_alias is not None:
            obj["model_alias"] = self.model_alias
        if self.by_twin is not None:
            obj["by_twin"] = str(self.by_twin)
        if self.by_property is not None:
            obj["by_property"] = str(self.by_property)
        if self.property_name is not None:
            obj["property_name"] = self.property_name

        return obj

    def has_target_feat(self) -> bool:
        """
        determine if configuration possess a target feature
        """
        if self.target_feat is None:
            return False

        if isinstance(self.target_feat, str):
            return True
        elif isinstance(self.target_feat, list):
            if len(self.target_feat) == 0:
                return False
            else:
                return True
        else:
            raise TypeError(f'unsupported target_feat type {self.target_feat.__class__.__name__}')


class MLModel(ApiDto):
    """
    used to define a stored machine learning model within Wizata.
    - deprecated -
    """

    @classmethod
    def route(cls):
        return "mlmodels"

    @classmethod
    def from_dict(cls, data):
        obj = MLModel()
        obj.from_json(data)
        return obj

    @classmethod
    def get_type(cls):
        return "pickle"

    def __init__(self,
                 model_id: str = None,
                 generated_by_id=None,
                 exact_names=True,
                 exact_numbers=True,
                 key=None):
        self.model_id = model_id
        self.key = key

        self.generatedById = generated_by_id

        self.status = 'draft'
        self.input_columns = []
        self.output_columns = []

        self.needExactColumnNumbers = exact_numbers
        self.needExactColumnNames = exact_names
        self.has_anomalies = False
        self.label_counts = 0
        self.has_target_feat = False

        self.trained_model = None
        self.scaler = None

        self.experimentId = None

    def api_id(self) -> str:
        return str(self.model_id).upper()

    def endpoint(self) -> str:
        return "MLModels"

    def to_json(self, target: str = None):
        obj = {"id": str(self.model_id),
               "status": str(self.status),
               "needExactColumnNames": str(self.needExactColumnNames),
               "needExactColumnNumbers": str(self.needExactColumnNumbers),
               "hasAnomalies": str(self.has_anomalies),
               "hasTargetFeat": str(self.has_target_feat),
               "labelCount": str(self.label_counts)
               }
        if self.key is not None:
            obj["key"] = str(self.key)
        if self.generatedById is not None:
            obj["generatedById"] = self.generatedById
        if self.input_columns is not None:
            obj["inputColumns"] = json.dumps(list(self.input_columns))
        if self.output_columns is not None:
            obj["outputColumns"] = json.dumps(list(self.output_columns))
        if self.experimentId is not None:
            obj["experimentId"] = str(self.experimentId)
        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.model_id = obj["id"]
        if "key" in obj.keys() and obj["key"] is not None:
            self.key = obj["key"]
        if "generatedById" in obj.keys() and obj["generatedById"] is not None:
            self.generatedById = int(obj["generatedById"])
        if "experimentId" in obj.keys() and obj["experimentId"] is not None:
            self.experimentId = uuid.UUID(obj["experimentId"])
        if "status" in obj.keys():
            self.status = str(obj["status"]).lower()
        if "inputColumns" in obj.keys():
            self.input_columns = json.loads(obj["inputColumns"])
        if "outputColumns" in obj.keys():
            self.output_columns = json.loads(obj["outputColumns"])
        if "labelCount" in obj.keys():
            self.label_counts = int(obj["labelCount"])
        if "hasAnomalies" in obj.keys():
            if isinstance(obj["hasAnomalies"], str) and obj["hasAnomalies"].lower() == "false":
                self.has_anomalies = False
            else:
                self.has_anomalies = bool(obj["hasAnomalies"])
        if "hasTargetFeat" in obj.keys():
            if isinstance(obj["hasTargetFeat"], str) and obj["hasTargetFeat"].lower() == "false":
                self.has_target_feat = False
            else:
                self.has_target_feat = bool(obj["hasTargetFeat"])
        if "needExactColumnNumbers" in obj.keys():
            if isinstance(obj["needExactColumnNumbers"], str) and obj["needExactColumnNumbers"].lower() == "false":
                self.needExactColumnNumbers = False
            else:
                self.needExactColumnNumbers = bool(obj["needExactColumnNumbers"])
        if "needExactColumnNames" in obj.keys():
            if isinstance(obj["needExactColumnNames"], str) and obj["needExactColumnNames"].lower() == "false":
                self.needExactColumnNames = False
            else:
                self.needExactColumnNames = bool(obj["needExactColumnNames"])

    def get_sample_payload(self):
        pl_columns = {"timestamp": "[timestamp]"}
        for hardwareId in self.input_columns:
            pl_columns[hardwareId] = "[" + hardwareId + "]"
        pl_json = {
            "id": str(self.model_id),
            "dataset": pl_columns
        }
        return pl_json
