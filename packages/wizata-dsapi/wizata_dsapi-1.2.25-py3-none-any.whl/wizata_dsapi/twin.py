import uuid
from .api_dto import ApiDto
from enum import Enum
import re
import json


def is_valid_hex_color(color):
    hex_color_pattern = r'^#([A-Fa-f0-9]{6})$'
    match = re.match(hex_color_pattern, color)
    if match is None:
        raise ValueError('color is not a proper hexadecimal color : e.g. #E64600')
    else:
        return True


class TwinType(ApiDto):
    """
    twin type
    """

    @classmethod
    def route(cls):
        return "twintypes"

    @classmethod
    def from_dict(cls, data):
        obj = TwinType()
        obj.from_json(data)
        return obj

    def __init__(self,
                 twin_type_id: uuid.UUID = None,
                 name: str = None,
                 icon: str = None,
                 color: str = None,
                 description: str = None):
        if twin_type_id is None:
            self.twin_type_id = uuid.uuid4()
        else:
            self.twin_type_id = twin_type_id
        self.name = name
        self.icon = icon
        self.color = color
        if color is not None:
            is_valid_hex_color(color)
        self.description = description
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        return str(self.twin_type_id).upper()

    def endpoint(self) -> str:
        return "TwinTypes"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.twin_type_id = uuid.UUID(obj["id"])
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "color" in obj.keys() and obj["color"] is not None:
            is_valid_hex_color(str(obj["color"]))
            self.color = str(obj["color"])
        if "icon" in obj.keys() and obj["icon"] is not None:
            self.icon = str(obj["icon"])
        if "description" in obj.keys() and obj["description"] is not None:
            self.description = str(obj["description"])
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.twin_type_id)
        }
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.color is not None:
            obj["color"] = str(self.color)
        if self.description is not None:
            obj["description"] = str(self.description)
        if self.icon is not None:
            obj["icon"] = str(self.icon)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj



class TwinBlockType(Enum):
    """
    deprecated - replaced by TwinType
    digital twin block type
        - area
        - machine
        - equipment
        - flow
    """
    AREA = "area"
    MACHINE = "machine"
    EQUIPMENT = "equipment"
    FLOW = "flow"


class Twin(ApiDto):
    """
    digital twin item representing an asset, machine, equipment.

    :ivar uuid.UUID twin_id: technical id of the twin.
    :ivar uuid.UUID hardware_id: unique str hardware id (e.g. required in template and ml models 'by_twin').
    :ivar str name: logical display name of the Asset.
    :ivar uuid.UUID parent_id: technical id of the parent twin item.
    :ivar wizata_dsapi.TwinBlockType type: type (area, machine, equipment or flow).
    :ivar float latitude: fixed latitude of the twin item.
    :ivar float longitude: fixed longitude of the twin item.
    :ivar uuid.UUID latitude_id: technical id of a datapoint specifying dynamic latitude of twin.
    :ivar uuid.UUID longitude_id: technical id of a datapoint specifying dynamic longitude of twin.
    :ivar str color: hexadecimal code of the color to associate with this twin item.
    :ivar str icon: logical id of the icon or svg schema to associate with this twin item.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "twins"

    @classmethod
    def from_dict(cls, data):
        obj = Twin()
        obj.from_json(data)
        return obj

    def __init__(self,
                 twin_id=None,
                 hardware_id=None,
                 name=None, parent_id=None,
                 ttype=TwinBlockType.MACHINE,
                 type_id:uuid.UUID = None,
                 twin_type:TwinType = None,
                 latitude_id: uuid.UUID = None,
                 longitude_id: uuid.UUID = None,
                 color: str = None,
                 icon: str = None,
                 latitude: float = None,
                 longitude: float = None,
                 extra_properties: dict = None,
                 description: str = None):
        if twin_id is None:
            self.twin_id = uuid.uuid4()
        else:
            self.twin_id = twin_id
        self.hardware_id = hardware_id
        self.name = name
        self.parent_id = parent_id
        self.type = ttype
        if twin_type is not None:
            self.twin_type = twin_type
            self.type_id = twin_type.twin_type_id
        else:
            self.twin_type = None
            self.type_id = type_id
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.latitude_id = latitude_id
        self.longitude_id = longitude_id
        if color is not None:
            is_valid_hex_color(color)
        self.color = color
        self.icon = icon
        self.extra_properties = extra_properties
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        return str(self.twin_id).upper()

    def endpoint(self) -> str:
        return "Twins"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.twin_id = uuid.UUID(obj["id"])
        if "hardwareId" in obj.keys() and obj["hardwareId"] is not None:
            self.hardware_id = obj["hardwareId"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "parentId" in obj.keys() and obj["parentId"] is not None:
            self.parent_id = uuid.UUID(obj["parentId"])
        if "twinTypeId" in obj.keys() and obj["twinTypeId"] is not None:
            self.type_id = uuid.UUID(obj["twinTypeId"])
        if "latitude" in obj.keys() and obj["latitude"] is not None:
            self.latitude = float(obj["latitude"])
        if "longitude" in obj.keys() and obj["longitude"] is not None:
            self.longitude = float(obj["longitude"])
        if "latitudeSensorId" in obj.keys() and obj["latitudeSensorId"] is not None:
            self.latitude_id = uuid.UUID(obj["latitudeSensorId"])
        if "longitudeSensorId" in obj.keys() and obj["longitudeSensorId"] is not None:
            self.longitude_id = uuid.UUID(obj["longitudeSensorId"])
        if "color" in obj.keys() and obj["color"] is not None:
            is_valid_hex_color(str(obj["color"]))
            self.color = str(obj["color"])
        if "icon" in obj.keys() and obj["icon"] is not None:
            self.icon = str(obj["icon"])
        if "description" in obj.keys() and obj["description"] is not None:
            self.description = str(obj["description"])
        if "type" in obj.keys():
            self.type = TwinBlockType(str(obj["type"]))
        if "extraProperties" in obj.keys():
            if isinstance(obj["extraProperties"], str):
                self.extra_properties = json.loads(obj["extraProperties"])
            else:
                self.extra_properties = obj["extraProperties"]
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.twin_id)
        }
        if self.hardware_id is not None:
            obj["hardwareId"] = str(self.hardware_id)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.parent_id is not None:
            obj["parentId"] = str(self.parent_id)
        if self.twin_type is not None:
            obj["twinTypeId"] = str(self.twin_type.twin_type_id)
        elif self.type_id is not None:
            obj["twinTypeId"] = str(self.type_id)
        if self.type is not None and isinstance(self.type, TwinBlockType):
            obj["type"] = self.type.value
        if self.color is not None:
            obj["color"] = str(self.color)
        if self.description is not None:
            obj["description"] = str(self.description)
        if self.latitude is not None:
            obj["latitude"] = float(self.latitude)
        if self.longitude is not None:
            obj["longitude"] = float(self.longitude)
        if self.latitude_id is not None:
            obj["latitudeSensorId"] = str(self.latitude_id)
        if self.longitude_id is not None:
            obj["longitudeSensorId"] = str(self.longitude_id)
        if self.icon is not None:
            obj["icon"] = str(self.icon)
        if self.extra_properties is not None:
            if not isinstance(self.extra_properties, dict):
                raise ValueError('on twin extra properties must be None or a JSON serializable dict')
            obj["extraProperties"] = json.dumps(self.extra_properties)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj
