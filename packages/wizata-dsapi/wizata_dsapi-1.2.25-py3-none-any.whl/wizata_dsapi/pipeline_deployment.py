import uuid

from .api_dto import ApiDto


class PipelineDeployment(ApiDto):
    """
    Pipeline Deployment contains deployment instruction for a pipeline.

    :ivar deployment_type: str with values "stream" or "classic"
    """

    def __init__(self,
                 pipeline_deployment_id: uuid.UUID = None,
                 pipeline_id: uuid.UUID = None,
                 deployment_type: str = None):

        if pipeline_deployment_id is None:
            pipeline_deployment_id = uuid.uuid4()
        self.pipeline_deployment_id = pipeline_deployment_id
        self.pipeline_id = pipeline_id
        self.deployment_type = deployment_type

    def from_json(self, obj):
        """
        load from JSON dictionary representation
        """
        if "id" in obj.keys():
            self.pipeline_deployment_id = uuid.UUID(obj["id"])
        if "pipelineId" in obj.keys() and obj["pipelineId"] is not None:
            self.pipeline_id = uuid.UUID(obj['pipelineId'])
        if "deploymentType" in obj.keys() and obj["deploymentType"] is not None:
            if str(obj["deploymentType"]) not in ['stream', 'classic']:
                raise ValueError('deployment type must be stream or classic.')
            self.deployment_type = str(obj["deploymentType"])

    def to_json(self):
        """
        convert object to a proper dictionary
        """
        obj = {
            "id": str(self.pipeline_deployment_id)
        }
        if self.pipeline_id is not None:
            obj["pipelineId"] = str(self.pipeline_id)
        if self.deployment_type is not None and str(self.deployment_type) in ['stream', 'classic']:
            obj["deploymentType"] = str(self.deployment_type)
        return obj
