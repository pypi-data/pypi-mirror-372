from .api_dto import ApiDto


class GroupSystem(ApiDto):

    @classmethod
    def route(cls):
        return "groupsystems"

    @classmethod
    def from_dict(cls, data):
        obj = GroupSystem()
        obj.from_json(data)
        return obj

    @classmethod
    def get_id_type(cls) -> type:
        return int

    def __init__(self,
                 group_system_id: int = None,
                 key: str = None,
                 name: str = None,
                 description: str = None):
        self.group_system_id = group_system_id
        self.key = key
        self.name = name
        self.description = description

    def api_id(self) -> str:
        return str(self.group_system_id).upper()

    def endpoint(self) -> str:
        return "GroupSystems"

    def set_id(self, id_value):
        if not isinstance(id_value, int):
            raise TypeError(f"group system id must be an integer")
        self.group_system_id = id_value

    def to_json(self, target: str = None):
        obj = {}
        if self.group_system_id is not None:
            obj["id"] = self.group_system_id
        if self.key is not None:
            obj["key"] = self.key
        if self.name is not None:
            obj["name"] = self.name
        if self.description is not None:
            obj["description"] = self.description
        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.group_system_id = int(obj["id"])
        if "key" in obj.keys():
            self.key = str(obj['key'])
        if "name" in obj.keys():
            self.name = str(obj['name'])
        if "description" in obj.keys():
            self.description = str(obj['description'])
