import uuid
from .api_dto import ApiDto


class Plot(ApiDto):
    """
    A plot is a definition of a Plotly figure that can be stored and shared on Wizata.
    :ivar plot_id: The UUID of the plot.
    :ivar generatedById: The UUID of the Execution from which the plot was created.
    :ivar name: A simple name helping the user identifying the plot.
    :ivar figure: Plotly figure defining the plot itself.
    """

    @classmethod
    def route(cls):
        return "plots"

    @classmethod
    def from_dict(cls, data):
        obj = Plot()
        obj.from_json(data)
        return obj

    def __init__(self, plot_id=None, name=None, generated_by_id=None, figure=None):
        if plot_id is None:
            self.plot_id = uuid.uuid4()
        else:
            self.plot_id = plot_id
        self.name = name
        self.generatedById = generated_by_id # Execution
        # Step Id
        self.figure = figure

    def api_id(self) -> str:
        """
        Id of the plot (plot_id)
        :return: string formatted UUID of the plot.
        """
        return str(self.plot_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate plots.
        :return: Endpoint name.
        """
        return "Plots"

    def from_json(self, obj):
        """
        Load the Plot entity from a dictionary representation of the Plot.
        :param obj: Dict version of the Plot.
        """
        if "id" in obj.keys():
            self.plot_id = uuid.UUID(obj["id"])
        if "name" in obj.keys():
            self.name = obj["name"]
        if "figure" in obj.keys():
            self.figure = obj["figure"]
        if "generatedById" in obj.keys():
            self.generatedById = int(obj["generatedById"])

    def to_json(self, target: str = None):
        """
        Convert the plot to a dictionary compatible to JSON format.
        :return: dictionary representation of the Plot object.
        """
        obj = {
            "id": str(self.plot_id)
        }
        if self.name is not None:
            obj["name"] = self.name
        if target is None or target != 'backend-create':
            if self.figure is not None:
                obj["figure"] = self.figure
        if self.generatedById is not None:
            obj["generatedById"] = self.generatedById
        return obj
