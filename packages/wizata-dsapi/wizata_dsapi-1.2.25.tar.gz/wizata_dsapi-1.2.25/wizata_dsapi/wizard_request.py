import uuid
import json
from .request import Request


class WizardRequest:
    """
    represents a wizard request to generate automatically a pipeline through an experimentation.
    :ivar uuid.UUID execution_id: execution id at origin of this request.
    :ivar str name: name of the request.
    :ivar bool is_anomaly_detection: true if request concerns an anomaly detection.
    :ivar str function: name of the function.
    :ivar dict properties: dictionary of properties defining the request.
    """

    def __init__(self,
                 execution_id: uuid.UUID = None,
                 name: str = None,
                 request: Request = None,
                 properties: dict = None
                 ):
        if execution_id is None:
            execution_id = uuid.uuid4()
        self.execution_id = execution_id
        self.name = name
        self.request = request
        self.is_anomaly_detection = False
        self.function = None
        self.properties = properties

    def to_json(self):
        obj = {
            "id": str(self.execution_id),
            "name": str(self.name)
        }
        if self.request is not None:
            obj["request"] = json.dumps(self.request.to_json())

        if self.function is not None:
            obj["function"] = self.function
        if self.is_anomaly_detection:
            obj["isAnomalyDetection"] = True
        else:
            obj["isAnomalyDetection"] = False
        if self.properties is not None:
            obj["properties"] = json.dumps(self.properties)
        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.execution_id = uuid.UUID(obj["id"])
        if "name" in obj.keys():
            self.name = obj["name"]
        else:
            raise ValueError("please set a name on the request")
        if "request" in obj.keys() and obj["request"] is not None:
            self.request = Request()
            if isinstance(obj["request"], str):
                self.request.from_json(json.loads(obj["request"]))
                self.copy_properties(json.loads(obj["request"]))
            else:
                self.request.from_json(obj["request"])
                self.copy_properties(obj["request"])
        if "properties" in obj.keys() and obj["properties"] is not None:
            if isinstance(obj["properties"], str):
                self.add_properties(json.loads(obj["properties"]))
            else:
                self.add_properties(obj["properties"])

        if "function" in obj.keys() and obj["function"] is not None:
            self.function = obj["function"]
        if "isAnomalyDetection" in obj.keys() and obj["isAnomalyDetection"] is not None:
            if isinstance(obj["isAnomalyDetection"], bool):
                self.is_anomaly_detection = obj["isAnomalyDetection"]
            else:
                self.is_anomaly_detection = obj["isAnomalyDetection"] == 'True'

    def copy_properties(self, obj: dict):
        """
        copy all properties from a dict to another.
        :param dict obj: new dict
        """
        keys = [
            'target_feat',
            'sensitivity',
            'aggregations',
            'restart_filter',
            'interval'
        ]
        for key in keys:
            if key in obj:
                if self.properties is None:
                    self.properties = {}
                self.properties[key] = obj[key]

    def add_properties(self, obj: dict):
        """
        add all properties from a dict to current properties.
        :param dict obj: properties to add.
        """
        for key in obj.keys():
            if self.properties is None:
                self.properties = {}
            self.properties[key] = obj[key]
