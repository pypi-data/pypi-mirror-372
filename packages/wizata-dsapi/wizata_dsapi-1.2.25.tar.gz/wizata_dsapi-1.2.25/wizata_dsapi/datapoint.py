import uuid
from enum import Enum
from .api_dto import ApiDto
from .datastore import DataStore
import json


class Category(ApiDto):
    """
    Category groups unit into what they represent.
    e.g. Temperature, Distance, Speed, Pressure, ...
    :ivar uuid.UUID category_id: Technical id of the category.
    :ivar str name: Category name.
    """

    def __init__(self,
                 category_id: uuid.UUID = None,
                 name: str = None):
        if category_id is None:
            self.category_id = uuid.uuid4()
        else:
            self.category_id = category_id
        self.name = name
        self.units = []

    def api_id(self) -> str:
        return str(self.category_id).upper()

    def endpoint(self) -> str:
        return "Categories"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.category_id = uuid.UUID(obj["id"])

        if "name" in obj.keys():
            self.name = obj["name"]

    def to_json(self):
        obj = {
            "id": str(self.category_id)
        }
        if self.name is not None and self.name != '':
            obj["name"] = self.name
        return obj


class Label(ApiDto):
    """
    Label is a custom tag defining a time-series value.
    :ivar uuid.UUID label_id: Technical id of the label.
    :ivar str name: Label name.
    """

    def __init__(self,
                 label_id: uuid.UUID = None,
                 name: str = None):
        if label_id is None:
            self.label_id = uuid.uuid4()
        else:
            self.label_id = label_id
        self.name = name

    def api_id(self) -> str:
        return str(self.label_id).upper()

    def endpoint(self) -> str:
        return "Labels"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.label_id = uuid.UUID(obj["id"])

        if "name" in obj.keys():
            self.name = obj["name"]

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.label_id)
        }
        if self.name is not None and self.name != '':
            obj["name"] = self.name
        return obj


class Unit(ApiDto):
    """
    Unit defines how a time-series value is expressed.
    :ivar uuid.UUID unit_id: Technical id of the unit.
    :ivar str short_name: Short Display Name of the unit.
    """

    def __init__(self,
                 unit_id: uuid.UUID = None,
                 symbol: str = None,
                 short_name: str = None,
                 full_name: str = None,
                 category_id: uuid.UUID = None,
                 is_canonical: bool = False,
                 from_canonical: str = None,
                 to_canonical: str = None):
        if unit_id is None:
            self.unit_id = uuid.uuid4()
        else:
            self.unit_id = unit_id
        self.symbol = symbol
        self.short_name = short_name
        self.full_name = full_name
        self.category_id = category_id
        self.is_canonical = is_canonical
        self.from_canonical = from_canonical
        self.to_canonical = to_canonical

    def api_id(self) -> str:
        return str(self.unit_id).upper()

    def endpoint(self) -> str:
        return "Units"

    def from_json(self, obj):
        """
        Load the datapoint entity from a dictionary.

        :param obj: Dict version of the datapoint.
        """
        if "id" in obj.keys():
            self.unit_id = uuid.UUID(obj["id"])
        if "symbol" in obj.keys():
            self.symbol = obj["symbol"]
        if "shortName" in obj.keys() and obj["shortName"] is not None:
            self.short_name = obj["shortName"]
        if "fullName" in obj.keys() and obj["fullName"] is not None:
            self.full_name = obj["fullName"]
        if "isCanonical" in obj.keys() and obj["isCanonical"] is not None:
            self.is_canonical = obj["isCanonical"]
        if "categoryId" in obj.keys() and obj["categoryId"] is not None:
            self.category_id = uuid.UUID(obj["categoryId"])
        if "fromCanonical" in obj.keys() and obj["fromCanonical"] is not None:
            self.from_canonical = obj["fromCanonical"]
        if "toCanonical" in obj.keys() and obj["toCanonical"] is not None:
            self.to_canonical = obj["toCanonical"]

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.unit_id),
            "isCanonical": self.is_canonical
        }
        if self.symbol is not None and self.symbol != '':
            obj["symbol"] = self.symbol
        if self.short_name is not None and self.short_name != '':
            obj["shortName"] = self.short_name
        if self.short_name is not None and self.short_name != '':
            obj["fullName"] = self.full_name
        if self.category_id is not None:
            obj["categoryId"] = str(self.category_id)
        if self.from_canonical is not None and self.from_canonical != '':
            obj["fromCanonical"] = self.from_canonical
        else:
            obj["fromCanonical"] = None
        if self.to_canonical is not None and self.to_canonical != '':
            obj["toCanonical"] = self.to_canonical
        else:
            obj["toCanonical"] = None
        return obj


class BusinessType(Enum):
    """
    BusinessType represents business usage of a datapoint, enumeration:
        - "telemetry" represents a time-series emitted by a hardware device as an information (one direction).
        - "setPoint" is used for time-series signals bidirectional used to set hardware configuration.
        - "logical" represents a time-series calculated from others or third-party solution.
        - "measurement" represents a logical time-series manually inputted by a human.
        - "event" represents a state or probability that have a start and stop timestamp.
        - "text" represents a time-series emitted as text/string value.
    """
    TELEMETRY = "telemetry"
    SET_POINTS = "setPoint"
    LOGICAL = "logical"
    MEASUREMENT = "measurement"
    EVENT = "event"
    TEXT = "text"


class InputModeType(Enum):
    """
    InputModeType defines authorization or not to write value on a time-series datapoint.
        - "none" datapoint cannot be written from Wizata.
        - "manual" datapoint can be written by a human.
        - "automatic" datapoint can only be written through automatic computation.
        - "manualAndAutomatic" authorize both manual and automatic.
    """
    NONE = "none"
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    MANUAL_AND_AUTOMATIC = "manualAndAutomatic"


class DataPoint(ApiDto):
    """
    A datapoint reference a time-series tag stored on DB.

    :ivar uuid.UUID datapoint_id: Unique datapoint identifier (technical id).
    :ivar str hardware_id: The unique datapoint logical hardware id corresponding to time-series tag name.
    :ivar wizata_dsapi.BusinessType business_type: Business type of a datapoint defining usage.
    :ivar str name: Display name used in the user interface.
    :ivar uuid.UUID twin_id: Set parent twin id on which datapoint is attached.
    :ivar uuid.UUID unit_id: Unit on which the time-series is expressed (e.g. Celsius Degree).
    :ivar uuid.UUID category_id: Defines the Unit category (e.g Temperature).
    :ivar str description: Additional information to help user understand the datapoint.
    :ivar float min_value: Set manufacturer specification for hardware logical minimum values.
    :ivar float max_value: Set manufacturer specification for hardware logical maximum values.
    :ivar int frequency: Set frequency in milliseconds at which this data point should theoretically emit data.
    :ivar wizata_dsapi.InputModeType input_mode: Set if time-series can or not be manually/automatically written in Wizata.
    :ivar dict extra_properties: Add any custom properties to your datapoints as a key/value pair dictionary.
    """

    @classmethod
    def route(cls):
        return "datapoints"

    @classmethod
    def from_dict(cls, data):
        obj = DataPoint()
        obj.from_json(data)
        return obj

    def __init__(self,
                 datapoint_id: uuid.UUID = None,
                 hardware_id: str = None,
                 business_type: BusinessType = None,
                 name: str = None,
                 twin_id: uuid.UUID = None,
                 unit_id: uuid.UUID = None,
                 category_id: uuid.UUID = None,
                 description: str = None,
                 min_value: float = None,
                 max_value: float = None,
                 frequency: int = None,
                 input_mode: InputModeType = None,
                 extra_properties: dict = None,
                 group_system_id: int = None,
                 data_store_id: int = None):
        if datapoint_id is None:
            self.datapoint_id = uuid.uuid4()
        else:
            self.datapoint_id = datapoint_id
        self.hardware_id = hardware_id
        self.name = name
        self.business_type = business_type
        self.twin_id = twin_id
        self.unit_id = unit_id
        self.category_id = category_id
        self.description = description
        self.min_value = min_value
        self.max_value = max_value
        self.frequency = frequency
        self.input_mode = input_mode
        self.extra_properties = extra_properties
        self.group_system_id = group_system_id
        self.data_store_id = data_store_id
        self.data_store = None

    def api_id(self) -> str:
        """
        formatted id of the datapoint (datapoint_id)
        :return: string formatted UUID of the DataPoint.
        """
        return str(self.datapoint_id).upper()

    def endpoint(self) -> str:
        """
        endpoint name used to manipulate datapoint on backend.
        :return: endpoint name.
        """
        return "DataPoints"

    def from_json(self, obj):
        """
        load the datapoint entity from a dictionary.
        :param obj: dict version of the datapoint.
        """
        if "id" in obj.keys():
            self.datapoint_id = uuid.UUID(obj["id"])

        if "hardwareId" in obj.keys():
            self.hardware_id = obj["hardwareId"]

        if "name" in obj.keys():
            self.name = obj["name"]

        if "businessType" in obj.keys():
            self.business_type = BusinessType(str(obj["businessType"]))

        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])

        if "unitId" in obj.keys() and obj["unitId"] is not None:
            self.unit_id = uuid.UUID(obj["unitId"])

        if "categoryId" in obj.keys() and obj["categoryId"] is not None:
            self.category_id = uuid.UUID(obj["categoryId"])

        if "description" in obj.keys() and obj["description"] is not None:
            self.description = obj["description"]

        if "minValue" in obj.keys() and obj["minValue"] is not None:
            self.min_value = float(obj["minValue"])

        if "maxValue" in obj.keys() and obj["maxValue"] is not None:
            self.max_value = float(obj["maxValue"])

        if "frequency" in obj.keys() and obj["frequency"] is not None:
            self.frequency = int(obj["frequency"])

        if "inputMode" in obj.keys():
            self.input_mode = InputModeType(str(obj["inputMode"]))

        if "extraProperties" in obj.keys():
            if isinstance(obj["extraProperties"], str):
                self.extra_properties = json.loads(obj["extraProperties"])
            else:
                self.extra_properties = obj["extraProperties"]

        if "groupSystemId" in obj.keys() and obj["groupSystemId"] is not None:
            self.group_system_id = int(obj["groupSystemId"])

        if "dataStoreId" in obj.keys() and obj["dataStoreId"] is not None:
            self.data_store_id = int(obj["dataStoreId"])

        if "dataStore" in obj.keys() and obj["dataStore"] is not None:
            self.data_store = DataStore.from_dict(obj["dataStore"])
            self.data_store_id = self.data_store.data_store_id

    def to_json(self, target: str = None):
        """
        convert the datapoint to a dictionary compatible with JSON format.
        :return: dictionary representation of the datapoint object.
        """
        obj = {
            "id": str(self.datapoint_id),
            "hardwareId": str(self.hardware_id)
        }
        if self.business_type is not None and isinstance(self.business_type, BusinessType):
            obj["businessType"] = self.business_type.value
        if self.input_mode is not None and isinstance(self.input_mode, InputModeType):
            obj["inputMode"] = self.input_mode.value
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)
        if self.unit_id is not None:
            obj["unitId"] = str(self.unit_id)
        if self.category_id is not None:
            obj["categoryId"] = str(self.category_id)
        if self.description is not None and self.description != "":
            obj["description"] = self.description
        if self.name is not None and self.name != "":
            obj["name"] = self.name
        if self.max_value is not None:
            obj["maxValue"] = self.max_value
        if self.min_value is not None:
            obj["minValue"] = self.min_value
        if self.frequency is not None:
            obj["frequency"] = self.frequency
        if self.extra_properties is not None:
            if not isinstance(self.extra_properties, dict):
                raise ValueError('on datapoint extra properties must be None or a JSON serializable dict')
            obj["extraProperties"] = json.dumps(self.extra_properties)
        if self.group_system_id is not None:
            obj["groupSystemId"] = int(self.group_system_id)
        if self.data_store_id is not None:
            obj["dataStoreId"] = int(self.data_store_id)
        return obj

    def copy(self):
        new_dp = DataPoint(datapoint_id=self.datapoint_id)
        new_dp.hardware_id = self.hardware_id
        new_dp.name = self.name
        new_dp.twin_id = self.twin_id
        new_dp.unit_id = self.unit_id
        new_dp.description = self.description
        new_dp.input_mode = self.input_mode
        new_dp.max_value = self.max_value
        new_dp.min_value = self.min_value
        new_dp.extra_properties = self.extra_properties
        new_dp.frequency = self.frequency
        new_dp.category_id = self.category_id
        new_dp.business_type = self.business_type
        new_dp.group_system_id = self.group_system_id
        new_dp.data_store_id = self.data_store_id
        return new_dp
