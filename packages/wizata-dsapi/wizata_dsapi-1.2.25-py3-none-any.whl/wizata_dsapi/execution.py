import json
import uuid
from enum import Enum

from .api_dto import ApiDto
from .pipeline import Pipeline
from .experiment import Experiment


class AbortedException(Exception):
    """
    exception to trigger within a custom script to 'abort' a pipeline instead of failing it.
    """
    pass


class ExecutionStatus(Enum):
    """
    ExecutionStatus defines different status possible for an execution.
        - "received" default status when execution is created initially.
        - "queued" execution have been put in the queue.
        - "started" a runner have started processing the execution.
        - "completed" execution finished processing as expected.
        - "failed" execution finished with errors.
        - "aborted" execution was cancelled from expected or manual conditions.
        - "abortrequested" set on an execution queued to force its abortion as soon as a runner start processing it.
    """
    RECEIVED = "received"
    QUEUED = "queued"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ABORT_REQUESTED = "abortrequested"


class ExecutionStepLog(ApiDto):
    """
    execution Step Log defines result of a specific step processing (only for execution in experiment mode).
    :ivar uuid.UUID execution_step_log_id: technical id of an execution step log.
    :ivar str content: str representing result of this execution.
    :ivar uuid.UUID execution_id: parent execution id.
    :ivar wizata_dsapi.ExecutionStatus status: status of this execution step log.
    :ivar uuid.UUID step_id: technical id of the pipeline step.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    def __init__(self, execution_step_log_id=None, step_id=None, execution_id=None, content=None, status=None):
        if execution_step_log_id is None:
            execution_step_log_id = uuid.uuid4()
        self.execution_step_log_id = execution_step_log_id
        self.execution_id = execution_id
        self.step_id = step_id
        self.content = content
        self.status = status
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        formatted id of the expected_step_log (execution_step_log_id)
        :return: string formatted UUID of the ExecutionStepLog.
        """
        return str(self.execution_step_log_id).upper()

    def endpoint(self) -> str:
        """
        endpoint name used to manipulate execution step log on backend.
        :return: endpoint name.
        """
        return "ExecutionStepLogs"

    def to_json(self, target: str = None):
        """
        convert the execution step log to a dictionary compatible with JSON format.
        :return: dictionary representation of the execution step log object.
        """
        obj = {
            "id": str(self.execution_step_log_id)
        }
        if self.execution_id is not None:
            obj["executionId"] = self.execution_id
        if self.step_id is not None:
            obj["stepId"] = str(self.step_id)
        if self.content is not None:
            obj["content"] = json.dumps(self.content)
        if self.createdById is not None:
            obj["createdById"] = self.createdById
        if self.createdDate is not None:
            obj["createdDate"] = self.createdDate
        if self.updatedById is not None:
            obj["updatedById"] = self.updatedById
        if self.updatedDate is not None:
            obj["updatedDate"] = self.updatedDate
        if self.status is not None and isinstance(self.status, ExecutionStatus):
            obj["status"] = self.status.value
        return obj

    def from_json(self, obj):
        """
        load the execution step log entity from a dictionary.
        :param obj: dict version of the datapoint.
        """
        if "id" in obj.keys():
            self.execution_step_log_id = uuid.UUID(obj["id"])
        if "executionId" in obj.keys() and obj["executionId"] is not None:
            self.execution_id = int(obj["executionId"])
        if "stepId" in obj.keys() and obj["stepId"] is not None:
            self.step_id = uuid.UUID(obj["stepId"])
        if "content" in obj.keys() and obj["content"] is not None:
            if isinstance(obj["content"], str):
                self.content = json.loads(obj["content"])
            else:
                self.content = obj["content"]
        if "status" in obj.keys():
            self.status = ExecutionStatus(str(obj["status"]))
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]


class Execution(ApiDto):
    """
    execution keeps all information on time, status and results of a specific pipeline manual or automatic run.

    :ivar uuid.UUID execution_id: technical id of execution.
    :ivar int execution_time: duration of the execution from started.
    :ivar uuid.UUID experiment_id: experiment id used in experiment mode.
    :ivar uuid.UUID pipeline_id: pipeline id executed or to execute.
    :ivar uuid.UUID pipeline_image_id: pipeline image package to use instead of current pipeline.
    :ivar dict properties: configuration, parameters and variables (only accessible from front-end to DS api).
    :ivar int queued_date: timestamp on which execution is queued, if none use createdDate
    :ivar int started_date: timestamp on which execution is started.
    :ivar wizata_dsapi.ExecutionStatus status: execution status.
    :ivar uuid.UUID template_id: template id linked to the pipeline.
    :ivar uuid.UUID trigger_id: trigger id used if automatic run.
    :ivar uuid.UUID twin_id: twin id registered on the template to run pipeline on.
    :ivar int waiting_time: duration of the waiting time in the queue.
    :ivar list warnings: list of error and/or warning messages.
    """

    @classmethod
    def route(cls):
        return "execute"

    @classmethod
    def from_dict(cls, data):
        obj = Execution()
        obj.from_json(data)
        return obj

    def __init__(self,
                 execution_id: int = None,
                 properties: dict = None,
                 pipeline: Pipeline = None,
                 pipeline_id: uuid.UUID = None,
                 pipeline_image_id: str = None,
                 experiment: Experiment = None,
                 experiment_id: uuid.UUID = None,
                 twin_id: uuid.UUID = None,
                 template_id: uuid.UUID = None,
                 trigger_id: uuid.UUID = None):

        self.execution_id = execution_id

        # Experiment
        if experiment is not None:
            self.experiment_id = experiment.experiment_id
        else:
            self.experiment_id = experiment_id

        # Trigger
        self.trigger_id = trigger_id
        self.twin_id = twin_id
        self.template_id = template_id

        # Pipeline
        if pipeline is not None:
            self.pipeline_id = pipeline.pipeline_id
        else:
            self.pipeline_id = pipeline_id
        self.pipeline_image_id = pipeline_image_id

        # Status and info
        self.status = None
        self.queued_date = None
        self.started_date = None
        self.execution_time = None
        self.waiting_time = None
        self.warnings = None
        self.edge_device_id = None

        # Only accessible between Front-End and DS API (not backend)
        if properties is None:
            properties = {}
        self.properties = properties

        # created/updated
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

        # outputs (only accessible within runners)
        self.models = []
        self.plots = []
        self.dataframes = []

    def set_id(self, id_value):
        if not isinstance(id_value, int):
            raise TypeError(f"execution id must be an integer")
        self.execution_id = id_value

    def api_id(self) -> str:
        return str(self.execution_id).upper()

    def endpoint(self) -> str:
        return "Executions"

    def to_json(self, target: str = None):
        obj = {}

        # Create doesn't have id now
        if self.execution_id is not None:
            obj["id"] = self.execution_id

        # Experiment
        if self.experiment_id is not None:
            obj["experimentId"] = str(self.experiment_id)

        # Pipeline
        if self.pipeline_id is not None:
            obj["pipelineId"] = str(self.pipeline_id)
        if self.pipeline_image_id is not None:
            obj["pipelineImageId"] = str(self.pipeline_image_id)

        # Trigger , Twin & Template
        if self.trigger_id is not None:
            obj["executionTriggerId"] = str(self.trigger_id)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)

        # Status and info
        if self.queued_date is not None:
            obj["queuedDate"] = self.queued_date
        if self.started_date is not None:
            obj["startedDate"] = self.started_date
        if self.execution_time is not None:
            obj["executionTime"] = self.execution_time
        if self.waiting_time is not None:
            obj["waitingTime"] = self.waiting_time
        if self.warnings is not None:
            obj["warnings"] = self.warnings
        if self.status is not None and isinstance(self.status, ExecutionStatus):
            obj["status"] = self.status.value
        if self.edge_device_id is not None:
            obj["edgeDeviceId"] = self.edge_device_id

        # Properties (DS API/Front-End only)
        if self.properties is not None and target is None:
            obj["properties"] = json.dumps(self.properties)

        # created/updated
        if self.createdById is not None:
            obj["createdById"] = self.createdById
        if self.createdDate is not None:
            obj["createdDate"] = self.createdDate
        if self.updatedById is not None:
            obj["updatedById"] = self.updatedById
        if self.updatedDate is not None:
            obj["updatedDate"] = self.updatedDate

        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.execution_id = int(obj["id"])

        # Experiment
        if "experimentId" in obj.keys() and obj["experimentId"] is not None:
            self.experiment_id = uuid.UUID(obj["experimentId"])

        # Pipeline
        if "pipelineId" in obj.keys() and obj["pipelineId"] is not None:
            self.pipeline_id = uuid.UUID(obj["pipelineId"])
        if "pipelineImageId" in obj.keys() and obj["pipelineImageId"] is not None:
            self.pipeline_image_id = obj["pipelineImageId"]

        # Trigger , Twin & Template
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
        if "executionTriggerId" in obj.keys() and obj["executionTriggerId"] is not None:
            self.trigger_id = uuid.UUID(obj["executionTriggerId"])

        # Status and Info
        if "queuedDate" in obj.keys() and obj["queuedDate"] is not None:
            self.queued_date = int(obj["queuedDate"])
        if "startedDate" in obj.keys() and obj["startedDate"] is not None:
            self.started_date = int(obj["startedDate"])
        if "waitingTime" in obj.keys() and obj["waitingTime"] is not None:
            self.waiting_time = int(obj["waitingTime"])
        if "executionTime" in obj.keys() and obj["executionTime"] is not None:
            self.execution_time = int(obj["executionTime"])
        if "warnings" in obj.keys() and obj["warnings"] is not None:
            self.warnings = obj["warnings"]
        if "status" in obj.keys():
            self.status = ExecutionStatus(str(obj["status"]))
        if "edgeDeviceId" in obj.keys() and obj["edgeDeviceId"] is not None:
            self.edge_device_id = obj["edgeDeviceId"]

        # Properties
        if "properties" in obj.keys() and obj["properties"] is not None:
            if isinstance(obj["properties"], str):
                if obj["properties"] == '':
                    self.properties = {}
                self.properties = json.loads(obj["properties"])
            else:
                self.properties = obj["properties"]

        # created/updated
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

