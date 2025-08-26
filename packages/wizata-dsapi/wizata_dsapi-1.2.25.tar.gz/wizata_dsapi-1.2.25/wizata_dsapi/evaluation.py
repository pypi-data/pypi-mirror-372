import json
import uuid
from .api_dto import ApiDto


class Evaluation(ApiDto):
    """
    an evaluation stores insights, such as properties and accuracy once a model training was executed.
    """

    @classmethod
    def route(cls):
        return "evaluations"

    @classmethod
    def from_dict(cls, data):
        obj = Evaluation()
        obj.from_json(data)
        return obj

    def __init__(self,
                 evaluation_id: uuid.UUID = None,
                 execution_id: int = None,
                 model_id: str = None,
                 properties: dict = None,
                 metrics: dict = None):
        if evaluation_id is None:
            self.evaluation_id = uuid.uuid4()
        else:
            self.evaluation_id = evaluation_id
        self.execution_id = execution_id
        self.model_id = model_id
        self.properties = properties
        self.metrics = metrics

        # related entities
        self.execution = None

    def api_id(self) -> str:
        return str(self.evaluation_id).upper()

    def endpoint(self) -> str:
        return "Evaluations"

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.evaluation_id)
        }
        if self.execution_id is not None:
            obj["executionId"] = int(self.execution_id)
        if self.model_id is not None:
            obj["modelId"] = str(self.model_id)
        if self.properties is not None:
            obj["properties"] = json.dumps(self.properties)
        if self.metrics is not None:
            obj["metrics"] = json.dumps(self.metrics)
        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.evaluation_id = uuid.UUID(obj["id"])
        if "executionId" in obj.keys() and obj["executionId"] is not None:
            self.execution_id = int(obj["executionId"])
        if "modelId" in obj.keys() and obj["modelId"] is not None:
            self.model_id = obj["modelId"]
        if "properties" in obj.keys() and obj["properties"] is not None:
            self.properties = json.loads(obj["properties"])
        if "metrics" in obj.keys() and obj["metrics"] is not None:
            self.metrics = json.loads(obj["metrics"])
