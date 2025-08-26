import json
import uuid

import dill
import os
import types
from .api_dto import ApiDto
import inspect
from collections import OrderedDict


def get_imports(line) -> dict:
    keywords = []
    for item in line.split(' '):
        keywords.extend(item.split(','))
    keywords[:] = [x for x in keywords if x]

    if len(keywords) <= 1:
        return {}

    i = 0
    current_key = None
    definition = {}
    while i < len(keywords):
        word = keywords[i]
        if word in ['from', 'as', 'import']:
            current_key = word
        elif current_key is not None:
            if current_key not in definition or definition[current_key] is None:
                definition[current_key] = [word]
            else:
                definition[current_key].append(word)
        else:
            raise ValueError(f'{line} cannot be parsed for possible import.')
        i = i+1

    return definition


class ScriptConfig(ApiDto):
    """
    a script config defines execution properties for a specific script.
    usually to define how a pipeline should call your script.

    :ivar str function: name of function referencing the script.
    :ivar dict properties: specific properties to configure the script.
    :ivar dict properties_mapping: mapping used to rename properties from context to script expected name.
    """

    def __init__(self,
                 function=None,
                 library=None,
                 properties_mapping=None,
                 properties: dict = None):
        self.function = function
        self.library = library
        self.properties = properties
        self.properties_mapping = properties_mapping

    def from_json(self, obj):
        if isinstance(obj, str):
            self.function = obj
            return
        else:
            if "function" in obj:
                self.function = obj["function"]
            if "library" in obj:
                self.library = obj["library"]
            elif "script" in obj:
                self.function = obj["script"]
            if "properties" in obj:
                self.properties = obj["properties"]
            if "properties_mapping" in obj:
                self.properties_mapping = obj["properties_mapping"]

    def to_json(self, target: str = None):
        obj = {
            "function": self.function
        }
        if self.library is not None:
            obj["library"] = self.library
        if self.properties is not None and isinstance(self.properties, dict):
            obj["properties"] = self.properties
        if self.properties_mapping is not None and isinstance(self.properties_mapping, dict):
            obj["properties_mapping"] = self.properties_mapping
        return obj


class Script(ApiDto):
    """
    a piece of python code that can either transform data, generate plot, train Machine Learning models.

    :ivar uuid.UUID script_id: technical id of the script
    :ivar str name: name of your script function, same as the code object.
    :ivar str description: provide an insight-full description of what does your script.
    :ivar callable() function: your function as a callable function - 'your function without ()'.
    :ivar str source: source code extracted from your source file.
    """

    @classmethod
    def route(cls):
        return "scripts"

    @classmethod
    def from_dict(cls, data):
        obj = Script()
        obj.from_json(data)
        return obj

    @classmethod
    def get_type(cls):
        return "dill"

    def __init__(self, script_id=None, description=None, function=None,
                 exact_names=False, exact_numbers=False):

        # Id
        if script_id is None:
            script_id = uuid.uuid4()
        self.script_id = script_id
        self._name = None

        # Properties
        self.description = description
        self.needExactColumnNumbers = exact_numbers
        self.needExactColumnNames = exact_names

        # Validation Properties
        self.canGeneratePlot = False
        self.canGenerateModel = False
        self.canGenerateData = False
        self.status = "draft"
        self.inputColumns = []
        self.outputColumns = []

        # Source code property
        self.source = None

        # Function properties (code)
        self.function = None
        if function is not None:
            self.copy(function)

    @property
    def name(self):
        """
        Name of the function
        :return: name of the function
        """
        return self._name

    def api_id(self) -> str:
        """
        Id of the script (script_id)

        :return: string formatted UUID of the script.
        """
        return str(self.script_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate scripts.
        :return: Endpoint name.
        """
        return "Scripts"

    def to_json(self, target: str = None):
        """
        Convert the script to a dictionary compatible to JSON format.

        :return: dictionary representation of the Script object.
        """
        obj = {
            "id": str(self.script_id),
            "canGeneratePlot": str(self.canGeneratePlot),
            "canGenerateModel": str(self.canGenerateModel),
            "canGenerateData": str(self.canGenerateData),
            "status": str(self.status),
            "needExactColumnNumbers": str(self.needExactColumnNumbers),
            "needExactColumnNames": str(self.needExactColumnNames),
            "inputColumns": json.dumps(list(self.inputColumns)),
            "outputColumns": json.dumps(list(self.outputColumns))
        }
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.name is not None:
            obj["description"] = str(self.description)
        return obj

    def from_json(self, obj):
        """
        Load the Script entity from a dictionary representation of the Script.

        :param obj: Dict version of the Script.
        """
        if "id" in obj.keys():
            self.script_id = uuid.UUID(obj["id"])
        if "name" in obj.keys():
            self._name = obj["name"]
        if "description" in obj.keys():
            if obj["description"] != "None":
                self.description = obj["description"]
        if "canGeneratePlot" in obj.keys():
            if isinstance(obj["canGeneratePlot"], str) and obj["canGeneratePlot"].lower() == "false":
                self.canGeneratePlot = False
            else:
                self.canGeneratePlot = bool(obj["canGeneratePlot"])
        if "canGenerateModel" in obj.keys():
            if isinstance(obj["canGenerateModel"], str) and obj["canGenerateModel"].lower() == "false":
                self.canGenerateModel = False
            else:
                self.canGenerateModel = bool(obj["canGenerateModel"])
        if "canGenerateData" in obj.keys():
            if isinstance(obj["canGenerateData"], str) and obj["canGenerateData"].lower() == "false":
                self.canGenerateData = False
            else:
                self.canGenerateData = bool(obj["canGenerateData"])
        if "status" in obj.keys():
            self.status = str(obj["status"]).lower()
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
        if "inputColumns" in obj.keys():
            if obj["inputColumns"].lower() == "false":
                self.inputColumns = False
            else:
                self.inputColumns = json.loads(obj["inputColumns"])
        if "outputColumns" in obj.keys():
            if obj["outputColumns"].lower() == "false":
                self.outputColumns = False
            else:
                self.outputColumns = json.loads(obj["outputColumns"])

    def copy(self, myfunction):
        """
        Copy your function code and decorators to a format executable by the Wizata App.
        :param myfunction: your function - pass the function itself as parameter
        """

        if myfunction.__code__.co_argcount < 1:
            raise ValueError('your function must contains at least one parameter')

        self.function = Function()

        self.function.id = myfunction.__name__
        self.function.params = inspect.signature(myfunction).parameters

        self._name = myfunction.__name__

        self.function.code = myfunction.__code__

        f_globals = myfunction.__globals__
        self.function.globals = []

        # ADD GLOBAL IMPORTS
        k_global: str
        for k_global in f_globals:

            if self._name == k_global:
                pass
            elif isinstance(myfunction.__globals__[k_global], types.ModuleType):
                module = f_globals[k_global]
                self.function.append_global(definition={
                    "var": k_global,
                    "module": str(module.__name__)
                })

            elif not k_global.startswith('__') and not k_global.startswith('@') and not k_global.startswith('_'):
                obj = f_globals[k_global]
                if callable(obj) and hasattr(obj, '__module__'):
                    definition = {
                        "var": k_global,
                        'module': obj.__module__
                    }
                    if hasattr(obj, '__name__'):
                        definition['class'] = obj.__name__
                    self.function.append_global(definition)

        # ADD LOCAL IMPORTS
        for line in inspect.getsourcelines(myfunction)[0]:
            line = line.strip()
            if line.startswith("from ") or line.startswith("import "):
                imports = get_imports(line)
                if 'import' not in imports:
                    raise ValueError(f'from/import statement missing import {line}')

                if 'from' in imports:
                    if len(imports['from']) != 1:
                        raise ValueError(f'unsupported multiple from statement {line}')
                    if 'as' in imports:
                        if len(imports["import"]) != 1:
                            raise ValueError(f'unsupported multiple import statement with as {line}')
                        self.function.append_global({
                            'module': imports['from'][0],
                            'class': imports['import'][0],
                            'var': imports['as'][0]
                        })
                    else:
                        for import_class in imports['import']:
                            self.function.append_global({
                                'module': imports['from'][0],
                                'class': import_class,
                                'var': import_class
                            })
                else:
                    if 'as' in imports:
                        if len(imports["import"]) != 1:
                            raise ValueError(f'unsupported multiple import statement with as {line}')
                        self.function.append_global({
                            'module': imports['import'][0],
                            'var': imports['as'][0]
                        })
                    else:
                        for import_class in imports['import']:
                            self.function.append_global({
                                'module': import_class,
                                'var': import_class
                            })

        if myfunction.__code__.co_filename is not None:
            if os.path.exists(myfunction.__code__.co_filename):
                with open(myfunction.__code__.co_filename, "r") as f:
                    source_code = f.read()
                self.source = source_code


class Function:
    """
    Python Code Function

    :ivar id: technical name and then id of the function
    :ivar code: code of the function __code__
    :ivar globals: modules references __globals__
    """

    def __init__(self):
        self.id = None
        self.code = None
        self.globals = None
        self.params = OrderedDict()

    def append_global(self, definition: dict):
        exclusion_list = [
            '__main__',
            'IPython.core.interactiveshell',
            'IPython.core.autocall'
        ]
        if 'module' in definition and definition['module'] not in exclusion_list:
            self.globals.append(definition)


