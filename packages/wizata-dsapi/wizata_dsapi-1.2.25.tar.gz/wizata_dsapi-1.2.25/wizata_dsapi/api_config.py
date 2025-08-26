# Api Entities (Dto)
from .plot import Plot
from .datapoint import DataPoint
from .datastore import DataStore
from .mlmodel import MLModel
from .request import Request
from .execution import Execution, ExecutionStatus
from .experiment import Experiment
from .evaluation import Evaluation
from .group_system import GroupSystem
from .script import Script
from .template import Template, TemplateProperty
from .solution_component import SolutionComponent
from .business_label import BusinessLabel
from .twinregistration import TwinRegistration, TwinRegistrationProperty
from .trigger import Trigger
from .twin import Twin, TwinType
from .pipeline import Pipeline
from .pipeline_image import PipelineImage
from .insight import Insight


# init APIs supported operations
_registry = {
    "business_labels":
        {
            "class": BusinessLabel,
            "cloud_dsapi": ["lists"],
            "cloud_context": []
        },
    "components":
        {
            "class": SolutionComponent,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": ['get_by_id', 'create', 'update', 'delete']
        },
    "datapoints":
        {
            "class": DataPoint,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'create', 'update', 'delete', 'search'],
            "cloud_context": ['get_by_id', 'get_by_key', 'create', 'update', 'delete', 'search']
        },
    "datastores":
        {
            "class": DataStore,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": []
        },
    "evaluations":
        {
            "class": Evaluation,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": ['get_by_id', 'create', 'update', 'delete']
        },
    "executions":
        {
            "class": Execution,
            "cloud_dsapi": ['get_by_id', 'search', 'abort'],
            "cloud_context": []
        },
    "experiments":
        {
            "class": Experiment,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'create', 'update', 'delete'],
            "cloud_context": []
        },
    "groupsystems":
        {
            "class": GroupSystem,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'create', 'update', 'delete'],
            "cloud_context": []
        },
    "insights":
        {
            "class": Insight,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete', 'search'],
            "cloud_context": ['get_by_id', 'create', 'update', 'delete', 'search']
        },
    "mlmodels":
        {
            "class": MLModel,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'delete'],
            "cloud_context": []
        },
    "pipelines":
        {
            "class": Pipeline,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'create', 'update', 'delete'],
            "cloud_context": []
        },
    "pipelineimages":
        {
            "class": PipelineImage,
            "cloud_dsapi": ['lists', 'get_by_id', 'delete', 'build_image', 'download_image'],
            "cloud_context": []
        },
    "plots":
        {
            "class": Plot,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'delete'],
            "cloud_context": []
        },
    "registrations":
        {
            "class": TwinRegistration,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": ['get_by_id', 'create', 'update', 'delete']
        },
    "registrationproperties":
        {
            "class": TwinRegistrationProperty,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": []
        },
    "request":
        {
            "class": Request,
            "cloud_dsapi": ['query'],
            "cloud_context": ['query']
        },
    "scripts":
        {
            "class": Script,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'create', 'update', 'delete'],
            "cloud_context": []
        },
    "templates":
        {
            "class": Template,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'create', 'update', 'delete'],
            "cloud_context": ['get_by_id', 'get_by_key', 'create', 'update', 'delete']
        },
    "templateproperties":
        {
            "class": TemplateProperty,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": []
        },
    "triggers":
        {
            "class": Trigger,
            "cloud_dsapi": ['lists', 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": ['get_by_id']
        },
    "twins":
        {
            "class": Twin,
            "cloud_dsapi": ['lists', 'get_by_id', 'get_by_key', 'create', 'update', 'delete', 'search'],
            "cloud_context": ['get_by_id', 'get_by_key', 'create', 'update', 'delete', 'search']
        },
    "twintypes":
        {
            "class": TwinType,
            "cloud_dsapi": [ 'get_by_id', 'create', 'update', 'delete'],
            "cloud_context": [ 'get_by_id', 'create', 'update', 'delete' ]
        }
}
