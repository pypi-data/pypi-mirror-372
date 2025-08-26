import uuid
import pandas
from .api_dto import ApiDto


class DSDataFrame(ApiDto):
    """
    A DS Dataframe is a definition of a pandas Dataframe that can be stored and shared on Wizata.

    :ivar df_id: The UUID of the dataframe.
    :ivar generatedById: The UUID of the Execution from which the dataframe was created.
    :ivar dataframe: Pandas Dataframe.
    """

    @classmethod
    def route(cls):
        return "dataframes"

    @classmethod
    def from_dict(cls, data):
        obj = DSDataFrame()
        obj.from_json(data)
        return obj

    @classmethod
    def get_type(cls):
        return "pickle"

    def __init__(self, df_id=None, dataframe=None):
        if df_id is None:
            self.df_id = uuid.uuid4()
        else:
            self.df_id = df_id
        self.generatedById = None
        self.dataframe = dataframe

    def api_id(self) -> str:
        """
        Id of the dataframe (df_id)

        :return: string formatted UUID of the dataframe.
        """
        return str(self.df_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate dataframes.
        :return: Endpoint name.
        """
        return "Dataframes"

    def from_json(self, obj):
        """
        Load the Dataframe entity from a dictionary representation of the dataframe.
        Doesn't load the dataframe itself, you can use df_from_json to fetch it from JSON, CSV or other formats.

        :param obj: Dict version of the Dataframe.
        """
        if "id" in obj.keys():
            self.df_id = uuid.UUID(obj["id"])
        if "generatedById" in obj.keys():
            self.generatedById = int(obj["generatedById"])

    def to_json(self, target: str = None):
        """
        Convert the dataframe to a dictionary compatible to JSON format.

        :return: dictionary representation of the Dataframe object.
        """
        obj = {
            "id": str(self.df_id)
        }
        if self.generatedById is not None:
            obj["generatedById"] = self.generatedById
        return obj

