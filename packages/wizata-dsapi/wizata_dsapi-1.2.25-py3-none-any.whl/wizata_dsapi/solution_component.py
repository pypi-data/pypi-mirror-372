import uuid
from .api_dto import ApiDto
from .dataframe_toolkit import verify_relative_datetime
from enum import Enum
import json


class SolutionType(Enum):
    """
    SolutionType defines components content type enumeration:
        - "Grafana" embedded grafana dashboard within Wizata.
        - "Dashboard" native default dashboard.
        - "Iframe" custom iframe displayed within a component.
    """
    GRAFANA = "Grafana"
    DASHBOARD = "Dashboard"
    IFRAME = "Iframe"
    STREAMLIT = "Streamlit"


class SolutionComponent(ApiDto):
    """
    A component handle part of a solution displayed to end users to interact with solution.
    The component is rendered under 'operate' section and associated to a digital twin item.
    It can be a native dashboard, a grafana dashboard, ...
    :ivar uuid.UUID solution_component_id: identifier of the component.
    :ivar str content: depending on component type : iframe URL or grafana relative URL (e.g. 'd/your_uid/name')
    :ivar uuid.UUID dashboard_id: technical UUID of a dashboard only for native dashboard.
    :ivar str default_from: relative date (e.g. now-1d) used as default value to filter the component content.
    :ivar str default_to: relative date (e.g. now) used as default value to filter the component content.
    :ivar uuid.UUID label_id: Business Label identification on which menu displaying the component.
    :ivar str name: Component name used as the tab name.
    :ivar int order: Value used to order the tabs.
    :ivar uuid.UUID owner_id: set to a user to associate for a personal component, leave None for a global component.
    :ivar wizata_dsapi.SolutionType solution_type: defines component type (Dashboard, Grafana, ...)
    :ivar uuid.UUID template_id: unique identifier of template (optional).
    :ivar uuid.UUID twin_id: unique identifier of digital twin item associated.
    :ivar uuid.UUID createdById: unique identifier of creating user.
    :ivar int createdDate: timestamp of created date.
    :ivar uuid.UUID updatedById: unique identifier of updating user.
    :ivar int updatedDate: timestamp of updated date.
    :ivar int refreshInterval: refresh interval in ms or as a str Grafana format (e.g. '30s').
    """

    @classmethod
    def route(cls):
        return "components"

    @classmethod
    def from_dict(cls, data):
        obj = SolutionComponent()
        obj.from_json(data)
        return obj

    possible_refresh_intervals = {
        "5s": 5000,
        "10s": 10000,
        "30s": 30000,
        "1m": 60000,
        "5m": 300000,
        "15m": 900000,
        "30m": 1800000,
        "1h": 3600000,
        "2h": 7200000,
        "1d": 86400000
    }

    def __init__(
        self,
        solution_component_id=None,
        label_id=None,
        name=None,
        solution_type=None,
        content=None,
        order=None,
        dashboard_id=None,
        twin_id=None,
        template_id=None,
        owner_id=None,
        default_from: str = None,
        default_to: str = None,
        refresh_interval = None
    ):
        if solution_component_id is None:
            self.solution_component_id = uuid.uuid4()
        else:
            self.solution_component_id = solution_component_id

        self.label_id = label_id
        self.name = name

        self.order = order
        if self.order is not None and not isinstance(self.order, int):
            raise TypeError(f"order must be None or a valid integer")

        self.solution_type = solution_type
        if self.solution_type is not None and not isinstance(
            self.solution_type, SolutionType
        ):
            raise TypeError(f"solution type must be None or a valid SolutionType")

        self.content = content
        self.dashboard_id = dashboard_id

        self.owner_id = owner_id

        self.twin_id = twin_id
        self.template_id = template_id

        self.default_from = default_from
        self.default_to = default_to

        self.refresh_interval = refresh_interval

        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    @property
    def refresh_interval(self):
        for key, value in self.possible_refresh_intervals.items():
            if value == self._refresh_interval:
                return key
        return None

    @refresh_interval.setter
    def refresh_interval(self, value):
        if value is not None:
            if isinstance(value, str):
                if value not in self.possible_refresh_intervals:
                    raise ValueError(f'refresh_interval as a str must be in {self.possible_refresh_intervals.keys()}')
                else:
                    self._refresh_interval = self.possible_refresh_intervals[value]
            elif isinstance(value, int):
                if value == 0:
                    self._refresh_interval = 0
                else:
                    closest_value = min(self.possible_refresh_intervals.values(), key=lambda x: abs(x - value))
                    self._refresh_interval = closest_value
            else:
                raise TypeError(f'refresh_interval expect int as ms or str from {self.possible_refresh_intervals.keys()}')
        else:
            self._refresh_interval = value

    def api_id(self) -> str:
        return str(self.solution_component_id).upper()

    def endpoint(self) -> str:
        return "Components"

    def to_json(self, target: str = None):
        if self.label_id is None:
            raise ValueError("label ID is required when creating/updating a component.")
        if self.name is None:
            raise ValueError("name is required when creating/updating a component.")
        if self.solution_type is None or not isinstance(
            self.solution_type, SolutionType
        ):
            raise ValueError("solution type must be a valid solution type.")
        obj = {
            "id": str(self.solution_component_id),
            "labelId": str(self.label_id),
            "name": self.name,
            "type": self.solution_type.value,
        }

        if self.order is not None:
            if not isinstance(self.order, int):
                raise ValueError("order must be None or a valid integer.")
            obj["order"] = self.order

        if self.content is not None:
            obj["content"] = self.content
        if self.solution_type == SolutionType.DASHBOARD:
            if self.dashboard_id is None or not isinstance(
                self.dashboard_id, uuid.UUID
            ):
                raise ValueError(
                    "dashboard Id of type UUID must be on component type dashboard"
                )
            obj["dashboardId"] = str(self.dashboard_id)

        if self.owner_id is not None:
            obj["ownerId"] = str(self.owner_id)
        if self.twin_id is not None:
            obj["twinId"] = str(self.twin_id)
        if self.template_id is not None:
            obj["templateId"] = str(self.template_id)

        if self.default_from is not None and verify_relative_datetime(self.default_from):
            obj["defaultFrom"] = self.default_from
        if self.default_to is not None and verify_relative_datetime(self.default_to):
            obj["defaultTo"] = self.default_to

        if self._refresh_interval is not None:
            obj["refreshInterval"] = int(self._refresh_interval)

        return obj

    def from_json(self, obj):
        if "id" in obj.keys():
            self.solution_component_id = uuid.UUID(obj["id"])
        if "labelId" in obj.keys() and obj["labelId"] is not None:
            self.label_id = uuid.UUID(obj["labelId"])
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "ownerId" in obj.keys() and obj["ownerId"] is not None:
            self.owner_id = uuid.UUID(obj["ownerId"])
        if "defaultFrom" in obj.keys() and obj["defaultFrom"] is not None and obj["defaultFrom"] != '':
            self.default_from = obj["defaultFrom"]
        if "defaultTo" in obj.keys() and obj["defaultTo"] is not None and obj["defaultTo"] != '':
            self.default_to = obj["defaultTo"]
        if "order" in obj.keys() and obj["order"] is not None:
            self.order = int(obj["order"])
        if "content" in obj.keys() and obj["content"] is not None:
            self.content = obj["content"]
        if "type" in obj.keys():
            self.solution_type = SolutionType(str(obj["type"]))
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twin_id = uuid.UUID(obj["twinId"])
        if "dashboardId" in obj.keys() and obj["dashboardId"] is not None:
            self.dashboard_id = uuid.UUID(obj["dashboardId"])
        if "templateId" in obj.keys() and obj["templateId"] is not None:
            self.template_id = uuid.UUID(obj["templateId"])
        if "refreshInterval" in obj.keys() and obj["refreshInterval"] is not None:
            self.refresh_interval = obj["refreshInterval"]
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]
