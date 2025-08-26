import uuid
from enum import Enum
from .api_dto import ApiDto
import json


class Insight(ApiDto):
    """
    An insight defines how display live data on control panel tiles.

    :ivar str name: Name of the insight displayed on the tile.
    """

    VALID_TYPES = {'lte', 'gte', 'gt', 'lt', 'eq', 'neq'}
    SEVERITY_RANGE = range(4)

    @classmethod
    def route(cls):
        return "insights"

    @classmethod
    def from_dict(cls, data):
        obj = Insight()
        obj.from_json(data)
        return obj

    def __init__(self,
                 insight_id: uuid.UUID = None,
                 name: str = None,
                 display_precision: int = 0,
                 component_id: uuid.UUID = None,
                 twin_id: uuid.UUID = None,
                 datapoint_id: uuid.UUID = None):
        if insight_id is None:
            self.insight_id = uuid.uuid4()
        else:
            self.insight_id = insight_id
        self.name = name
        self._conditions = []
        self.display_precision = display_precision
        self.component_id = component_id
        self.twin_id = twin_id
        self.datapoint_id = datapoint_id

    def api_id(self) -> str:
        return str(self.insight_id).upper()

    def endpoint(self) -> str:
        return "Insights"

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(self, value):
        raise AttributeError(
            "Conditions list cannot be directly set. Use 'add_condition', 'update_condition', or modify an item.")

    def _validate_condition(self, condition, is_first: bool, is_last: bool):
        if not isinstance(condition, dict):
            raise ValueError("condition must be a dictionary.")

        if not all(key in condition for key in ('severity', 'name')):
            raise ValueError("condition dictionary must contain 'severity', 'name'. ")

        if not isinstance(condition['name'], str):
            raise ValueError("'name' must be a string.")

        if not isinstance(condition['severity'], int) or condition['severity'] not in self.SEVERITY_RANGE:
            raise ValueError("'severity' must be an integer between 0 and 3.")

        is_else_condition = "type" not in condition and "value" not in condition
        if is_else_condition:
            if is_first:
                raise ValueError("The 'else' condition cannot be the first condition in the list.")
            if not is_last:
                raise ValueError("The 'else' condition must be the last condition in the list.")
            if any("type" not in cond and "value" not in cond for cond in self._conditions):
                raise ValueError("Only one 'else' condition is allowed.")
        else:
            if "type" not in condition or condition['type'] is None or condition['type'] not in self.VALID_TYPES:
                raise ValueError(f"'type' must be one of {self.VALID_TYPES} if specified.")
            if "value" not in condition or condition['value'] is None or not isinstance(condition['value'], (float, int)):
                raise ValueError("'value' must be a float if specified.")

    def add_condition(self, condition):
        """
        add a condition to the conditions.
        :param condition:
        :return:
        """
        self._validate_condition(condition, (len(self._conditions) == 0), True)
        self._conditions.append(condition)

    def update_condition(self, index, condition):
        if index < 0 or index >= len(self._conditions):
            raise IndexError("Condition index out of range.")
        is_first = index == 0
        is_last = index == len(self._conditions) - 1
        self._validate_condition(condition, is_first=is_first, is_last=is_last)
        self._conditions[index] = condition

    def remove_condition(self, index):
        if index < 0 or index >= len(self._conditions):
            raise IndexError("Condition index out of range.")
        if index == 0 and len(self._conditions) == 2:
            if "type" not in self._conditions[1] and "value" not in self._conditions[1]:
                raise ValueError("You cannot pop out if condition if only remaining one will be an else")
        self._conditions.pop(index)

    def clear_conditions(self):
        self._conditions.clear()

    def from_json(self, obj):
        if "id" in obj.keys():
            self.insight_id = uuid.UUID(obj["id"])

        if "name" in obj.keys():
            self.name = obj["name"]

        if "displayPrecision" in obj.keys() and obj["displayPrecision"] is not None:
            self.display_precision = int(obj["displayPrecision"])

        if "condition" in obj.keys() and obj["condition"] is not None:
            if isinstance(obj["condition"], str):
                backend_conditions = json.loads(obj["condition"])
            else:
                backend_conditions = obj["condition"]
            if "parsed" in backend_conditions:
                for backend_condition in backend_conditions["parsed"]:
                    self._conditions.append(backend_condition)

        if "componentId" in obj.keys() and obj["componentId"] is not None:
            self.component_id = uuid.UUID(obj["componentId"])

        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])

        if "sensorId" in obj.keys() and obj["sensorId"] is not None:
            self.datapoint_id = uuid.UUID(obj["sensorId"])

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.insight_id),
        }

        if self.name is not None:
            obj["name"] = str(self.name)

        if self.display_precision is not None:
            obj["displayPrecision"] = int(self.display_precision)

        if self._conditions is not None:
            if not isinstance(self._conditions, list):
                raise ValueError('to_json cannot find any valid parsed_condition')
            if len(self._conditions) > 0:
                obj["condition"] = json.dumps({
                    "parsed": self._conditions
                })
            else:
                obj["condition"] = None

        if self.component_id is not None:
            obj["componentId"] = str(self.component_id)

        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)

        if self.datapoint_id is not None:
            obj["sensorId"] = str(self.datapoint_id)

        return obj
