import uuid
import json

import wizata_dsapi
from .api_dto import ApiDto, VarType
from .datapoint import DataPoint
from .template import TemplateProperty


class TwinRegistrationProperty(ApiDto):
    """
    define a property mapping between template and registration.
    :ivar uuid.UUID twin_registration_property_id: technical id of the twin registration property.
    :ivar uuid.UUID twin_registration_id: technical id of the twin registration.
    :ivar wizata_dsapi.TemplateProperty template_property: template property associated.
    :ivar wizata_dsapi.VarType p_type: type associate to this registration - equal the one on template_property.
    :ivar value: value of the registration property, type is depending upon p_type.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "registrationproperties"

    @classmethod
    def from_dict(cls, data):
        obj = TwinRegistrationProperty()
        obj.from_json(data)
        return obj

    def __init__(self,
                 twin_registration_property_id: uuid.UUID = None,
                 twin_registration_id: uuid.UUID = None,
                 template_property: TemplateProperty = None,
                 value=None,
                 p_type: VarType = None):
        if twin_registration_property_id is None:
            self.twin_registration_property_id = uuid.uuid4()
        else:
            self.twin_registration_property_id = twin_registration_property_id
        self.twin_registration_id = twin_registration_id
        self.template_property = template_property
        self.value = value
        self.p_type = p_type
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        return str(self.twin_registration_property_id).upper()

    def endpoint(self) -> str:
        return "TwinRegistrationProperties"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.twin_registration_property_id = uuid.UUID(obj["id"])
        if "templatePropertyId" in obj.keys() and obj["templatePropertyId"] is not None:
            self.template_property = TemplateProperty(obj["templatePropertyId"])
        if "twinRegistrationId" in obj.keys() and obj["twinRegistrationId"] is not None:
            self.twin_registration_id = obj["twinRegistrationId"]

        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

        if "sensorId" in obj.keys() and obj["sensorId"] is not None:
            datapoint = DataPoint(datapoint_id=obj["sensorId"])
            if "sensor" in obj.keys():
                datapoint.from_json(obj["sensor"])
            self.value = datapoint
            self.p_type = VarType.DATAPOINT
        elif "json" in obj.keys() and obj["json"] is not None:
            if isinstance(obj["json"], str):
                self.value = json.loads(obj["json"])
            else:
                self.value = obj["json"]
            self.p_type = VarType.JSON
        elif "relative" in obj.keys() and obj["relative"] is not None:
            self.value = obj["relative"]
            self.p_type = VarType.RELATIVE
        elif "datetime" in obj.keys() and obj["datetime"] is not None:
            self.value = obj["datetime"]
            self.p_type = VarType.DATETIME
        elif "integer" in obj.keys() and obj["integer"] is not None:
            self.value = obj["integer"]
            self.p_type = VarType.INTEGER
        elif "float" in obj.keys() and obj["float"] is not None:
            self.value = obj["float"]
            self.p_type = VarType.FLOAT
        elif "string" in obj.keys() and obj["string"] is not None:
            self.value = obj["string"]
            self.p_type = VarType.STRING

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.twin_registration_property_id)
        }
        if self.template_property is not None:
            obj["templatePropertyId"] = str(self.template_property.template_property_id)
        if self.twin_registration_id is not None:
            obj["twinRegistrationId"] = str(self.twin_registration_id)
        if self.p_type is not None:
            if self.p_type == VarType.JSON:
                if isinstance(self.value, str):
                    obj["json"] = self.value
                else:
                    obj["json"] = json.dumps(self.value)
            elif self.p_type == VarType.FLOAT:
                try:
                    obj["float"] = float(self.value)
                except Exception as e:
                    print(f'{self.twin_registration_property_id} have invalid property type/value')
                    obj["float"] = None
            elif self.p_type == VarType.STRING:
                obj["string"] = str(self.value)
            elif self.p_type == VarType.INTEGER:
                try:
                    obj["integer"] = int(self.value)
                except Exception as e:
                    print(f'{self.twin_registration_property_id} have invalid property type/value')
                    obj["integer"] = None
            elif self.p_type == VarType.DATETIME:
                try:
                    obj["datetime"] = int(self.value)
                except Exception as e:
                    print(f'{self.twin_registration_property_id} have invalid property type/value')
                    obj["datetime"] = None
            elif self.p_type == VarType.RELATIVE:
                obj["relative"] = str(self.value)
            elif self.p_type == VarType.DATAPOINT:
                obj["sensorId"] = str(self.value.datapoint_id)
            else:
                raise ValueError(f'unrecognized {self.p_type} registration property type')

        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj


class TwinRegistration(ApiDto):
    """
    registration of a digital twin item on a template.

    :ivar uuid.UUID twin_registration_id: technical id of the registration.
    :ivar uuid.UUID twin_id: technical id of the twin item.
    :ivar uuid.UUID template_id: technical id of the template.
    :ivar list properties: list of wizata_dsapi.TwinRegistrationProperty or dict { name , datapoint, float, integer, string }
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "registrations"

    @classmethod
    def from_dict(cls, data):
        obj = TwinRegistration()
        obj.from_json(data)
        return obj

    def __init__(self, twin_registration_id=None, twin_id=None, template_id=None, properties=None):
        if twin_registration_id is None:
            self.twin_registration_id = uuid.uuid4()
        else:
            self.twin_registration_id = twin_registration_id
        self.twin_id = twin_id
        self.template_id = template_id

        # retro-compatibility properties
        if properties is None:
            properties = []
        self.properties = properties

        # new hidden properties
        self._properties = []

        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

        # connected entity
        self.twin = None

    def api_id(self) -> str:
        return str(self.twin_registration_id).upper()

    def endpoint(self) -> str:
        return "TwinRegistration"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.twin_registration_id = uuid.UUID(obj["id"])
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
        if "twinRegistrationProperties" in obj.keys() and obj["twinRegistrationProperties"] is not None:
            for dict_property in obj["twinRegistrationProperties"]:
                r_property = TwinRegistrationProperty()
                r_property.from_json(dict_property)
                self._properties.append(r_property)
        elif "properties" in obj.keys() and obj["properties"] is not None:
            if isinstance(obj["properties"], str):
                self.properties = json.loads(obj["properties"])
            else:
                self.properties = obj["properties"]
            self._properties = []
            for dict_property in self.properties:
                if isinstance(dict_property, dict):
                    r_property = TwinRegistrationProperty()
                    r_property.from_json(dict_property)
                    self._properties.append(r_property)
                else:
                    print(f'{dict_property} is invalid properties on registration {self.twin_registration_id} '
                          f'and have been skipped')
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
            "id": str(self.twin_registration_id)
        }
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self._properties is not None and self._properties != []:
            list_properties = []
            r_property: TwinRegistrationProperty
            for r_property in self._properties:
                list_properties.append(r_property.to_json())
            obj["properties"] = json.dumps(list_properties)
        elif self.properties is not None:
            obj["properties"] = json.dumps(self.properties)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj

    def append(self, registration_property: TwinRegistrationProperty):
        """
        append a twin registration property.
        :param wizata_dsapi.TwinRegistrationProperty registration_property: append a property.
        """

        if registration_property.twin_registration_id is None:
            registration_property.twin_registration_id = self.twin_registration_id
        elif registration_property.twin_registration_id != self.twin_registration_id:
            raise ValueError('mismatch between registration id and property id')

        self._properties.append(registration_property)

    def get_properties(self) -> list:
        """
        return a list of TwinRegistrationProperty (replacing dict properties)
        """
        return self._properties

    def get_value(self, name: str, p_type: str):
        """
        get value of a property based on name and type.
        :param name: name of property.
        :param p_type: type of property.
        :return: value.
        """
        if self.properties is None:
            raise ValueError('there is no property on your registration.')

        if name is None or p_type is None:
            raise ValueError('please set a name or a p_type')

        for r_property in self.properties:
            if r_property is None:
                raise ValueError('a registration property cannot be None.')

            if "name" in r_property and r_property["name"] is not None and r_property["name"] == name:
                if p_type not in r_property:
                    raise ValueError(f'requested type is not set on the property {name}')
                return r_property[p_type]

        raise ValueError(f'property {name} of type {p_type} not found in the registration')
