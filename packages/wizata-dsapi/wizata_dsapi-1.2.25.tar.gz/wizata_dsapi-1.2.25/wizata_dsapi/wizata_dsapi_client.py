import datetime
from datetime import timedelta
import json
import uuid
import sys
from typing import Tuple

import dill
import requests
import pickle
import pandas
import plotly
import msal
import os
import types
import wizata_dsapi
import urllib.parse

import string
import random

from .api_dto import ApiDto, VarType
from .business_label import BusinessLabel
from .plot import Plot
from .request import Request
from .mlmodel import MLModel
from .experiment import Experiment
from .script import Script
from .execution import Execution, ExecutionStatus
from .dsapi_json_encoder import DSAPIEncoder
from .group_system import GroupSystem
from .ds_dataframe import DSDataFrame
from .insight import Insight
from .model_toolkit import predict
from .template import Template, TemplateProperty
from .twinregistration import TwinRegistration
from .trigger import Trigger
from .twin import Twin
from .datapoint import DataPoint, BusinessType, Label, Category
from .pipeline import Pipeline, PipelineStep
from .pipeline_image import PipelineImage
from .solution_component import SolutionComponent, SolutionType
from .paged_query_result import PagedQueryResult
from .api_interface import ApiInterface
from .version import __version__
import ast
from .api_config import _registry

from .streamlit_utils import get_streamlit_token, get_streamlit_domain


def sanitize_url_parameter(param_value):
    illegal_characters = set(c for c in param_value if not (c.isalnum() or c in '-_., '))
    if illegal_characters:
        raise ValueError(f"illegal characters found in parameter {param_value}: {', '.join(illegal_characters)}")
    encoded_param_value = urllib.parse.quote(param_value)
    return encoded_param_value


def parse_string_list(s):
    try:
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return result
        else:
            return []
    except (ValueError, SyntaxError):
        return []


class WizataDSAPIClient(ApiInterface):
    """
    client wrapper to cloud data science API

    accessible preferably through wizata_dsapi.api() using os variables, you can also create an instance using __init__()
    please contact your administrator to receive configuration and connection details

    :ivar str domain: URL of data science API
    :ivar str client_id: azure authentication - client id
    :ivar str client_secret: azure authentication - your client secret API key
    :ivar str scope: azure authentication - scope
    :ivar str tenant_id: azure authentication - tenant
    :ivar str protocol: default - https
    :ivar str username: azure authentication - deprecated - username
    :ivar str password: azure authentication - deprecated - password
    """

    def __init__(self,
                 client_id=None,
                 scope=None,
                 tenant_id=None,
                 username=None,
                 password=None,
                 domain="localhost",
                 protocol="https",
                 client_secret=None):
        super().__init__()
        super()._set_registry("cloud_dsapi", _registry)

        # properties
        self.domain = domain
        self.protocol = protocol

        # authentication
        self.__username = username
        self.__password = password

        self.__client_id = client_id
        self.__tenant_id = tenant_id
        if tenant_id is not None:
            self.__authority = "https://login.microsoftonline.com/" + tenant_id
        self.__scopes = [scope]

        self.__interactive_token = None
        self.__daemon = False

        if client_secret is not None:
            self.__daemon = True
            self.__confidential_app = msal.ConfidentialClientApplication(
                client_id=self.__client_id,
                client_credential=client_secret,
                authority=self.__authority
            )

        if self.__client_id is not None:
            self.__app = msal.PublicClientApplication(
                client_id=self.__client_id,
                authority=self.__authority
            )

        self.roles = []
        self.twins = []

    def authenticate(self):
        """
        perform authentication on client side
        """
        result = self.__app.acquire_token_interactive(
            scopes=self.__scopes,
            success_template="""<html><body>You are authenticated and your code is running, you can close this page.<script>setTimeout(function(){window.close()}, 3000);</script></body></html> """
        )
        self.__daemon = False
        self.__interactive_token = result["access_token"]

    def __url(self):
        return self.protocol + "://" + self.domain + "/dsapi/"

    def __token(self):
        # Interactive Authentication
        if self.__interactive_token is not None:
            return self.__interactive_token

        streamlit_token = get_streamlit_token()
        if streamlit_token is not None:
            return streamlit_token

        if not self.__daemon:
            # Silent Authentication
            result = None
            accounts = self.__app.get_accounts(username=self.__username)
            if accounts:
                # If there is an account in the cache, try to get the token silently
                result = self.__app.acquire_token_silent(scopes=self.__scopes, account=accounts[0])

            if not result:
                # If there is no cached token, try to get a new token using the provided username and password
                result = self.__app.acquire_token_by_username_password(
                    username=self.__username,
                    password=self.__password,
                    scopes=self.__scopes
                )

            if "error_description" in result.keys():
                raise RuntimeError(str(result["error_description"]))

            if "access_token" in result.keys():
                return result["access_token"]
            else:
                raise RuntimeError(str(result))
        else:
            result = self.__confidential_app.acquire_token_silent(scopes=self.__scopes, account=None)

            if not result:
                result = self.__confidential_app.acquire_token_for_client(scopes=self.__scopes)

            if "error_description" in result.keys():
                raise RuntimeError(str(result["error_description"]))

            if "access_token" in result.keys():
                return result["access_token"]

            return result

    def __header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__token()}',
            'Wizata-Version': f'{__version__}'
        }

    def __raise_error(self, response):
        """
        raise a formatted error from an API response.
        :param response: response from the server.
        """
        if 'Content-Type' in response.headers and response.headers['Content-Type'] == 'application/json':
            json_content = response.json()
            if "errors" in json_content.keys():
                message = json_content["errors"][0]["message"]
                return RuntimeError(str(response.status_code) + " - " + message)
            else:
                return RuntimeError(str(response.status_code) + " - " + response.reason)
        else:
            raise RuntimeError(str(response.status_code) + " - " + response.reason)

    def access_check(self):
        """
        call the who am I request, to read proper headers and get specific information.
        :return: roles, twins
        """
        self._process_request(method='GET', route='whoami/')
        return self.roles, self.twins

    def _process_request(self,
                         method: str,
                         route: str,
                         dto_class=None,
                         result_type: str = None,
                         params: dict = None,
                         data=None):
        """
        process a request against DS API.
        :param method: HTTP operation method to use ( GET, POST, DELETE, PUT, ... )
        :param route: sub-route from main URL to target.
        :param dto_class: set a ApiDto class implementation to use (e.g. to format result)
        :param params: query parameters to add if presents
        :param result_type: set if result should be processed ('list', 'object')
        :param data: data for POST, PUT, PATCH requests
        """
        response = None
        if method == "GET":
            response = requests.request(
                "GET",
                self.__url() + route,
                headers=self.__header(),
                params=params
            )
        if method == "POST":
            response = requests.post(
                self.__url() + route,
                headers=self.__header(),
                params=params,
                data=data
            )
        if method == "PUT":
            response = requests.put(
                self.__url() + route,
                headers=self.__header(),
                params=params,
                data=data
            )
        if method == "DELETE":
            response = requests.delete(
                self.__url() + route,
                headers=self.__header(),
                params=params
            )
        if response is None:
            raise ValueError('Method not supported')
        if "Wizata-Version" in response.headers:
            server_version = response.headers["Wizata-Version"]
            if server_version != wizata_dsapi.__version__:
                print(f' * Warning - version mismatch - server {server_version} vs local {wizata_dsapi.__version__}')
                print(f'        python -m pip install --upgrade pip')
                print(f'        pip install wizata_dsapi=={server_version}')
        if response.status_code == 200:
            if 'Wizata-Roles' in response.headers:
                self.roles = parse_string_list(response.headers['Wizata-Roles'])
            if 'Wizata-Twins' in response.headers:
                self.twins = parse_string_list(response.headers['Wizata-Twins'])
            if result_type == "list":
                obj_list = []
                for obj_json in response.json():
                    obj_list.append(dto_class.from_dict(obj_json))
                return obj_list
            elif result_type == "json":
                return dto_class.from_dict(response.json())
            elif result_type == "pickle":
                pickle_bytes = response.content
                return pickle.loads(pickle_bytes)
            elif result_type == "dill":
                script_bytes = response.content
                return dill.loads(script_bytes)
            elif result_type == "bytes":
                content_bytes = response.content
                return content_bytes
            else:
                return response
        else:
            raise self.__raise_error(response)

    def _query(self, request: wizata_dsapi.Request) -> pandas.DataFrame:
        """
        Perform a request on Time-Series through DS API
        """
        return self._process_request(
            method="POST",
            route="execute/data",
            result_type="pickle",
            data=json.dumps(request.to_json(), cls=DSAPIEncoder)
        )

    def info(self):
        """
        print insights regarding version and supported operations
        """
        print(f"")
        print(f"version: {__version__} ")
        for class_name in _registry:
            print(f'Entity {class_name}')
            print(f' * Class    {_registry[class_name]["class"]} - ')
            print(f' * DS API   {_registry[class_name]["cloud_dsapi"]} - ')
            print(f' * Context  {_registry[class_name]["cloud_context"]}')
            print(f"")
        print(f"")

    def lists(self, entity):
        """
        lists all elements of a specific entity.
        :param entity: plural name of the entity or class (e.g. scripts, plots, mlmodels, dataframes...)
        :return: list of all elements with at least the id property.
        """
        dto_class = self._get_class(entity=entity, operation="lists")
        return self._process_request(
            method="GET",
            route=dto_class.route() + "/",
            dto_class=dto_class,
            result_type="list"
        )

    def get(self,
            obj=None,
            id: uuid.UUID = None,
            key: str = None,
            entity=None,
            script_name=None,
            experiment_key=None,
            pipeline_key=None,
            model_key=None,
            template_key=None,
            twin_hardware_id=None,
            datapoint_hardware_id=None):
        """
        get record content from DS API.

        - get will look first for obj then for id then for key (e.g. if id and key specified, key is ignored )

        :param obj: a wizata_dsapi.<Entity>() with UUID set - fetch using technical UUID

        :param id: a UUID of a specific object (use in combination of entity)
        :param key: a logical key of a specific object (e.g. hardware id for DataPoint and Twin (use in combination of entity)
        :param entity: plural name of the entity or class (use in combination of entity)(e.g. scripts, plots, mlmodels, dataframes...)
        :return: object with all properties or None if not found.

        """
        operation = "get_by_id"
        if obj is not None:
            if isinstance(obj, Request):
                return self._query(request=obj)
            else:
                dto_class = self._get_class(entity=type(obj), operation=operation)
                if dto_class == PipelineImage:
                    id = obj.api_id()
                else:
                    id = uuid.UUID(obj.api_id())
        elif entity is not None:
            if id is not None:
                dto_class = self._get_class(entity=entity, operation=operation)
            elif key is not None:
                operation = "get_by_key"
                dto_class = self._get_class(entity=entity, operation=operation)
            else:
                raise KeyError(f"cannot get record - get have an entity specified but no id or key")

        # deprecated exceptions
        elif script_name is not None:
            operation = "get_by_key"
            key = script_name
            dto_class = self._get_class(entity="scripts", operation=operation)
        elif experiment_key is not None:
            operation = "get_by_key"
            key = experiment_key
            dto_class = self._get_class(entity="experiments", operation=operation)
        elif model_key is not None:
            operation = "get_by_key"
            key = model_key
            dto_class = self._get_class(entity="mlmodels", operation=operation)
        elif pipeline_key is not None:
            operation = "get_by_key"
            key = pipeline_key
            dto_class = self._get_class(entity="pipelines", operation=operation)
        elif template_key is not None:
            operation = "get_by_key"
            key = template_key
            dto_class = self._get_class(entity="templates", operation=operation)
        elif twin_hardware_id is not None:
            operation = "get_by_key"
            key = twin_hardware_id
            dto_class = self._get_class(entity="twins", operation=operation)
        elif datapoint_hardware_id is not None:
            operation = "get_by_key"
            key = datapoint_hardware_id
            dto_class = self._get_class(entity="datapoints", operation=operation)

        # unsupported parameter combination
        else:
            raise KeyError(f"cannot get record - misconfiguration please provide valid obj or id+entity, key+entity")

        # get_by_id
        if operation == "get_by_id":
            return self._process_request(
                method="GET",
                route=dto_class.route() + "/" + str(id) + "/",
                dto_class=dto_class,
                result_type=dto_class.get_type()
            )

        # get_by_key
        elif operation == "get_by_key":
            if dto_class == Script:
                return self._process_request(
                    method="GET",
                    route=dto_class.route() + "/" + str(key) + "/",
                    dto_class=dto_class,
                    result_type=dto_class.get_type()
                )
            else:
                results = self._process_request(
                        method="GET",
                        route=dto_class.route() + "/",
                        dto_class=dto_class,
                        result_type="list",
                        params={'key': key}
                    )
                for result in results:
                    return result
                return None

    def create(self, obj) -> uuid.UUID:
        """
        create and save an object on the server
        :param obj: object from any supported entity (see info()) or python callable function (Script)
        :return: id of created object
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if not callable(obj) and isinstance(obj, Script):
            dto_class = self._get_class(entity=type(obj), operation="create")
            script = self._process_request(
                method="POST",
                route=dto_class.route() + "/",
                data=dill.dumps(obj),
                result_type="json")
            return script.script_id
        else:
            dto_class = self._get_class(entity=type(obj), operation="create")
            response = self._process_request(
                method="POST",
                route=dto_class.route() + "/",
                dto_class=dto_class,
                data=json.dumps(obj.to_json())
            )
            if dto_class.get_id_type() == int:
                obj.set_id(response.json()["id"])
                return response.json()["id"]
            else:
                return uuid.UUID(obj.api_id())

    def update(self, obj):
        """
        update and save an object on DS API
        :param obj: object to update on DS API (see info()) or python callable function (Script)
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if not callable(obj) and isinstance(obj, Script):
            dto_class = self._get_class(entity=type(obj), operation="update")
            self._process_request(
                method="PUT",
                route=dto_class.route() + "/" + str(obj.script_id) + "/",
                data=dill.dumps(obj),
                result_type="json")
        else:
            dto_class = self._get_class(entity=type(obj), operation="update")
            if dto_class.get_id_type() == uuid.UUID:
                id = uuid.UUID(obj.api_id())
            else:
                id = obj.api_id()
            self._process_request(
                method="PUT",
                route=dto_class.route() + "/" + str(id) + "/",
                dto_class=dto_class,
                data=json.dumps(obj.to_json())
            )

    def delete(self, obj):
        """
        delete an object on the server
        :param obj: object to delete including all content
        """
        dto_class = self._get_class(entity=type(obj), operation="delete")
        self._process_request(
            method="DELETE",
            route=dto_class.route() + "/" + obj.api_id() + "/"
        )

    def get_categories(self) -> dict:
        """
        get a name / uuid dictionary with all categories in platform.
        """
        response = requests.request("GET",
                                    self.__url() + "datapoints/categories/",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            categories_json = response.json()
            categories_dict = {}
            for category_json in categories_json:
                categories_dict[category_json["name"]] = category_json["id"]
            return categories_dict
        else:
            raise self.__raise_error(response)

    def get_units(self) -> dict:
        """
        get a name / uuid dictionary with all units in platform.
        """
        response = requests.request("GET",
                                    self.__url() + "datapoints/units/",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            units_json = response.json()
            units_dict = {}
            for unit in units_json:
                units_dict[unit["shortName"]] = unit["id"]
            return units_dict
        else:
            raise self.__raise_error(response)

    def get_business_labels(self) -> dict:
        """
        get a name / uuid dictionary with all business labels in platform.
        """
        response = requests.request("GET",
                                    self.__url() + "components/labels/",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            categories_json = response.json()
            categories_dict = {}
            for category_json in categories_json:
                categories_dict[category_json["name"]] = category_json["id"]
            return categories_dict
        else:
            raise self.__raise_error(response)

    def upsert(self, obj):
        """
        upsert on object on the server
        work with Script, MLModel or directly a function name

        :param obj: object to upsert on the server
        :return: ID of the object created or updated
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if isinstance(obj, Script):
            response = requests.put(self.__url() + "scripts/",
                                    headers=self.__header(),
                                    data=dill.dumps(obj))
            if response.status_code == 200:
                obj.script_id = uuid.UUID(response.json()['id'])
                return obj.script_id
            else:
                raise self.__raise_error(response)
        if isinstance(obj, MLModel):
            response = requests.put(self.__url() + "mlmodels/",
                                    headers=self.__header(),
                                    data=pickle.dumps(obj))
            if response.status_code == 200:
                obj.model_id = uuid.UUID(response.json()['id'])
                return obj.model_id
            else:
                raise self.__raise_error(response)
        if isinstance(obj, Template):
            return self.upsert_template(obj.key, obj.name)
        if isinstance(obj, Pipeline):
            return self.upsert_pipeline(pipeline=obj)
        if isinstance(obj, DataPoint):
            return self.upsert_datapoint(datapoint=obj)
        if isinstance(obj, Twin):
            return self.upsert_twin(twin=obj)
        else:
            raise TypeError("Type not supported.")

    def query(self,
              datapoints: list = None,
              start: datetime = None,
              end: datetime = None,
              interval: int = None,
              agg_method: str = "mean",
              template: str = None,
              twin: str = None,
              null: str = None,
              filters: dict = None,
              options: dict = None,
              group = None,
              field=None,
              bucket: str = None,
              tags: dict = None) -> pandas.DataFrame:
        """
        Query a dataframe from API.
        :param agg_method:
        :param datapoints: list of datapoints to fetch.
        :param start: start datetime of range to fetch
        :param end: end datetime of range to fetch
        :param interval: interval in milliseconds.
        :param template: template to fetch.
        :param twin: hardware ID of twin to fetch based on template.
        :param null: By default at 'drop' and dropping NaN values. If not intended behavior please set it to 'ignore' or 'all'.
        :param group: can be use to set group system and event retrieving instructions (dict or list[dict]).
        :param filters: dict of filters.
        :param options: dict of options.
        :param field: by default 'value' if none, accept str or list (e.g. value, reliability, eventId, ...)
        :param bucket: specify on which bucket the query applies.
        :return: dataframe
        """
        request = Request()

        if datapoints is not None:
            request.datapoints = datapoints

        if start is not None:
            request.start = start
        elif group is None:
            raise ValueError('start datetime is required.')

        if end is not None:
            request.end = end
        elif group is None:
            raise ValueError('end datetime is required.')

        if null is not None:
            request.null = null

        request.set_aggregation(agg_method, interval)

        if template is not None or twin is not None:
            request.select_template(
                template_key=template,
                twin_hardware_id=twin
            )

        if filters is not None:
            request.filters = filters

        if tags is not None:
            request.tags = tags

        if options is not None:
            request.options = options

        if group is not None:
            request.group = group

        if field is not None:
            if not isinstance(field, str) and not isinstance(field, list):
                raise TypeError('field must be str or list')
            request.field = field

        if bucket is not None:
            request.bucket = bucket

        return self._query(request=request)

    def batch_query(self,
                    step: timedelta,
                    datapoints: list = None,
                    start: datetime = None,
                    end: datetime = None,
                    interval: int = None,
                    agg_method: str = "mean",
                    template: str = None,
                    twin: str = None,
                    null: str = None,
                    filters: dict = None,
                    options: dict = None,
                    group: dict = None,
                    field=None,
                    bucket: str = None,
                    tags: dict = None,
                    verbose: bool = True) -> pandas.DataFrame:
        all_data = []
        current_start = start
        total_duration = (end - start).total_seconds()

        while current_start < end:
            current_end = min(current_start + step, end)

            progress = ((current_start - start).total_seconds() / total_duration) * 100
            if verbose:
                print(f"Querying from {current_start} to {current_end}... ({progress:.2f}% completed)")

            df_batch = wizata_dsapi.api().query(
                datapoints=datapoints,
                start=current_start,
                end=current_end,
                interval=interval,
                agg_method=agg_method,
                template=template,
                twin=twin,
                null=null,
                filters=filters,
                options=options,
                group=group,
                field=field,
                bucket=bucket,
                tags=tags
            )

            all_data.append(df_batch)
            current_start = current_end

        if verbose:
            print("100% completed. Concatenating results...")

        df_final = pandas.concat(all_data)

        return df_final

    def get_ts_query(self,
                     datapoints: list[str] = None,
                     start: datetime = None,
                     end: datetime = None,
                     interval: int = None,
                     agg_method: str = "mean",
                     template: str = None,
                     twin: str = None,
                     null: str = None,
                     filters: dict = None,
                     options: dict = None) -> str:
        """
        Get a Query string to Timeseries Database.
        :param agg_method:
        :param datapoints: list of datapoints to fetch.
        :param start: start datetime of range to fetch
        :param end: end datetime of range to fetch
        :param interval: interval in milliseconds.
        :param template: template to fetch.
        :param twin: hardware ID of twin to fetch based on template.
        :param null: By default at 'drop' and dropping NaN values. If not intended behavior please set it to 'ignore' or 'all'.
        :param filters: dict of filters.
        :param options: dict of options.
        :return: dataframe
        """
        request = Request()

        if datapoints is not None:
            request.add_datapoints(datapoints)

        if start is not None:
            request.start = start
        else:
            raise ValueError('start datetime is required.')

        if end is not None:
            request.end = end
        else:
            raise ValueError('end datetime is required.')

        if null is not None:
            request.null = null

        if interval is None:
            raise ValueError('interval is required.')
        request.set_aggregation(agg_method, interval)

        if template is not None and twin is not None:
            request.select_template(
                template_key=template,
                twin_hardware_id=twin
            )

        if filters is not None:
            request.filters = filters

        if options is not None:
            request.options = options

        response = requests.request("POST", self.__url() + "data/string",
                                    headers=self.__header(),
                                    data=json.dumps(request.to_json(), cls=DSAPIEncoder))
        if response.status_code == 200:
            return response.json()
        else:
            raise self.__raise_error(response)

    def __execute(self,
                  execution: Execution = None,
                  request: Request = None,
                  dataframe=None,
                  script=None,
                  ml_model=None,
                  isAnomalyDetection=False,
                  function=None,
                  experiment=None,
                  properties: dict = None,
                  pipeline=None,
                  image: str = None,
                  twin=None,
                  mode: str = 'experiment'
                  ) -> Execution:
        """
        internal function - deprecated - please use experiment() or test_run() instead.
        """
        # Prepare
        if execution is None:
            execution = Execution()
        if request is not None:
            execution.request = request
        if dataframe is not None:
            if isinstance(dataframe, pandas.DataFrame):
                execution.dataframe = dataframe
            elif isinstance(dataframe, DSDataFrame):
                execution.input_ds_dataframe = dataframe
        if script is not None:
            if isinstance(script, uuid.UUID) or (isinstance(script, str) and is_valid_uuid(script)):
                execution.script = Script(script)
            elif isinstance(script, str):
                execution.script = self.get(script_name=script)
            elif isinstance(script, Script):
                execution.script = script
        if ml_model is not None:
            if isinstance(ml_model, uuid.UUID) or (isinstance(ml_model, str) and is_valid_uuid(ml_model)):
                execution.ml_model = MLModel(ml_model)
            elif isinstance(ml_model, str):
                execution.ml_model = self.get(model_key=ml_model)
            elif isinstance(ml_model, MLModel):
                execution.ml_model = ml_model
        if image is not None:
            execution.pipeline_image_id = image
        if isAnomalyDetection:
            execution.isAnomalyDetection = True
        if function is not None:
            execution.function = function
        if experiment is not None:
            if isinstance(experiment, uuid.UUID):
                execution.experiment_id = experiment
            elif isinstance(experiment, str):
                execution.experiment_id = self.get(experiment_key=experiment).experiment_id
            elif isinstance(experiment, Experiment):
                execution.experiment_id = experiment.experiment_id
        if properties is not None and isinstance(properties, dict):
            execution.properties = properties

        if pipeline is not None:
            if isinstance(pipeline, uuid.UUID) or (isinstance(pipeline, str) and is_valid_uuid(pipeline)):
                execution.pipeline_id = pipeline
            elif isinstance(pipeline, str):
                execution.pipeline_id = self.get(pipeline_key=pipeline).pipeline_id
            elif isinstance(pipeline, Pipeline):
                execution.pipeline_id = pipeline.pipeline_id
        if twin is not None:
            if isinstance(twin, uuid.UUID) or (isinstance(twin, str) and is_valid_uuid(twin)):
                execution.twin_id = twin
            elif isinstance(twin, str):
                execution.twin_id = self.get(twin_hardware_id=twin).twin_id
            elif isinstance(twin, Twin):
                execution.twin_id = twin.twin_id

        # Execute
        if isinstance(execution, Execution):
            response = requests.post(f"{self.__url()}execute/?mode={mode}",
                                     headers=self.__header(),
                                     data=json.dumps(execution.to_json(), cls=DSAPIEncoder))

            # Parse
            if response.status_code == 200:
                obj = response.json()
                result_execution = Execution()
                result_execution.from_json(obj)
                if "plots" in obj.keys():
                    for plot in obj["plots"]:
                        result_execution.plots.append(self.get(Plot(plot_id=plot["id"])))
                if "models" in obj.keys():
                    for mlmodel in obj["models"]:
                        result_execution.models.append(self.get(MLModel(model_id=mlmodel["id"])))
                if "resultDataframe" in obj.keys() and obj["resultDataframe"]["id"] is not None:
                    result_execution.output_ds_dataframe = self.get(DSDataFrame(df_id=obj["resultDataframe"]["id"]))

                return result_execution
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("No execution have been loaded from parameters.")

    def experiment(self,
                   pipeline,
                   experiment=None,
                   twin=None,
                   image: str = None,
                   properties: dict = None,
                   train: bool = True,
                   plot: bool = True,
                   write: bool = False) -> Execution:
        """
        experiment and train models with a pipeline.

        - existing experiment is required (use create or upsert_experiment(key, name)).
        - if your pipeline is templated please provide a twin.
        - please provide all variables and parameters required through properties.
        - return an execution
            - check status with "wizata_dsapi.api().get(execution).status"
            - see plots with "wizata_dsapi.api().plots(execution)"

        :param experiment: existing experiment identified by its id (uuid or wizata_dsapi.Experiment) or key (str).
        :param pipeline: pipeline identified by its id (uuid or wizata_dsapi.Pipeline) or key (str) .
        :param twin: twin identified by its id (uuid or wizata_dsapi.Twin) or hardware ID (str)(optional).
        :param image: pipeline image id to use.
        :param properties: dictionary containing override for variables or additional parameters for your script.
        :param train: train machine learning model on model steps.
        :param plot: if False plot steps are ignored.
        :param write: if False write steps are ignored.
        """
        if not train or not plot or write:
            if properties is None:
                properties = {}
            if "execution_options" not in properties:
                properties["execution_options"] = {}
            properties["execution_options"]["train"] = train
            properties["execution_options"]["plot"] = plot
            properties["execution_options"]["write"] = write

        return self.__execute(
            experiment=experiment,
            pipeline=pipeline,
            twin=twin,
            image=image,
            properties=properties,
            mode='experiment'
        )

    def run(self,
            pipeline, twin=None,
            properties: dict = None,
            image: str = None,
            train: bool = False,
            plot: bool = False,
            write: bool = True) -> Execution:
        """
        run a pipeline.

        - existing models are used for simulation and prediction.
        - caution this might affect data inside platform or trigger automation.
        - if your pipeline is templated please provide a twin.
        - please provide all variables and parameters required through properties.
        - return an execution
            - check status with "wizata_dsapi.api().get(execution).status"
            - check results in platform (dashboard/explorer) or perform queries.

        :param pipeline: pipeline identified by its id (uuid or wizata_dsapi.Pipeline) or key (str).
        :param twin: twin identified by its id (uuid or wizata_dsapi.Twin) or hardware ID (str).
        :param properties: dictionary containing override for variables or additional parameters for your script.
        :param train: train machine learning model on model steps.
        :param image: pipeline image id to use.
        :param plot: if False plot steps are ignored.
        :param write: if False write steps are ignored.
        """

        if train or plot or not write:
            if properties is None:
                properties = {}
            if "execution_options" not in properties:
                properties["execution_options"] = {}
            properties["execution_options"]["train"] = train
            properties["execution_options"]["plot"] = plot
            properties["execution_options"]["write"] = write

        return self.__execute(
            pipeline=pipeline,
            twin=twin,
            properties=properties,
            image=image,
            mode='production'
        )

    def multi_run(self, pipeline_id, twin_ids: list, properties: dict = None):
        """
        run a pipeline against one or multiple twin in production.
        :param pipeline_id: UUID or str UUID of a pipeline.
        :param twin_ids: list of UUID or str UUID of asset registered on the pipeline.
        :param properties: optional properties of a pipeline (serializable as JSON).
        :return: list of executions IDs ("ids" key)
        """
        if isinstance(pipeline_id, uuid.UUID):
            pipeline_id = str(pipeline_id)
        else:
            pipeline_id = str(uuid.UUID(pipeline_id))

        if twin_ids is None or len(twin_ids) == 0:
            raise ValueError("please provide at least a valid twin id")

        formatted_ids = []
        for twin_id in twin_ids:
            if isinstance(twin_id, uuid.UUID):
                formatted_ids.append(str(twin_id))
            elif isinstance(twin_id, str):
                formatted_ids.append(str(uuid.UUID(twin_id)))
            else:
                raise TypeError(f'wrong type for twin-id')
        payload = {
            "pipelineId": pipeline_id,
            "twinIds": formatted_ids
        }
        if properties is not None:
            payload["properties"] = properties
        response = requests.post(f"{self.__url()}execute/pipelines/",
                                 headers=self.__header(),
                                 data=json.dumps(payload, cls=DSAPIEncoder))
        if response.status_code == 200:
            obj = response.json()
            return obj
        else:
            raise self.__raise_error(response)

    def plot(self, plot_id: str = None, plot: Plot = None, figure=None,):
        """
        Fetch and show plot.
        :param plot: Wizata Plot Object
        :param figure: JSON Figure
        :param plot_id: Plot Id
        :return: plotly figure
        """
        if plot is not None and plot.figure is not None:
            return plotly.io.from_json(plot.figure)
        elif plot is not None and plot.figure is None:
            plot = self.get(plot)
            if plot.figure is not None:
                return plotly.io.from_json(plot.figure)
            else:
                raise ValueError('No plot has been fetch.')
        elif figure is not None:
            return plotly.io.from_json(plot.figure)
        elif plot_id is not None:
            plot = self.get(Plot(plot_id=plot_id))
            if plot.figure is not None:
                return plotly.io.from_json(plot.figure)
            else:
                raise ValueError('No plot has been fetch.')
        else:
            raise KeyError('No valid arguments.')

    def plots(self, execution):
        """
        get all plot for an execution.
        :param execution: id or Execution.
        :return: list of plots.
        """

        if execution is None:
            raise ValueError("execution cannot be None to retrieve plot")
        if isinstance(execution, int):
            execution_id = execution
        elif isinstance(execution, str):
            execution_id = int(execution)
        elif isinstance(execution, Execution):
            execution_id = execution.execution_id
        else:
            raise Exception(f'unsupported type {execution}')

        response = requests.request("GET",
                                    self.__url() + f"plots/?generatedById={execution_id}",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            plots = []
            for plot in response.json():
                plots.append(self.plot(plot_id=str(plot["id"])))
            return plots
        else:
            raise self.__raise_error(response)

    def register_model(self,
                       model_key,
                       train_model,
                       df: pandas.DataFrame,
                       scaler=None,
                       has_anomalies: bool = False,
                       has_target_feat: bool = False,
                       experiment_key = None) -> tuple[MLModel, pandas.DataFrame]:
        """
        Register a Machine Learning model to Wizata.
        Model is tested by the API against a sample dataframe.
        :param model_key: logical string id to identify the model.
        :param train_model: trained model (must be compatible with pickle library)
        :param df: sample dataframe.
        :param scaler: scaler (must be compatible with pickle library)
        :param has_anomalies: True is model generate Anomalies
        :param has_target_feat: True if model need a target feature to be selected
        :param experiment_key: Reference of an experiment to which link the generated ML Model
        :return: registered ML Model , pandas.DataFrame
        """
        if model_key is None and isinstance(model_key, str):
            raise ValueError('Please provide a str Model Key to identify the model.')
        if train_model is None:
            raise ValueError('Trained Machine Learning model should not be null')
        elif df is None:
            raise ValueError('A sample dataframe must be provided')

        # Create a ML Model object
        ml_model = MLModel()
        ml_model.trained_model = train_model
        if scaler is not None:
            ml_model.scaler = scaler
        ml_model.has_anomalies = has_anomalies
        ml_model.has_target_feat = has_target_feat
        ml_model.input_columns = df.columns
        ml_model.key = model_key

        if experiment_key is not None:
            ml_model.experimentId = self.get(experiment_key=experiment_key).experiment_id

        try:
            result_df = predict(df, ml_model)
            if result_df is not None:
                ml_model.status = "valid"
                self.upsert(ml_model)
                return ml_model, result_df
            else:
                raise RuntimeError('no dataframe was generated by your model while testing predict capabilities')
        except Exception as e:
            raise RuntimeError('not able to validated the model : ' + str(e))

    def upsert_experiment(self, key: str, name: str, pipeline=None, twin=None):
        """
        Upsert an experiment.
        :param key: unique key identifying the experiment.
        :param name: display name of the experiment.
        :param pipeline: pipeline to set at creation only - cannot be updated.
        :param twin: twin uuid, hardware id or twin.
        :return: upserted experiment.
        """
        experiment = self.get(experiment_key=key)

        if twin:
            if isinstance(twin, uuid.UUID) or (isinstance(twin, str) and is_valid_uuid(twin)):
                experiment.twin_id = twin
            elif isinstance(twin, str):
                experiment.twin_id = self.get(twin_hardware_id=twin).twin_id
            elif isinstance(twin, Twin):
                experiment.twin_id = twin.twin_id

        if experiment is not None:
            found = True
            experiment.name = name
        else:
            experiment = Experiment(
                key=key,
                name=name
            )
            if pipeline:
                if isinstance(pipeline, uuid.UUID) or (isinstance(pipeline, str) and is_valid_uuid(pipeline)):
                    experiment.pipeline_id = pipeline
                elif isinstance(pipeline, str):
                    experiment.pipeline_id = self.get(pipeline_key=pipeline).pipeline_id
                elif isinstance(pipeline, Pipeline):
                    experiment.pipeline_id = pipeline.pipeline_id
            else:
                raise KeyError('please, specify a valid pipeline for an experiment creation.')
            found = False

        if not found:
            return self.create(experiment)
        else:
            return self.update(experiment)

    def upsert_template(self, key: str, name: str):
        """
        Upsert a template.
        :param key: unique key identifying the template.
        :param name: display name of the template
        :return: upserted template.
        """

        template = self.get(template_key=key)
        if template is not None:
            found = True
            template.name = name
        else:
            template = Template(
                key=key,
                name=name
            )
            found = False

        if not found:
            return self.create(template)
        else:
            return self.update(template)

    def upsert_pipeline(self, pipeline: Pipeline):
        """
        Upsert a template (ignore ID, use the key)
        :return: upserted template.
        """

        get = self.get(pipeline_key=pipeline.key)
        if get is not None:
            pipeline.pipeline_id = get.pipeline_id
            return self.update(pipeline)
        else:
            return self.create(pipeline)

    def upsert_datapoint(self, datapoint: DataPoint):
        """
        Upsert a datapoint (ignore ID, use the key)
        :return: upsert datapoint.
        """
        get = self.get(datapoint_hardware_id=datapoint.hardware_id)
        if get is not None:
            datapoint.datapoint_id = get.datapoint_id
            return self.update(datapoint)
        else:
            return self.create(datapoint)

    def upsert_twin(self, twin: Twin):
        """
        Upsert a twin (ignore ID, use the key)
        :return: upsert twin.
        """

        get = self.get(twin_hardware_id=twin.hardware_id)
        if get is not None:
            twin.twin_id = get.twin_id
            return self.update(twin)
        else:
            return self.create(twin)

    def add_template_property(self,
                              template,
                              property_name: str,
                              property_type: str = "datapoint",
                              is_required: bool = True) -> wizata_dsapi.TemplateProperty:

        # check type
        p_type = VarType(property_type)

        if isinstance(template, str):
            template_id = self.get(template_key=template).template_id
        elif isinstance(template, wizata_dsapi.Template):
            template_id = template.template_id
        elif isinstance(template, uuid.UUID):
            template_id = template
        else:
            raise TypeError('template should be a UUID or at least a key str referring template or a proper wizata_dsapi Template')

        template_property = wizata_dsapi.TemplateProperty(
            template_id=template_id,
            p_type=p_type,
            name=property_name,
            required=is_required
        )
        response = requests.post(self.__url() + "templateproperties/",
                                 headers=self.__header(),
                                 data=json.dumps(template_property.to_json()))
        if response.status_code == 200:
            return template_property
        else:
            raise self.__raise_error(response)

        # if isinstance(template, str):
        #     template = self.get(template_key=template)
        # elif not isinstance(template, Template):
        #     raise TypeError('template must be a key str referring template or a proper wizata_dsapi Template')
        #
        # if property_name is None:
        #     raise ValueError('please provide a valid name for the property')
        #
        # property_dict = {
        #     "type": p_type.value,
        #     "name": property_name,
        #     "required": is_required
        # }
        #
        # response = requests.post(self.__url() + "templates/" + str(template.template_id) + '/properties/',
        #                          headers=self.__header(),
        #                          data=json.dumps(property_dict))
        # if response.status_code == 200:
        #     return
        # else:
        #     raise self.__raise_error(response)

    def remove_template_property(self, template, property_name: str):

        if isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be a key str referring template or a proper wizata_dsapi Template')

        if property_name is None:
            raise ValueError('please provide a valid name for the property')

        property_dict = {
            "name": property_name
        }

        response = requests.delete(self.__url() + "templates/" + str(template.template_id) + '/properties/',
                                   headers=self.__header(),
                                   data=json.dumps(property_dict))
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def get_registrations(self, template) -> list:
        """
        retrieve all registrations for
        :param template: template object, UUID or str key.
        :return: list of twin registration.
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')
        if template is None:
            raise ValueError('template cannot be found on server')

        response = requests.get(self.__url() + "templates/" + str(template.template_id) + '/registrations/',
                                headers=self.__header())
        if response.status_code == 200:
            registrations_json = response.json()
            registrations = []
            for twin_registration_json in registrations_json:
                registration = TwinRegistration()
                registration.from_json(twin_registration_json)
                registrations.append(registration)
            return registrations
        else:
            raise self.__raise_error(response)

    def register_twin(self, template, twin, properties: dict, override=True):
        """
        register a twin on a specific template using a map.
        :param template: template object, UUID or str key.
        :param twin: twin object, UUID or str key.
        :param properties: dict where key = template property and value = datapoint name or const value (str, int, float, relative or epoch datetime).
        :param override: by default at True - allow overriding any existing subscription
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')

        if template is None:
            raise ValueError('template cannot be found on server')

        if twin is None:
            raise ValueError('twin must be specified.')
        elif isinstance(twin, uuid.UUID):
            twin_id = twin
        elif isinstance(twin, str):
            twin_id = self.get(twin_hardware_id=twin).twin_id
        elif isinstance(twin, Twin):
            twin_id = twin.twin_id
        else:
            raise TypeError('twin must be UUID, a key str referring hardware ID or a proper wizata_dsapi Twin')

        if template.properties is None or len(template.properties) == 0:
            raise ValueError('template chosen does not contains any properties')

        if properties is None or len(properties.keys()) == 0:
            raise ValueError('your map dictionary must contains properties matching template')

        twin_properties = {
            "properties": []
        }
        for key in properties.keys():
            property_type = None
            for template_property in template.properties:
                template_property: TemplateProperty
                if key == template_property.name:
                    property_type = template_property.p_type
            if property_type is None:
                raise ValueError(f'cannot find property {key} in template or cannot determine its type')
            twin_properties["properties"].append({
                'name': key,
                property_type.value: properties[key]
            })

        # Check if already exist
        exists = False
        response_exists = requests.get(self.__url() + "templates/" + str(template.template_id)
                                       + '/registrations/' + str(twin_id) + '/',
                                       headers=self.__header())
        if response_exists.status_code == 200:
            exists = True

        if exists and not override:
            raise ValueError("registration already exists and override not allowed.")

        if exists and override:
            response = requests.put(self.__url() + "templates/" + str(template.template_id)
                                    + '/registrations/' + str(twin_id) + '/',
                                    headers=self.__header(),
                                    data=json.dumps(twin_properties))
        else:
            response = requests.post(self.__url() + "templates/" + str(template.template_id)
                                     + '/registrations/' + str(twin_id) + '/',
                                     headers=self.__header(),
                                     data=json.dumps(twin_properties))

        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def unregister_twin(self, template, twin):
        """
        un-register a twin from a specific template.
        :param template: template object, UUID or str key.
        :param twin: twin object, UUID or str key.
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')

        if twin is None:
            raise ValueError('twin must be specified.')
        elif isinstance(twin, uuid.UUID):
            twin_id = twin
        elif isinstance(twin, str):
            twin_id = self.get(twin_hardware_id=twin).twin_id
        elif isinstance(twin, Twin):
            twin_id = twin.twin_id
        else:
            raise TypeError('twin must be UUID, a key str referring hardware ID or a proper wizata_dsapi Twin')

        response = requests.delete(self.__url() + "templates/" + str(template.template_id)
                                   + '/registrations/' + str(twin_id) + '/',
                                   headers=self.__header())
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def create_component(self, component: SolutionComponent):
        """
        create a component based on its ID.
        """
        if component is None:
            raise ValueError("component cannot be null")

        response = requests.post(self.__url() + "components/",
                                 headers=self.__header(),
                                 data=json.dumps(component.to_json()))

        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def update_component(self, component: SolutionComponent):
        """
        update a component based on its ID.
        """
        if component is None:
            raise ValueError("component cannot be null")

        response = requests.put(self.__url() + "components/" + str(component.solution_component_id) + "/",
                                 headers=self.__header(),
                                 data=json.dumps(component.to_json()))

        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def get_datapoint_mappings(self, registration):
        """
        get datapoint mapping from a registration.
        """
        if isinstance(registration, uuid.UUID):
            registration = str(registration)
        elif isinstance(registration, TwinRegistration):
            registration = str(registration.twin_registration_id)
        response = requests.request("GET",
                                    self.__url() + "registrations/" + registration + "/mapping/",
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            return response.json()
        else:
            raise self.__raise_error(response)

    def get_components(self,
                       label_id: uuid.UUID = None,
                       twin_id: uuid.UUID = None,
                       template_id: uuid.UUID = None,
                       owner_id: uuid.UUID = None,
                       organization_only: bool = False,
                       name: str = None):
        """
        get components
        :param label_id: filter on a specific label
        :param template_id: filter on a specific template
        :param twin_id: filter on a specific twin
        :param owner_id: filter on a specific owner_id
        :param organization_only: work only with organization components (by default - False)
        :param name: filter on a specific name (contains)
        """
        params = {}
        if label_id is not None:
            params['labelId'] = str(label_id)
        if twin_id is not None:
            params['twinId'] = str(twin_id)
        if template_id is not None:
            params['templateId'] = str(template_id)
        if owner_id is not None:
            params['ownerId'] = str(owner_id)
        if organization_only:
            params['organizatianOnly'] = True
        if name is not None:
            params['name'] = str(name)
        response = requests.request("GET",
                                    self.__url() + "components/",
                                    params=params,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            components = []
            for json_model in response.json():
                component = SolutionComponent()
                component.from_json(json_model)
                components.append(component)
            return components
        else:
            raise self.__raise_error(response)

    def delete_component(self, component_id: uuid.UUID):
        response = requests.delete(self.__url() + "components/" + str(component_id) + '/',
                                   headers=self.__header())
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def search_datapoints(self,
                          page: int = 1,
                          size: int = 20,
                          sort: str = "id",
                          direction: str = "asc",
                          hardware_id: str = None,
                          categories: list = None,
                          business_types: list = None,
                          twin=None,
                          recursive: bool = False) -> PagedQueryResult:
        """
        get datapoints with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param hardware_id: filter on a specific hardware ID name or partial name.
        :param business_types: list of BusinessType or str.
        :param categories: list of UUID or Category.
        :param twin: uuid or Twin element to search datapoints.
        :param recursive: set to True in combination of a twin to look inside all sub-twins recursively.
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        query = PagedQueryResult(
            page=page,
            size=size,
            sort=sort,
            direction=direction
        )

        if sort not in ["id", "hardwareId", "createdDate", "createdById", "updatedDate", "updatedById",
                        "unitId", "businessType", "categoryId", "description"]:
            raise ValueError("invalid sort column")

        parameter_str = "?page=" + str(page) + "&size=" + str(size) + "&sort=" + str(sort) + "&direction=" + str(direction)
        if hardware_id is not None:
            parameter_str += "&hardwareId=" + sanitize_url_parameter(hardware_id)
        if business_types is not None and len(business_types) > 0:
            list_str = []
            for businessType in business_types:
                if isinstance(businessType, str):
                    list_str.append(businessType)
                elif isinstance(businessType, BusinessType):
                    list_str.append(businessType.value)
                else:
                    raise ValueError('business type must be a BusinessType or a str')
            parameter_str += "&businessTypes=" + sanitize_url_parameter(",".join(list_str))
        if categories is not None and len(categories) > 0:
            list_str = []
            for categoryId in categories:
                if isinstance(categoryId, uuid.UUID):
                    list_str.append(str(categoryId))
                if isinstance(categoryId, str):
                    list_str.append(categoryId)
                elif isinstance(categoryId, Category):
                    list_str.append(str(categoryId.category_id))
                else:
                    raise ValueError('category must be a Category, UUID or a str UUID')
            parameter_str += "&categoryIds=" + sanitize_url_parameter(",".join(list_str))

        if recursive is not None and recursive:
            parameter_str += "&recursive=" + sanitize_url_parameter("true")

        if twin is not None:
            if isinstance(twin, uuid.UUID):
                twin = str(twin)
            if isinstance(twin, str):
                twin = twin
            elif isinstance(twin, Twin):
                twin = str(twin.twin_id)
            else:
                raise ValueError('category must be a Twin, UUID or a str UUID')
            parameter_str += "&twinId=" + sanitize_url_parameter(twin)

        response = requests.request("GET",
                                    self.__url() + "datapoints/filter" + parameter_str,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            response_obj = response.json()
            query.total = int(response_obj["total"])
            query.results = []
            for obj in response_obj["results"]:
                datapoint = DataPoint()
                datapoint.from_json(obj)
                query.results.append(datapoint)
            return query
        else:
            raise self.__raise_error(response)

    def search_twins(self,
                     page: int = 1,
                     size: int = 20,
                     sort: str = "id",
                     direction: str = "asc",
                     hardware_id: str = None,
                     name: str = None,
                     parents: list = None) -> PagedQueryResult:
        """
        get twins with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param hardware_id: filter on a specific hardware ID name or partial name.
        :param name: name or part of twin name.
        :param parents: list of all possible parents (Twin, UUID, or str UUID).
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        query = PagedQueryResult(
            page=page,
            size=size,
            sort=sort,
            direction=direction
        )

        if sort not in ["id", "hardwareId", "createdDate", "createdById", "updatedDate", "updatedById",
                        "name", "description"]:
            raise ValueError("invalid sort column")

        parameter_str = "?page=" + str(page) + "&size=" + str(size) + "&sort=" + str(sort) + "&direction=" + str(direction)
        if hardware_id is not None:
            parameter_str += "&hardwareId=" + sanitize_url_parameter(hardware_id)
        if parents is not None and len(parents) > 0:
            list_str = []
            for parent in parents:
                if isinstance(parent, uuid.UUID):
                    list_str.append(str(parent))
                elif isinstance(parent, str):
                    list_str.append(parent)
                elif isinstance(parent, Twin):
                    list_str.append(str(parent.twin_id))
                else:
                    raise ValueError('parent must be a Twin or a str')
            parameter_str += "&parentIds=" + sanitize_url_parameter(",".join(list_str))

        if name is not None:
            parameter_str += "&name=" + sanitize_url_parameter(name)

        response = requests.request("GET",
                                    self.__url() + "twins/filter" + parameter_str,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            response_obj = response.json()
            query.total = int(response_obj["total"])
            query.results = []
            for obj in response_obj["results"]:
                twin = Twin()
                twin.from_json(obj)
                query.results.append(twin)
            return query
        else:
            raise self.__raise_error(response)

    def search_insights(self,
                        page: int = 1,
                        size: int = 20,
                        sort: str = "id",
                        direction: str = "asc",
                        datapoint_id: str = None,
                        twin_id: str = None,
                        component_id: list = None):
        """
        get insights with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param datapoint_id: id of the datapoint on which filtering the insights.
        :param twin_id: id of the twin on which filtering the insights.
        :param component_id: id of the component on which filtering the insights.
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        query = PagedQueryResult(
            page=page,
            size=size,
            sort=sort,
            direction=direction
        )

        if sort not in ["id", "sensorId", "twinId", "componentId",
                        "name", "displayPrecision"]:
            raise ValueError("invalid sort column")

        parameter_str = "?page=" + str(page) + "&size=" + str(size) + "&sort=" + str(sort) + "&direction=" + str(direction)

        if datapoint_id is not None:
            parameter_str += "&datapointId=" + sanitize_url_parameter(str(datapoint_id))

        if twin_id is not None:
            parameter_str += "&twinId=" + sanitize_url_parameter(str(twin_id))

        if component_id is not None:
            parameter_str += "&componentId=" + sanitize_url_parameter(str(component_id))

        response = requests.request("GET",
                                    self.__url() + "insights/filter" + parameter_str,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            response_obj = response.json()
            query.total = int(response_obj["total"])
            query.results = []
            for obj in response_obj["results"]:
                insight = Insight()
                insight.from_json(obj)
                query.results.append(insight)
            return query
        else:
            raise self.__raise_error(response)

    def search_executions(self,
                          page: int = 1,
                          size: int = 20,
                          sort: str = "id",
                          direction: str = "asc",
                          pipeline_id: uuid.UUID = None,
                          twin_id:  uuid.UUID = None,
                          template_id: uuid.UUID = None,
                          status: ExecutionStatus = None) -> PagedQueryResult:
        """
        get executions with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param pipeline_id: filter on a specific pipeline.
        :param twin_id: filter on a specific twin.
        :param template_id: filter on a specific template.
        :param status: filter on a specific status.
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        query = PagedQueryResult(
            page=page,
            size=size,
            sort=sort,
            direction=direction
        )

        if sort not in ["id", "pipelineId", "twinId", "templateId",
                        "createdDate" , "createdById",
                        "updatedDate", "updatedById",
                        "status"]:
            raise ValueError("invalid sort column")

        parameter_str = "?page=" + str(page) + "&size=" + str(size) + "&sort=" + str(sort) + "&direction=" + str(direction)

        if pipeline_id is not None:
            parameter_str += "&pipelineId=" + sanitize_url_parameter(str(pipeline_id))

        if twin_id is not None:
            parameter_str += "&twinId=" + sanitize_url_parameter(str(twin_id))

        if template_id is not None:
            parameter_str += "&templateId=" + sanitize_url_parameter(str(template_id))

        if status is not None:
            if not isinstance(status, ExecutionStatus):
                raise ValueError(f'status is not a valid ExecutionStatus')
            parameter_str += "&status=" + sanitize_url_parameter(status.value)

        response = requests.request("GET",
                                    self.__url() + "execute/filter" + parameter_str,
                                    headers=self.__header()
                                    )
        if response.status_code == 200:
            response_obj = response.json()
            query.total = int(response_obj["total"])
            query.results = []
            for obj in response_obj["results"]:
                execution = Execution()
                execution.from_json(obj)
                query.results.append(execution)
            return query
        else:
            raise self.__raise_error(response)

    def abort(self, executions: list) -> str:
        """
        send an abort request for executions and return a result message
        :param executions: must be a list containing uuid or Execution.
        """
        if executions is None or len(executions) == 0:
            raise ValueError(f'please provide at list one execution to abort')

        payload = {
            'ids': []
        }
        for execution in executions:
            if isinstance(execution, uuid.UUID):
                payload['ids'].append(str(execution))
            if isinstance(execution, str):
                payload['ids'].append(str(uuid.UUID(execution)))
            if isinstance(execution, Execution):
                payload['ids'].append(str(execution.execution_id))
        response = requests.post(
            self.__url() + "execute/abort",
            headers=self.__header(),
            data=json.dumps(payload)
        )
        return response.text

    def build_image(self, key: str) -> str:
        """
        build an image of a pipeline, store it on the image repository and return its pipeline image id.
        :param key: pipeline key.
        :return: image id.
        """
        response = self._process_request(
            method="POST",
            route=PipelineImage.route() + "/",
            dto_class=PipelineImage,
            data=json.dumps({
                'key': key
            })
        )
        return response.json()["id"]

    def download_image(self, pipeline_image_id: str) -> PipelineImage:
        """
        download a pipeline image from the repository
        :param pipeline_image_id: id of image
        :return: packaged (unzipped) as a PipelineImage
        """

        response_bytes = self._process_request(
            method="GET",
            route=PipelineImage.route() + "/" + str(pipeline_image_id) + "/download/",
            result_type="bytes"
        )
        image = PipelineImage.loads(pipeline_image_id=pipeline_image_id, g_bytes=response_bytes)
        return image


def api() -> WizataDSAPIClient:
    """
    Create a WizataDSAPIClient from environment variables.
    :return: client
    """
    protocol = 'https'

    streamlit_domain = get_streamlit_domain()
    if streamlit_domain is not None:
        return WizataDSAPIClient(
            domain=streamlit_domain,
            protocol=protocol
        )

    if os.environ.get('WIZATA_CLIENT_ID') is None:
        raise ValueError('please configure OS variables to authenticate with api() method')

    if os.environ.get('WIZATA_PROTOCOL') is not None:
        protocol = os.environ.get('WIZATA_PROTOCOL')

    if os.environ.get('WIZATA_CLIENT_SECRET') is not None:
        scope = os.environ.get('WIZATA_SCOPE')
        if scope is None:
            scope = os.environ.get('WIZATA_CLIENT_ID') + '/.default'
        return WizataDSAPIClient(
            tenant_id=os.environ.get('WIZATA_TENANT_ID'),
            client_id=os.environ.get('WIZATA_CLIENT_ID'),
            client_secret=os.environ.get('WIZATA_CLIENT_SECRET'),
            scope=scope,
            domain=os.environ.get('WIZATA_DOMAIN'),
            protocol=protocol
        )
    else:
        return WizataDSAPIClient(
            tenant_id=os.environ.get('WIZATA_TENANT_ID'),
            client_id=os.environ.get('WIZATA_CLIENT_ID'),
            scope=os.environ.get('WIZATA_SCOPE'),
            username=os.environ.get('WIZATA_USERNAME'),
            password=os.environ.get('WIZATA_PASSWORD'),
            domain=os.environ.get('WIZATA_DOMAIN'),
            protocol=protocol
        )


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
