import uuid
from .api_dto import ApiDto


class BusinessLabel(ApiDto):
    """
    A Business Label is a custom tag representing any business concept.
    :ivar uuid.UUID label_id: technical identifier.
    :ivar str name: display name.
    :ivar str description: description of the label.
    :ivar str icon: identifier of Wizata icon.
    :ivar str color: hexadecimal color code.
    :ivar int order: integer value used to order the labels on the side navigation.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    """

    @classmethod
    def route(cls):
        return "components/labels"

    @classmethod
    def from_dict(cls, data):
        obj = BusinessLabel()
        obj.from_json(data)
        return obj

    def __init__(self, label_id=None, name=None, description=None, icon=None, color=None, order=None):
        if label_id is None:
            self.label_id = uuid.uuid4()
        else:
            self.label_id = label_id
        self.name = name
        self.description = description
        self.icon = icon
        self.color = color
        self.order = order
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        formatted id of the business label (label_id)
        :return: string formatted UUID.
        """
        return str(self.label_id).upper()

    def endpoint(self) -> str:
        """
        endpoint name used to manipulate business label on backend.
        :return: endpoint name.
        """
        return "BusinessLabels"

    def to_json(self, target: str = None):
        """
        load the business label entity from a dictionary.
        :param obj: dict version of the business label.
        """
        obj = {
            "id": str(self.label_id)
        }
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.description is not None:
            obj["description"] = str(self.description)
        if self.icon is not None:
            obj["icon"] = str(self.icon)
        if self.color is not None:
            obj["color"] = str(self.color)
        if self.order is not None:
            obj["order"] = int(self.order)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj

    def from_json(self, obj):
        """
        convert the business label to a dictionary compatible with JSON format.
        :return: dictionary representation of the business label object.
        """
        if "id" in obj.keys():
            self.label_id = uuid.UUID(obj["id"])
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "description" in obj.keys() and obj["description"] is not None:
            self.description = obj["description"]
        if "icon" in obj.keys() and obj["icon"] is not None:
            self.icon = obj["icon"]
        if "color" in obj.keys() and obj["color"] is not None:
            self.color = obj["color"]
        if "order" in obj.keys() and obj["order"] is not None:
            self.order = obj["order"]
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]
