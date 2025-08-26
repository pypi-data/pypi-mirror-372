from .api_dto import ApiDto


class DataStore(ApiDto):

    @classmethod
    def route(cls):
        return "datastores"

    @classmethod
    def from_dict(cls, data):
        obj = DataStore()
        obj.from_json(data)
        return obj

    @classmethod
    def get_id_type(cls) -> type:
        return int

    def __init__(self,
                 data_store_id: int = None,
                 name: str = None,
                 bucket: str = None,
                 measurement: str = None,
                 retention_seconds: int = None,
                 do_not_use_sensor_id: bool = False):
        self.data_store_id = data_store_id
        self.name = name
        self.bucket = bucket
        self.measurement = measurement
        self.retention_seconds = retention_seconds
        self.do_not_use_sensor_id = do_not_use_sensor_id

    def api_id(self) -> str:
        return str(self.data_store_id).upper()

    def endpoint(self) -> str:
        return "DataStores"

    def set_id(self, id_value):
        if not isinstance(id_value, int):
            raise TypeError(f"data store id must be an integer")
        self.data_store_id = id_value

    def to_json(self, target: str = None):
        obj = {}
        if self.data_store_id is not None:
            obj["id"] = self.data_store_id
        if self.name is not None:
            obj["name"] = self.name
        if self.bucket is not None:
            obj["bucket"] = self.bucket
        if self.measurement is not None:
            obj["measurement"] = self.measurement
        if self.retention_seconds is not None:
            obj["retentionSeconds"] = int(self.retention_seconds)
        if self.do_not_use_sensor_id is not None:
            obj["doNotUseSensorId"] = self.do_not_use_sensor_id
        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.data_store_id = int(obj["id"])
        if "name" in obj.keys():
            self.name = str(obj['name'])
        if "bucket" in obj.keys():
            self.bucket = str(obj['bucket'])
        if "measurement" in obj.keys():
            self.measurement = str(obj['measurement'])
        if "retentionSeconds" in obj.keys():
            self.retention_seconds = int(obj['retentionSeconds'])
        if "doNotUseSensorId" in obj.keys():
            if isinstance(obj["doNotUseSensorId"], str):
                if obj["doNotUseSensorId"] == "False" or obj["doNotUseSensorId"] is None:
                    self.do_not_use_sensor_id = False
                else:
                    self.do_not_use_sensor_id = True
            else:
                self.do_not_use_sensor_id = obj['doNotUseSensorId']
