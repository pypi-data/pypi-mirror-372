import uuid
import json
from typing import Optional

from .api_dto import ApiDto, VarType


class TemplateProperty(ApiDto):
    """
    defines a specific property associated with a template.

    :ivar uuid.UUID template_property_id: technical id of the template property.
    :ivar str name: name of the property to use in your queries, properties, dataframes, ...
    :ivar uuid.UUID template_id: template id on which the property is associated.
    :ivar str description: additional description of your property.
    :ivar wizata_dsapi.VarType p_type: property type as a valid VarType.
    :ivar bool required: set if your property is required.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "templateproperties"

    @classmethod
    def from_dict(cls, data):
        obj = TemplateProperty()
        obj.from_json(data)
        return obj

    def __init__(self,
                 template_property_id: uuid.UUID = None,
                 name: str = None,
                 description: str = None,
                 p_type: VarType = None,
                 required: bool = True,
                 template_id: uuid.UUID = None,
                 unit_id: uuid.UUID = None):
        if template_property_id is None:
            self.template_property_id = uuid.uuid4()
        else:
            self.template_property_id = template_property_id
        self.description = description
        self.template_id = template_id
        self.name = name
        self.p_type = p_type
        self.required = required
        self.unit_id = unit_id
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        return str(self.template_property_id).upper()

    def endpoint(self) -> str:
        return "TemplateProperties"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.template_property_id = uuid.UUID(obj["id"])
        if "name" in obj.keys():
            self.name = obj["name"]
        if "type" in obj.keys() and obj["type"] is not None:
            self.p_type = VarType(obj["type"])
        if "required" in obj.keys() and obj["required"] is not None:
            if not isinstance(obj["required"], bool):
                raise TypeError(f'template property field "required" should be a valid boolean')
            self.required = obj["required"]
        else:
            self.required = True
        if "description" in obj.keys():
            self.description = obj["description"]
        if "templateId" in obj.keys():
            self.template_id = uuid.UUID(obj["templateId"])
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]
        if "unitId" in obj.keys() and obj["unitId"] is not None:
            self.unit_id = uuid.UUID(obj["unitId"])

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.template_property_id)
        }
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.description is not None:
            obj["description"] = str(self.description)
        if self.p_type is not None:
            obj["type"] = str(self.p_type.value)
        if self.required is not None:
            if not isinstance(self.required, bool):
                raise TypeError(f'template property field "required" should be a valid boolean')
            obj["required"] = self.required
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)
        if self.unit_id is not None:
            obj["unitId"] = str(self.unit_id)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj


class Template(ApiDto):
    """
    template represents a common reusable asset, concept or data model within Wizata.

    :ivar uuid.UUID template_id: technical id of the template.
    :ivar str key: unique logical str key identifier of your template.
    :ivar str name: logical display name of the Template.
    :ivar list properties: list of template properties associated with the template.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "templates"

    @classmethod
    def from_dict(cls, data):
        obj = Template()
        obj.from_json(data)
        return obj

    def __init__(self, template_id=None, key=None, name=None, properties=None):
        if template_id is None:
            self.template_id = uuid.uuid4()
        else:
            self.template_id = template_id
        self.key = key
        self.name = name

        # retro-compatibility
        if properties is None:
            properties = []
        self.properties = properties

        # new hidden properties
        self._properties = []
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

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

    def api_id(self) -> str:
        return str(self.template_id).upper()

    def endpoint(self) -> str:
        return "Templates"

    def from_json(self, obj):
        if "id" in obj.keys():
            self.template_id = uuid.UUID(obj["id"])
        if "key" in obj.keys() and obj["key"] is not None:
            self.key = obj["key"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "templateProperties" in obj.keys() and obj["templateProperties"] is not None:
            for t_property in obj["templateProperties"]:
                template_property = TemplateProperty()
                template_property.from_json(t_property)
                self._properties.append(template_property)
        elif "properties" in obj.keys() and obj["properties"] is not None:
            if isinstance(obj["properties"], str):
                properties = json.loads(obj["properties"])
            else:
                properties = obj["properties"]
            for to_add in properties:
                self.add_property(to_add)
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
            "id": str(self.template_id)
        }
        if self.key is not None:
            obj["key"] = str(self.key)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.properties is not None:
            obj_properties = []
            template_property: TemplateProperty
            for template_property in self.properties:
                obj_properties.append(template_property.to_json())
            obj["properties"] = json.dumps(obj_properties)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj

    def get_properties(self) -> list:
        """
        return a list of TemplateProperty (replacing dict properties)
        """
        return self._properties

    def add(self,
            name: str,
            p_type: VarType,
            required: bool = True,
            template_property_id: uuid.UUID = None,
            description: str = None,
            unit_id: uuid.UUID = None):
        """
        add a property to the template.
        :param str name: name of the property.
        :param wizata_dsapi.VarType p_type: property type.
        :param bool required: set if property is required (default: true)
        :param uuid.UUID template_property_id: technical id of the template property.
        :param str description: additional information as a description.
        :param uuid.UUID unit_id: unique identifier of unit for datapoint property.
        """

        if self.properties is None:
            self.properties = []

        if name is None or p_type is None:
            raise ValueError('please set a name and a type for property')

        property_value = TemplateProperty(
            template_property_id=template_property_id,
            name=name,
            p_type=p_type,
            required=required,
            description=description,
            unit_id=unit_id
        )
        property_value.template_id = self.template_id

        existing_property: TemplateProperty
        for existing_property in self.properties:
            if existing_property.name == property_value.name:
                raise ValueError(f'property {property_value.name} already exists in template.')

        self.properties.append(property_value)

    def get_property(self, property_name) -> Optional[TemplateProperty]:
        """
        get a property from its name.
        :param property_name: name of the property.
        :return: template property
        """
        for t_property in self.properties:
            if t_property.name == property_name:
                return t_property
        return None

    def add_property(self, property_value):
        """
        add a property in list of properties
        by default - a property is required
        :param property_value: dict or TemplateProperty
        """
        if isinstance(property_value, dict):
            if "type" not in property_value:
                raise KeyError("property must have a type.")
            p_type = VarType(property_value['type'])

            if "name" not in property_value:
                raise KeyError("property must have a name")
            name = property_value["name"]

            template_property_id = None
            if "id" in property_value:
                if isinstance(property_value['id'], str):
                    template_property_id = uuid.UUID(property_value['id'])
                elif isinstance(property_value['id'], uuid.UUID):
                    template_property_id = property_value['id']
                else:
                    raise ValueError('id must be a valid str or UUID')

            required = True
            if "required" in property_value:
                required = property_value["required"]

            description = None
            if "description" in property_value:
                description = property_value["description"]

            unit_id = None
            if "unitId" in property_value and property_value["unitId"] is not None:
                unit_id = uuid.UUID(property_value["unitId"])

            self.add(template_property_id=template_property_id,
                     name=name,
                     p_type=p_type,
                     required=required,
                     description=description,
                     unit_id=unit_id)
        elif isinstance(property_value, TemplateProperty):
            property_value.template_id = self.template_id

            for existing_property in self.properties:
                if existing_property.name == property_value.name:
                    raise ValueError(f'property {property_value.name} already exists in template.')

            self.properties.append(property_value)
        else:
            raise ValueError('property must be a dict or a TemplateProperty')

    def remove_property(self, name: str):
        """
        remove a property from the list based on its name
        :param name: property to remove
        """
        found_property = None

        existing_property: TemplateProperty
        for existing_property in self.properties:
            if existing_property.name == name:
                found_property = existing_property

        if self.properties is not None and found_property is not None:
            self.properties.remove(found_property)


