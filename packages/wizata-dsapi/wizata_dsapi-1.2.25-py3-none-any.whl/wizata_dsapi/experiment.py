import uuid
from .api_dto import ApiDto


class Experiment(ApiDto):
    """
    an experiment is a container to track all executions made with the same business objective and hypothesis.
    :ivar uuid.UUID experiment_id: technical id of the experiment.
    :ivar str description: description to help user understanding the experimentation.
    :ivar str key: logical string unique id of the experiment.
    :ivar str name: a simple name helping the user identifying the experiment.
    :ivar uuid.UUID template_id: link the experiment with a template.
    :ivar uuid.UUID twin_id: link the experiment with a digital twin item.
    :ivar uuid.UUID pipeline_id: link to pipeline used to generate this experiment.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "experiments"

    @classmethod
    def from_dict(cls, data):
        obj = Experiment()
        obj.from_json(data)
        return obj

    def __init__(self,
                 experiment_id=None,
                 key=None,
                 name=None,
                 description=None,
                 template_id=None,
                 twin_id=None,
                 pipeline_id=None):
        if experiment_id is None:
            self.experiment_id = uuid.uuid4()
        else:
            self.experiment_id = experiment_id
        self.key = key
        self.name = name
        self.description = description
        self.template_id = template_id
        self.twin_id = twin_id
        self.pipeline_id = pipeline_id
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        if value is not None and len(value) > 32:
            raise ValueError(f'key is limited to 32 char : {value} ')
        self._key = value

    @key.deleter
    def key(self):
        del self._key

    def api_id(self) -> str:
        return str(self.experiment_id).upper()

    def endpoint(self) -> str:
        return "Experiments"

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.experiment_id)
        }
        if self.key is not None:
            obj["key"] = str(self.key)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.description is not None:
            obj["description"] = str(self.description)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)
        if self.pipeline_id is not None:
            obj["pipelineId"] = str(self.pipeline_id)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.experiment_id = uuid.UUID(obj["id"])
        if "key" in obj.keys() and obj["key"] is not None:
            self.key = obj["key"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "description" in obj.keys() and obj["description"] is not None:
            self.description = obj["description"]
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = obj["templateId"]
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = obj["twinId"]
        if "pipelineId" in obj.keys() and obj["pipelineId"] is not None:
            self.pipeline_id = obj["pipelineId"]
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

