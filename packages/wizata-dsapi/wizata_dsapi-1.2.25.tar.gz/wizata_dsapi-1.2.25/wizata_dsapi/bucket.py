from .api_dto import ApiDto


class Bucket(ApiDto):
    """
    a bucket is a group of time-series data.
    """

    @classmethod
    def route(cls):
        return "buckets"

    @classmethod
    def from_dict(cls, data):
        obj = Bucket()
        obj.from_json(data)
        return obj

    def __init__(self,
                 name: str = None,
                 retention_seconds: int = None):
        self.name = name
        self.retention_seconds = retention_seconds

    def api_id(self) -> str:
        return str(self.name).upper()

    def endpoint(self) -> str:
        return "Buckets"

    def to_json(self, target: str = None):
        obj = {}
        if self.retention_seconds is not None:
            obj["retentionSeconds"] = int(self.retention_seconds)
        if self.name is not None:
            obj["name"] = str(self.name)
        return obj

    def from_json(self, obj):
        if "retentionSeconds" in obj.keys() and obj["retentionSeconds"] is not None:
            self.retention_seconds = int(obj["retentionSeconds"])
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
