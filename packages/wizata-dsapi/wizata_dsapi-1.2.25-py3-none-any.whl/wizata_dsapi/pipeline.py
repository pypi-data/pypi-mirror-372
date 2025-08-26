import uuid
import json

import pandas
import wizata_dsapi

from .api_dto import ApiDto, VarType
from .script import ScriptConfig, Script
from .request import Request
from .mlmodel import MLModelConfig
from .template import Template, TemplateProperty
from .twin import Twin
from .twinregistration import TwinRegistration, TwinRegistrationProperty

from enum import Enum


class RunnerStatus(Enum):
    """
    defines a runner status.
        - starting: runner is starting but not yet listening to the queue
        - listening: runner is listening to the queue
        - executing: runner is executing some package and will continue listening
        - pausing: runner is executing some pipeline and will stop listening
        - idle: runner is stopped and is doing nothing
        - terminating: runner is executing and will terminate the process (and then restart auto)
    """
    STARTING = 'starting'
    LISTENING = 'listening'
    EXECUTING = 'executing'
    PAUSING = 'pausing'
    IDLE = 'idle'
    TERMINATING = 'terminating'


class StepType(Enum):
    """
    defines a pipeline step type.
        - "query"
        - "script"
        - "model"
        - "write"
        - "plot"
        - "df_save"
    """
    QUERY = 'query'
    SCRIPT = 'script'
    MODEL = 'model'
    WRITE = 'write'
    PLOT = 'plot'
    DF_SAVE = 'df_save'


class AlertType(Enum):
    """
    defines a type of alert.
        - "sms"
        - "email"
    """
    SMS = 'sms'
    EMAIL = 'email'
    SLACK = 'slack'
    TEAMS = 'teams'
    WHATSAPP = 'whatsapp'


class WriteConfig:
    """
    define how a step should write data into Wizata.

    can use a mapping table (key=dataframe column, value=hardware id or template property).

    :ivar uuid.UUID config_id: technical id of this configuration.
    :ivar dict datapoints: mapping dict between dataframe column and Wizata datapoint hardware id or template property.
    :ivar str map_property_name: define name of a context property containing a mapping table to use.
    """

    def __init__(self,
                 config_id = None,
                 datapoints: dict = None,
                 map_property_name: str = None,
                 bucket: str = None,
                 writer_type: str = None):
        if config_id is None:
            config_id = uuid.uuid4()
        self.config_id = config_id
        self.datapoints = datapoints
        self.map_property_name = map_property_name
        self.bucket = bucket
        self.writer_type = writer_type

    def from_json(self, obj):
        if "id" in obj:
            self.config_id = obj["id"]
        if "datapoints" in obj:
            self.datapoints = obj["datapoints"]
        if "map_property_name" in obj and obj["map_property_name"] is not None:
            self.map_property_name = str(obj["map_property_name"])
        if "bucket" in obj and obj["bucket"] is not None:
            self.bucket = obj["bucket"]
        if "writerType" in obj and obj["writerType"] is not None:
            self.writer_type = obj["writerType"]

    def to_json(self):
        obj = {
            "id": str(self.config_id)
        }
        if self.datapoints is not None:
            obj["datapoints"] = self.datapoints
        if self.bucket is not None:
            obj["bucket"] = self.bucket
        if self.map_property_name is not None:
            obj["map_property_name"] = self.map_property_name
        if self.writer_type is not None:
            obj["writerType"] = self.writer_type
        return obj


class PipelineIO(ApiDto):
    """
    define an input or output of a pipeline step.
    :ivar str dataframe: name of the dataframe to connect input and output, used in context.dafaframes
    :ivar dict mapping: mapping to rename dataframe column from key to value.
    :ivar list drops: list of columns to drop from dataframe.
    :ivar list columns: list of columns to select from dataframe and exclude others.
    """

    def __init__(self, dataframe: str = None, mapping: dict = None, drops: list = None, columns: list = None):
        self.dataframe = dataframe
        self.mapping = mapping
        self.drops = drops
        self.columns = columns

    def from_json(self, obj):
        if "dataframe" in obj:
            self.dataframe = obj["dataframe"]
        else:
            raise ValueError(f'a pipeline I/O should have at least a dataframe name.')
        if "mapping" in obj and obj["mapping"] is not None:
            if not isinstance(obj["mapping"], dict):
                raise TypeError(f'mapping should be dict not a {obj["mapping"].__class__.__name__}')
            self.mapping = obj["mapping"]
        if "drops" in obj and isinstance(obj['drops'], list):
            self.drops = obj['drops']
        if "columns" in obj and isinstance(obj['columns'], list):
            self.columns = obj['columns']

    def to_json(self, target: str = None):
        if self.dataframe is None or not isinstance(self.dataframe, str):
            raise ValueError(f'a pipeline I/O should have at least a dataframe name.')
        obj = {
            "dataframe": self.dataframe
        }
        if self.mapping is not None and isinstance(self.mapping, dict):
            obj["mapping"] = self.mapping
        if self.drops is not None and isinstance(self.drops, list):
            obj["drops"] = self.drops
        if self.columns is not None and isinstance(self.columns, list):
            obj["columns"] = self.columns
        return obj

    def prepare(self, df: pandas.DataFrame) -> pandas.DataFrame:
        """
        prepare the dataframe based in information from this pipeline I/O definition.
        perform mapping, selection and drops.
        :param pandas.DataFrame df: dataframe to prepare.
        :return: prepared dataframe.
        """
        try:
            prepare_df = df.copy()

            # map the dataframe
            if self.mapping is not None:
                for old_name, new_name in self.mapping.items():
                    if old_name not in prepare_df.columns:
                        raise ValueError(f"column '{old_name}' not found in the df.")
                    prepare_df = prepare_df.rename(columns={old_name: new_name})

            # select the column to keep or drop extra columns
            if self.columns is not None and len(self.columns) > 0:
                prepare_df = prepare_df[self.columns]
            elif self.drops is not None and len(self.drops) > 0:
                prepare_df = prepare_df.drop(columns=self.drops)

            return prepare_df
        except Exception as e:
            raise RuntimeError(f'not able to prepare your dataframe following Pipeline I/O directives {e}')

    @classmethod
    def from_obj(cls, obj):
        """
        convert a str, dict or PipelineIO to a PipelineIO
        """
        if isinstance(obj, PipelineIO):
            return obj
        elif isinstance(obj, dict):
            pipeline_io = PipelineIO()
            pipeline_io.from_json(obj)
            return pipeline_io
        elif isinstance(obj, str):
            pipeline_io = PipelineIO(dataframe=obj)
            return pipeline_io
        else:
            raise TypeError(f'unsupported input type for a Pipeline I/O : {obj.__class__.__name__}')

    @classmethod
    def from_list(cls, obj_list: list) -> list:
        """
        get a list of Pipeline I/O from list containing Pipeline I/O, dict or str.
        :param obj_list: list to convert
        :return: list of Pipeline I/O
        """
        pipeline_io_list = []
        for obj in obj_list:
            pipeline_io_list.append(cls.from_obj(obj))
        return pipeline_io_list


class PipelineStep(ApiDto):
    """
    step of a pipeline.
    :ivar uuid.UUID step_id: id of pipeline step.
    :ivar wizata_dsapi.StepType step_type: step type.
    :ivar config: step configuration; request, script_config, model_config, ...
    :ivar inputs: list of wizata_dsapi.PipelineIO
    :ivar outputs: list of wizata_dsapi.PipelineIO
    """

    def __init__(self,
                 step_id: uuid.UUID = None,
                 step_type: StepType = None,
                 config=None,
                 inputs=None,
                 outputs=None):

        if outputs is None:
            outputs = []
        if inputs is None:
            inputs = []
        if step_id is None:
            step_id = uuid.uuid4()
        self.step_id = step_id
        self.step_type = step_type
        self.config = config
        self.inputs = inputs
        self.outputs = outputs

    def from_json(self, obj):
        if "id" in obj.keys():
            self.step_id = uuid.UUID(obj["id"])

        if "type" in obj.keys():
            self.step_type = StepType(obj["type"])
        else:
            raise TypeError(f'pipeline step must have a type.')
        if "config" in obj.keys():
            if self.step_type == StepType.SCRIPT:
                self.config = ScriptConfig()
                self.config.from_json(obj['config'])
            elif self.step_type == StepType.QUERY:
                self.config = Request()
                self.config.from_json(obj['config'])
            elif self.step_type == StepType.WRITE:
                self.config = WriteConfig()
                self.config.from_json(obj['config'])
            elif self.step_type == StepType.MODEL:
                self.config = MLModelConfig()
                self.config.from_json(obj['config'])
            elif self.step_type == StepType.PLOT:
                self.config = ScriptConfig()
                self.config.from_json(obj['config'])
            else:
                self.config = obj['config']
        self.inputs = []
        if "inputs" in obj.keys():
            self.inputs = PipelineIO.from_list(obj["inputs"])

        self.outputs = []
        if "outputs" in obj.keys():
            self.outputs = PipelineIO.from_list(obj["outputs"])

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.step_id)
        }
        if self.step_type is not None:
            obj["type"] = str(self.step_type.value)
        if self.config is not None:
            if self.step_type == StepType.SCRIPT:
                obj["config"] = self.config.to_json()
            elif self.step_type == StepType.QUERY:
                obj["config"] = self.config.to_json()
            elif self.step_type == StepType.WRITE:
                obj["config"] = self.config.to_json()
            elif self.step_type == StepType.MODEL:
                obj["config"] = self.config.to_json()
            elif self.step_type == StepType.PLOT:
                obj["config"] = self.config.to_json()
            else:
                obj["config"] = self.config

        if self.inputs is not None:
            obj["inputs"] = []
            pipeline_io: PipelineIO
            for pipeline_io in self.get_inputs():
                obj["inputs"].append(pipeline_io.to_json())

        if self.outputs is not None:
            obj["outputs"] = []
            pipeline_io: PipelineIO
            for pipeline_io in self.get_outputs():
                obj["outputs"].append(pipeline_io.to_json())

        return obj

    def get_inputs(self) -> list:
        """
        get list of inputs, verified and transformed as PipelineIO
        :return: list of PipelineIO
        """
        return PipelineIO.from_list(self.inputs)

    def get_outputs(self) -> list:
        """
        get list of inputs, verified and transformed as PipelineIO
        :return: list of PipelineIO
        """
        return PipelineIO.from_list(self.outputs)

    def inputs_names(self, f_type: str = None) -> list:
        """
        get a list str representing inputs names
        :param f_type: filter on a type
        :return: list str
        """
        names = []

        if f_type is not None and f_type != "dataframe":
            raise ValueError(f'pipeline I/O only supports dataframe.')

        input_io: PipelineIO
        for input_io in self.get_inputs():
            names.append(input_io.dataframe)

        return names

    def outputs_names(self, f_type: str = None) -> list:
        """
        get a list str representing outputs names
        :param f_type: filter on a type
        :return: list str
        """
        names = []

        if f_type is not None and f_type != "dataframe":
            raise ValueError(f'pipeline I/O only supports dataframe.')

        output_io: PipelineIO
        for output_io in self.get_outputs():
            names.append(output_io.dataframe)

        return names

    def get_unique_input(self) -> PipelineIO:
        """
        verify pipeline step as only one input and returns it, raise an error otherwise.
        """
        inputs = self.get_inputs()
        if len(inputs) != 1:
            raise ValueError(f'pipeline step {self.step_id} of type {self.step_type.value} '
                             f'does not contains one and only one input but {len(inputs)}')
        return inputs[0]

    def get_unique_output(self) -> PipelineIO:
        """
        verify pipeline step as only one output and returns it, raise an error otherwise.
        """
        outputs = self.get_outputs()
        if len(outputs) != 1:
            raise ValueError(f'pipeline step {self.step_id} of type {self.step_type.value} '
                             f'does not contains one and only one output but {len(outputs)}')
        return outputs[0]

    def get_input(self, name: str) -> PipelineIO:
        """
        get input dict based on value name.
        :param name: value name to find.
        :return: input dict
        """
        input_io: PipelineIO
        for input_io in self.get_inputs():
            if name == input_io.dataframe:
                return input_io

    def get_output(self, name: str) -> PipelineIO:
        """
        get output dict based on value name.
        :param name: value name to find.
        :return: input dict
        """
        output_io: PipelineIO
        for output_io in self.get_outputs():
            if name == output_io.dataframe:
                return output_io


class Pipeline(ApiDto):
    """
    Pipeline defines a set of steps that can be executed together.
    :ivar uuid.UUID pipeline_id: technical id of the pipeline.
    :ivar uuid.UUID experiment_id: technical id of the experiment linked to the pipeline.
    :ivar str key: logical string unique id of the pipeline.
    :ivar list steps: list of steps connected between by their inputs and outputs.
    :ivar uuid.UUID template_id: template id associated to the pipeline.
    :ivar dict variables: dictionary of variable name with they wizata_dsapi.VarType.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "pipelines"

    @classmethod
    def from_dict(cls, data):
        obj = Pipeline()
        obj.from_json(data)
        return obj

    def __init__(self,
                 pipeline_id: uuid.UUID = None,
                 key: str = None,
                 variables: dict = None,
                 steps: list = None,
                 plots: list = None,
                 template_id: uuid.UUID = None,
                 experiment_id: uuid.UUID = None):

        if pipeline_id is None:
            pipeline_id = uuid.uuid4()
        self.pipeline_id = pipeline_id
        self.key = key
        if variables is None:
            variables = {}
        self.variables = variables
        self.template_id = template_id
        self.experiment_id = experiment_id
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None
        self.plots = plots
        if plots is None:
            self.plots = []
        if steps is not None:
            for step in steps:
                if not isinstance(step, PipelineStep):
                    raise TypeError(f'step expected PipelineStep but received {step.__class__.__name__}')
            self.steps = steps
        else:
            self.steps = []

        # related entities
        self.template = None
        self.twins = {}

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

    def check_path(self) -> bool:
        """
        validate that steps create a valid path.
        return true if path is valid, otherwise raise errors
        """

        followed = []  # all steps already followed
        produced = []  # all outputs already produced

        steps_to_follow = self._next_steps(followed, produced)
        if len(steps_to_follow) == 0:
            raise ValueError('path does not contains any initial steps producing outputs')

        while len(steps_to_follow) > 0:
            for step in steps_to_follow:
                self._follow_step(step, followed, produced)
            steps_to_follow = []
            if len(followed) < len(self.steps):
                steps_to_follow = self._next_steps(followed, produced)

        if len(followed) == len(self.steps):
            return True
        else:
            raise RuntimeError(f'missing {len(self.steps)-len(followed)} step(s) that could not be followed')

    def _follow_step(self,
                     step: PipelineStep,
                     followed: list,
                     produced: list):
        """
        simulate that step have been followed.
        """
        if step in followed:
            raise RuntimeError(f'path cannot pass two times through same step {step.step_id}')
        followed.append(step)
        if step.step_type == StepType.QUERY and len(step.outputs) != 1:
            raise RuntimeError(f'query step must have exactly one output and be of type dataframe')
        if step.step_type == StepType.WRITE and (len(step.inputs) != 1 or len(step.outputs) > 0):
            raise RuntimeError(f'write step must have exactly one input and no outputs')
        for output in step.outputs_names():
            if output in produced:
                raise RuntimeError(f'output {output} is already produced.')
            produced.append(output)

    def _next_steps(self, followed, produced):
        """
        find all next steps that are ready to be executed
        """
        next_steps = []
        step: PipelineStep
        for step in self.steps:
            if all(s_input in produced for s_input in step.inputs_names()) and step not in followed:
                next_steps.append(step)
        return next_steps

    def add_query(self,
                  request: Request,
                  df_name: str = "query_df",
                  use_template: bool = True,
                  output_df: PipelineIO = None):
        """
        add a query step
        :param request: request definition to add.
        :param df_name: output name ot use for the dataframe - use df_output for more features.
        :param output_df: output df - can set a mapping.
        :param use_template: by default, if pipeline is link to a template, the query will be too. set to false to disable forcing it.
        """
        if request is None:
            raise ValueError('please provide a request.')

        if use_template and self.template_id is not None:
            request.select_template(template_id=self.template_id)

        step = PipelineStep()
        step.step_type = StepType.QUERY
        step.config = request

        if output_df is None:
            if df_name is None:
                raise ValueError('please name the output')
            step.outputs.append(PipelineIO(dataframe=df_name))
        else:
            if output_df.dataframe is None:
                raise ValueError('please set a dataframe name on output')
            step.outputs.append(output_df)

        self.steps.append(step)

    def add_transformation(self,
                           script,
                           inputs: list = None,
                           outputs: list = None,
                           input_df_names: list = None,
                           output_df_names: list = None):
        """
        add a transformation script
        :param script: name, Script or ScriptConfig.
        :param inputs: list of Pipeline I/O or dict or str for dataframe input names.
        :param outputs: list of Pipeline I/O or dict or str for dataframe output names.
        :param input_df_names: deprecated support.
        :param output_df_names: deprecated support.
        """
        step = PipelineStep()
        step.step_type = StepType.SCRIPT

        # Script Config
        if script is None:
            raise ValueError('please provide a script.')
        if isinstance(script, str):
            step.config = ScriptConfig(function=script)
        elif isinstance(script, ScriptConfig):
            step.config = script
        elif isinstance(script, Script):
            name = script.name
            if name is None:
                raise ValueError('please fetch your script or set a function name directly')
            step.config = ScriptConfig(function=name)
        else:
            raise TypeError(f'unsupported type of script {script.__class__.__name__}')

        # Inputs / Outputs

        # deprecated support - to remove 10.6/11.0
        if input_df_names is not None:
            inputs = input_df_names
        if output_df_names is not None:
            outputs = output_df_names

        if inputs is not None:
            step.inputs = PipelineIO.from_list(inputs)
        if outputs is not None:
            step.outputs = PipelineIO.from_list(outputs)

        # append
        self.steps.append(step)

    def add_model(self, config: MLModelConfig, input_df, output_df=None):
        """
        add a model step
        :param config: model configuration to define how pipeline should train and use your model.
        :param input_df: str, dict or Pipeline I/O defining input dataframe properties
        :param output_df: str, dict or Pipeline I/O defining input dataframe properties
        """
        step = PipelineStep()
        step.step_type = StepType.MODEL

        if config is None:
            raise ValueError('please provide a config.')
        if not isinstance(config, MLModelConfig):
            raise ValueError('please provide a config.')
        step.config = config

        if input_df is None:
            raise ValueError('please provide a input_df str, dict or PipelineIO')
        step.inputs.append(PipelineIO.from_obj(input_df))

        if output_df is not None:
            step.outputs.append(PipelineIO.from_obj(output_df))

        if step.config.model_key is None:
            if self.key is None:
                raise ValueError("please set a model_key in config or a pipeline key")
            step.config.model_key = self.key

        self.steps.append(step)

    def add_writer(self,
                   config: WriteConfig,
                   input_df):
        """
        add a writer step
        :param config: writer configuration to define how pipeline should write data into platform.
        :param input_df: str, dict or Pipeline I/O defining input dataframe properties
        """

        if config is None:
            raise ValueError('please provide a config.')
        if input_df is None:
            raise ValueError('please provide a input_df name.')

        step = PipelineStep()
        step.step_type = StepType.WRITE

        if input_df is None:
            raise ValueError('please provide a input_df str, dict or PipelineIO')
        step.inputs.append(PipelineIO.from_obj(input_df))

        step.config = config
        self.steps.append(step)

    def add_plot(self,
                 script,
                 df_name: str = None,
                 input_df: PipelineIO = None):
        """
        add a writer step
        :param script: script configuration to define how pipeline should execute the plot script.
        :param df_name: str deprecated usage
        :param input_df: str, dict or Pipeline I/O defining input dataframe properties
        """

        step = PipelineStep()
        step.step_type = StepType.PLOT

        if script is None:
            raise ValueError('please provide a script.')
        if isinstance(script, str):
            step.config = ScriptConfig(function=script)
        elif isinstance(script, ScriptConfig):
            step.config = script
        elif isinstance(script, Script):
            name = script.name
            if name is None:
                raise ValueError('please fetch your script or set a function name directly')
            step.config = ScriptConfig(function=name)
        else:
            raise TypeError(f'unsupported type of script {script.__class__.__name__}')

        if input_df is None:
            if df_name is None:
                raise ValueError('please name the output')
            step.inputs.append(PipelineIO(dataframe=df_name))
        else:
            if input_df.dataframe is None:
                raise ValueError('please set a dataframe name on output')
            step.inputs.append(input_df)

        self.steps.append(step)

    def check_variables(self):
        """
        verify that variables dict is a valid { "name" : "VarType" } dictionary.
        """
        if self.variables is None:
            self.variables = {}
        elif not isinstance(self.variables, dict):
            raise TypeError(f'variables must be empty nor a valid dictionary')
        for key in self.variables:
            VarType(self.variables[key])

    def api_id(self) -> str:
        """
        Id of the pipeline

        :return: string formatted UUID of the Pipeline.
        """
        return str(self.pipeline_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate pipeline.
        :return: Endpoint name.
        """
        return "Pipelines"

    def from_json(self, obj):
        """
        load from JSON dictionary representation
        """
        if "id" in obj.keys():
            self.pipeline_id = uuid.UUID(obj["id"])
        if "key" in obj.keys():
            self.key = str(obj['key'])
        if "id" not in obj.keys() and "key" not in obj.keys():
            raise KeyError("at least id or key must be set on a pipeline")
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
        if "experimentKey" in obj.keys() and obj["experimentKey"] is not None:
            self.experiment_id = uuid.UUID(obj["experimentKey"])
        if "variables" in obj.keys():
            if isinstance(obj["variables"], str):
                self.variables = json.loads(obj["variables"])
            else:
                self.variables = obj["variables"]
            if self.variables is not None or not isinstance(self.variables, dict):
                if isinstance(self.variables, list) and len(self.variables) == 0:
                    self.variables = {}
            self.check_variables()
        if "steps" in obj.keys():
            if isinstance(obj["steps"], str):
                steps = json.loads(obj["steps"])
            else:
                steps = obj["steps"]
            for obj_step in steps:
                step = PipelineStep()
                step.from_json(obj_step)
                self.steps.append(step)
        if "plots" in obj.keys():
            if isinstance(obj["plots"], str):
                self.plots = json.loads(obj["plots"])
            else:
                self.plots = obj["plots"]
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

    def to_json(self, target: str = None):
        """
        Convert to a json version of Execution definition.
        By default, use DS API format.
        """
        obj = {
            "id": str(self.pipeline_id)
        }
        if self.key is not None:
            obj["key"] = self.key
        if self.steps is not None:
            obj_steps = []
            step: PipelineStep
            for step in self.steps:
                obj_steps.append(step.to_json())
            obj["steps"] = json.dumps(obj_steps)
        if self.plots is not None:
            obj["plots"] = json.dumps(self.plots)
        if self.variables is not None:
            self.check_variables()
            obj["variables"] = json.dumps(self.variables)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.experiment_id is not None:
            obj["experimentKey"] = str(self.experiment_id)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj

    def _load_related_entities(self, obj):
        """
        load related entities from full backend payload.
        :param obj: obj to load.
        """
        if "twins" in obj and len(obj["twins"]) == 1:
            twin_data = obj["twins"][0]
            twin_objects = {}
            twin_id = None
            if "twin" in twin_data and twin_data["twin"] is not None:
                twin_objects["twin"] = Twin()
                twin_objects["twin"].from_json(twin_data["twin"])
                twin_id = twin_objects["twin"].twin_id
            if "twinRegistration" in twin_data and twin_data["twinRegistration"] is not None:
                twin_objects["registration"] = TwinRegistration()
                twin_objects["registration"].from_json(twin_data["twinRegistration"])
                twin_id = twin_objects["registration"].twin_id
            if twin_id is not None:
                self.twins[str(twin_id)] = twin_objects
        if "template" in obj:
            self.template = Template()
            self.template.from_json(obj["template"])

    def get_model_configs(self) -> list[MLModelConfig]:
        """
        get all model configs present in this pipeline.
        :return: list of MLModelConfig
        """
        configs = []
        step: wizata_dsapi.PipelineStep
        for step in self.steps:
            if step.step_type == wizata_dsapi.StepType.MODEL:
                config: wizata_dsapi.MLModelConfig = step.config
                configs.append(config)
        return configs
