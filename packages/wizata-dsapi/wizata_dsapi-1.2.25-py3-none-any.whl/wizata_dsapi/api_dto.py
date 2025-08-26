import uuid
from enum import Enum


class VarType(Enum):
    """
    defines possible type for a defined variable.
        - "string" text sequence of characters
        - "integer" signed 64-bit integer
        - "datetime" static datetime or timestamp (UTC)
        - "relative" relative datetime using "now+-?yMwdmsms" format (e.g. 'now-7d')
        - "datapoint" hardware id, uuid or wizata_dsapi.DataPoint defining a datapoint
        - "float" floating-point decimal number
        - "json" complex object defined as a serializable JSON document.
    """
    STRING = "string"
    INTEGER = "integer"
    DATETIME = "datetime"
    RELATIVE = "relative"
    DATAPOINT = "datapoint"
    FLOAT = "float"
    JSON = "json"


class ApiDto:

    def api_id(self) -> str:
        """
        return current object id on Web API format.
        """
        pass

    def endpoint(self) -> str:
        """
        return endpoint name used to contact backend.
        """
        pass

    def to_json(self, target: str = None):
        """
        transform current object into a dict that could be JSONIFY.
        :target: by default - None. Can be 'backend-create' or 'backend-update' in order to JSONIFY only backend fields.
        :return: dumpable dict.
        """
        pass

    def from_json(self, obj):
        """
        load the object from a dict originating of a JSON format.
        :param obj: object to load information from.
        """
        pass

    def set_id(self, id_value):
        """
        specify the id_value neutrally
        :param id_value:
        :return:
        """
        pass

    @classmethod
    def route(cls):
        """
        Endpoint name in Web API (v0.4+).
        """
        pass

    @classmethod
    def from_dict(cls, data):
        """
        Init object instance from dict (v0.4+)
        """
        pass

    @classmethod
    def get_type(cls):
        """
        Return type of get format json by default - override with either pickle, dill, ...
        """
        return "json"

    @classmethod
    def get_id_type(cls) -> type:
        """
        return type of the id format, by default UUID but some are overridden integer.
        """
        return uuid.UUID
