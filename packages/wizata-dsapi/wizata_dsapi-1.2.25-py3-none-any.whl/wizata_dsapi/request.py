import uuid
from datetime import datetime, timedelta, timezone
from .dataframe_toolkit import generate_epoch
from .api_dto import ApiDto
from .datapoint import BusinessType

filter_map = {
    '>': 'gt',
    '<': 'lt',
    '>=': 'gte',
    '<=': 'lte',
    '==': 'eq',
    '!=': 'neq'
}

class DynamicSelector:
    """
    A dynamic selector defines how datapoint(s) are fetched within a query.
        - it corresponds to a request to fetch datapoints
        - it must be used on a twin base query
    :ivar category: filter datapoints on uuid of a category or str name.
    """

    def __init__(self,
                 category = None,
                 unit = None,
                 twin_type = None,
                 agg_method = None,
                 rename = None,
                 business_type: BusinessType = None):
        self.category = category
        self.unit = unit
        self.twin_type = twin_type
        self.agg_method = agg_method
        self.rename = rename
        self.business_type = business_type
        self.datapoints = []

    @classmethod
    def from_dict(cls, obj):
        dynamic_selector = cls()
        dynamic_selector.from_json(obj)
        return dynamic_selector

    def from_json(self, obj):
        if not isinstance(obj, dict):
            raise TypeError('dynamic selector to parse is not a dict.')
        if "category" in obj:
            self.category = obj["category"]
        if "unit" in obj:
            self.unit = obj["unit"]
        if "twin_type" in obj:
            self.twin_type = obj["twin_type"]
        if "business_type" in obj:
            self.business_type = BusinessType(obj["business_type"])
        if "datapoints" in obj:
            self.datapoints = obj["datapoints"]
        if "rename" in obj:
            self.rename = obj["rename"]
        if "agg_method" in obj:
            self.agg_method = obj["agg_method"]

    def to_json(self) -> dict:
        obj = {}
        if self.category:
            obj["category"] = self.category
        if self.unit:
            obj["unit"] = self.unit
        if self.twin_type:
            obj["twin_type"] = self.twin_type
        if self.business_type:
            obj["business_type"] = self.business_type.value
        if self.datapoints:
            obj["datapoints"] = self.datapoints
        if self.agg_method:
            obj["agg_method"] = self.agg_method
        if self.rename:
            obj["rename"] = self.rename
        return obj

class RequestGroup:
    """
    Define a group statement within a structured query.
    """

    def __init__(self,
                 system_id,
                 events: list = None,
                 group_by: str = "id",
                 start_delay: int = 0,
                 end_delay: int = 0,
                 maps: list = None):
        self.system_id = system_id
        self.group_by = group_by
        self.events = events
        self.maps = maps
        self.start_delay = start_delay
        self.end_delay = end_delay

    @classmethod
    def from_dict(cls, my_dict):
        if my_dict is None or not isinstance(my_dict, dict):
            raise ValueError(f"illegal group {my_dict}")

        if "system_id" not in my_dict or my_dict["system_id"] is None:
            if not isinstance(["system_id"], str) and not isinstance(my_dict["system_id"], int):
                raise ValueError(f"please specify system_id in {my_dict}")

        group = RequestGroup(
            system_id=my_dict["system_id"]
        )

        # set group_by
        if "group_by" in my_dict:
            if my_dict["group_by"] not in ["id", "type"]:
                raise ValueError(f"illegal group {my_dict['group_by']}")
            group.group_by = my_dict["group_by"]

        # one of the two is accepted to set events
        if "event_ids" in my_dict:
            group.events = my_dict["event_ids"]
        if "events" in my_dict:
            group.events = my_dict["events"]

        if "start_delay" in my_dict:
            group.start_delay = int(my_dict["start_delay"])

        if "end_delay" in my_dict:
            group.end_delay = int(my_dict["end_delay"])

        return group


class RequestGroupMap:
    """
    Define a mapping between a set of datapoints and their corresponding event datapoint.
    :ivar event_hardware_id str: hardware id of the datapoint identifying event inside a group.
    :ivar event_datapoint: datapoint complete definition corresponding to event_hardware_id.
    :ivar datapoints_hardware_ids list: list of all related datapoints.
    :ivar datapoints dict: dict with key as hardware id and value datapoint for all mapped datapoints.
    """

    def __init__(self,
                 event_hardware_id: str,
                 datapoints_hardware_ids: list,
                 group: RequestGroup = None):
        self.event_hardware_id = event_hardware_id
        self.datapoints_hardware_ids = datapoints_hardware_ids
        self.event_datapoint = None
        self.datapoints = {}
        self.group = group


class Request(ApiDto):
    """
    request defines how to fetch data from time-series database.

    :ivar list datapoints: list of str pointing to hardware ids of datapoint or template properties name.
    :ivar datetime|str start: start range to fetch set as a datetime, a @parameter or str relative format (e.g. 'now-1d')
    :ivar datetime|str end: start range to fetch set as a datetime, a @parameter or str relative format (e.g. 'now')
    :ivar str aggregation: aggregation method ("mean", "stddev", "mode", "median", "count", "sum", "first", "last", "max", "min").
    :ivar int interval: interval passed in seconds at __init__ (stored as milliseconds).
    :ivar uuid.UUID template_id: use technical id of wizata_dsapi.Template to fetch data based on a template.
    :ivar uuid.UUID twin_id: technical id of wizata_dsapi.Twin registered on template_id.
    :ivar dict filters: filters to apply to the query pre-aggregation. nested dictionary using as first key=datapoint then value=another dictionary with key=operator (gt,lt,gte,lte,eq,neq) and value is the float value to compare too).
    :ivar dict options: dict representing query options.
    """

    @classmethod
    def route(cls):
        return "data"

    @classmethod
    def from_dict(cls, data):
        obj = Request()
        obj.from_json(data)
        return obj

    @classmethod
    def get_type(cls):
        return "pickle"

    def __init__(self,
                 datapoints=None,
                 start=None,
                 end=None,
                 agg_method='mean',
                 interval=None,
                 null='drop',
                 template_id=None,
                 template=None,
                 twin_id=None,
                 twin=None,
                 request_id=None,
                 filters=None,
                 group=None,
                 options=None,
                 field=None,
                 bucket=None,
                 tags=None):
        if request_id is None:
            request_id = uuid.uuid4()
        self.request_id = request_id
        self.function = None

        # Datapoints
        self._datapoints = []
        self.datapoints = datapoints

        # Template & Registration
        self.template = None
        self.select_template(
             template_id=template_id,
             template_key=template,
             twin_id=twin_id,
             twin_hardware_id=twin
        )

        self.start = start
        self.end = end

        self.aggregation = agg_method
        if interval is not None:
            self.interval = int(interval) / 1000
        else:
            self.interval = None

        self.filters = filters
        self.group = group
        self.options = options
        self.field = field

        self.on_off_sensor = None
        self.restart_time = None
        self.sensitivity = None
        self.dataframe = None
        self.extra_data = None
        self.target_feat = None
        self.connections = None
        self.name = None
        self.bucket = bucket
        self.tags = tags

        self.null = null

    @property
    def fields(self):
        if self.field is None:
            return ['value']
        elif isinstance(self.field, str):
            return [self.field]
        elif isinstance(self.field, list):
            return self.field
        else:
            raise TypeError(f'field must be None, str or a list of str')

    @property
    def groups(self) -> list[RequestGroup]:
        """
        return formatted groups list based on group
        :return:
        """
        if self.group is not None and self.group != {}:
            if not isinstance(self.group, list):
                return [RequestGroup.from_dict(self.group)]
            else:
                groups = []
                for group in self.group:
                    groups.append(RequestGroup.from_dict(group))
                return groups
        else:
            return []

    def get_template_id(self):
        """
        extract template id from request if present.
        :return: template id as uuid.UUID
        """
        if self.template is None:
            return

        if isinstance(self.template, str):
            try:
                template_id = uuid.UUID(self.template)
                return template_id
            except ValueError as ve:
                return
        else:
            if not isinstance(self.template, dict):
                raise ValueError(f'template in request must be a str or a dict')
            elif "template_id" not in self.template:
                return
            else:
                if isinstance(self.template['template_id'], uuid.UUID):
                    return self.template['template_id']
                else:
                    return uuid.UUID(self.template['template_id'])

    def get_template_key(self):
        """
        extract template key from request if present.
        :return: template key as str
        """
        if self.template is None:
            return

        if isinstance(self.template, str):
            return
        else:
            if not isinstance(self.template, dict):
                raise ValueError(f'template in request must be a str or a dict')
            elif "template_id" not in self.template:
                if "template_key" not in self.template:
                    return
                else:
                    return self.template["template_key"]
            else:
                return

    def get_twin_id(self):
        """
        extract twin id from request if present.
        :return: template key as uuid
        """
        if self.template is None:
            return

        if not isinstance(self.template, dict):
            return

        if "twin_id" not in self.template:
            return
        else:
            if isinstance(self.template['twin_id'], uuid.UUID):
                return self.template['twin_id']
            else:
                return uuid.UUID(self.template['twin_id'])

    def get_twin_hardware_id(self):
        """
        extract twin hardware id from request if present.
        :return: template key as str
        """
        if self.template is None:
            return

        if not isinstance(self.template, dict):
            return

        if "twin_id" not in self.template:
            if "twin_hardware_id" not in self.template:
                return
            else:
                return self.template['twin_hardware_id']
        else:
            return

    def __format_date(self, dt_to_format):
        if isinstance(dt_to_format, datetime):
            millisec = dt_to_format.timestamp() * 1000
            return int(millisec)
        else:
            raise TypeError("date is not a valid datetime")

    def start_time(self, now=None) -> datetime:
        """
        convert a relative start time to a datetime based on a now parameter.
        :param now: override now value for relative datetime
        :return: start datetime
        """
        if self.start is None:
            raise ValueError('missing start datetime')
        elif isinstance(self.start, str):
            return datetime.fromtimestamp(generate_epoch(self.start, now=now) / 1000, timezone.utc)
        elif isinstance(self.start, datetime):
            return self.start
        else:
            raise TypeError(f'unsupported start datetime type {self.start.__class__.__name__}')

    def end_time(self, now=None) -> datetime:
        """
        convert a relative end time to a datetime based on a now parameter.
        :param now: override now value for relative datetime
        :return: end datetime
        """
        if self.end is None:
            raise ValueError('missing end datetime')
        elif isinstance(self.end, str):
            return datetime.fromtimestamp(generate_epoch(self.end, now=now) / 1000, timezone.utc)
        elif isinstance(self.end, datetime):
            return self.end
        else:
            raise TypeError(f'unsupported end datetime type {self.end.__class__.__name__}')

    @property
    def datapoints(self):
        return self._datapoints

    @datapoints.setter
    def datapoints(self, values):
        self._datapoints = []
        if values:
            if not isinstance(values, list):
                raise ValueError(f'datapoints on a query must be a list of str, dict or DynamicSelector')
            for value in values:
                if isinstance(value, str):
                    self._datapoints.append(value)
                elif isinstance(value, dict):
                    self._datapoints.append(DynamicSelector.from_dict(value))
                elif isinstance(value, DynamicSelector):
                    self._datapoints.append(value)
                else:
                    raise TypeError(f'datapoints on a query must be a list of str, dict or DynamicSelector '
                                    f'but encountered {type(value)} as {value}')

    @property
    def datapoints_without_selectors(self):
        datapoints = []
        for datapoint in self._datapoints:
            if not isinstance(datapoint, DynamicSelector):
                datapoints.append(datapoint)
        return datapoints

    @property
    def datapoints_only_selectors(self):
        datapoints = []
        for datapoint in self._datapoints:
            if isinstance(datapoint, DynamicSelector):
                datapoints.append(datapoint)
        return datapoints

    def set_aggregation(self, method, interval=None):
        """
        specifies aggregation properties
        :param method: "mean", "stddev", "mode", "median", "count", "sum", "first", "last", "max" or "min"
        :param interval: interval in ms (will be stored in seconds) can be null
        """
        if method not in self.list_agg_methods():
            raise KeyError(f'unsupported agg_method {method}.')
        self.aggregation = method
        if interval is not None:
            self.interval = int(interval) / 1000

    def list_agg_methods(self) -> list:
        """
        get a list of all authorized methods.
        :return: list with "mean", "stddev", "mode", "median", "count", "sum", "first", "last", "max" or "min"
        """
        return [
            "mean", "stddev", "mode", "median", "count", "sum", "first", "last", "max", "min", None
        ]

    def select_template(self,
                        template_id=None,
                        template_key=None,
                        twin_id=None,
                        twin_hardware_id=None):
        """
        select a template and its registration.
        :param template_id: template UUID
        :param template_key: template key ( ignored if template_id specified )
        :param twin_id: Digital Twin UUID
        :param twin_hardware_id: hardware ID of Digital Twin ( ignored if twin_id specified )
        """
        if template_id is None and template_key is None and twin_id is None and twin_hardware_id is None:
            self.template = None
            return
        else:
            self.template = {}

            if template_id is not None:
                if isinstance(template_id, uuid.UUID):
                    self.template['template_id'] = template_id
                else:
                    self.template['template_id'] = uuid.UUID(template_id)
            elif template_key is not None:
                self.template['template_key'] = str(template_key)

            if twin_id is not None:
                if isinstance(twin_id, uuid.UUID):
                    self.template['twin_id'] = twin_id
                else:
                    self.template['twin_id'] = uuid.UUID(twin_id)

            elif twin_hardware_id is not None:
                self.template['twin_hardware_id'] = str(twin_hardware_id)

    def get_params(self):
        """
        get a list of all parameters.
        :return: list of parameters
        """
        params = []

        if self.start is not None and isinstance(self.start, str) and self.start.startswith("@"):
            params.append(self.start[1:])

        if self.end is not None and isinstance(self.end, str) and self.end.startswith("@"):
            params.append(self.end[1:])

        return list(set(params))

    def set_param(self, name: str, value):
        """
        set value of parameter based on his name.
        """
        assigned = False

        if value is None:
            raise ValueError(f'please provide a valid param value for {name}')

        if self.start is not None and isinstance(self.start, str) \
                and self.start.startswith("@") and self.start[1:] == name:
            self.start = value
            assigned = True

        if self.end is not None and isinstance(self.end, str) \
                and self.end.startswith("@") and self.end[1:] == name:
            self.end = value
            assigned = True

        if not assigned:
            raise KeyError(f'parameter {name} not found in request.')

    def to_json(self, target: str = None):
        query = {}

        if self.request_id is not None:
            query["id"] = str(self.request_id)

        datapoints = []
        for datapoint in self.datapoints:
            if isinstance(datapoint, str):
                datapoints.append(datapoint)
            elif isinstance(datapoint, dict):
                datapoints.append(datapoint)
            elif isinstance(datapoint, DynamicSelector):
                datapoints.append(datapoint.to_json())
            else:
                raise TypeError(f'datapoints on a query must be a list of str, dict or DynamicSelector '
                                f'but encountered {type(datapoint)} as {datapoint}')
        query["datapoints"] = datapoints

        if self.start is not None and self.end is not None:

            if isinstance(self.start, str):
                start = self.start
            else:
                start = self.__format_date(self.start)

            if isinstance(self.end, str):
                end = self.end
            else:
                end = self.__format_date(self.end)

            query["timeframe"] = {
                "start": start,
                "end": end
            }
        else:
            if self.group is None:
                raise KeyError("missing in query start and end date, "
                               "please use datatime format or try with a group system")
        query["aggregations"] = {
            "agg_method": self.aggregation
        }
        if self.interval:
            query["aggregations"]["interval"] = self.interval * 1000
        if self.null is not None and self.null != 'drop':
            query['null'] = self.null
        if self.template is not None:
            query['template'] = self.template
            if isinstance(self.template, dict) and 'template_id' in query['template']:
                query['template']['template_id'] = str(query['template']['template_id'])
        if self.filters is not None:
            query['filters'] = self.filters
        if self.group is not None:
            query['group'] = self.group
        if self.options is not None:
            query['options'] = self.options
        if self.field is not None:
            query['field'] = self.field
        if self.bucket is not None:
            query['bucket'] = self.bucket
        if self.tags is not None:
            query['tags'] = self.tags

        if self.target_feat is not None:
            query["target_feat"] = {
                "sensor": self.target_feat["sensor"],
                "operator": self.target_feat["operator"],
                "threshold": self.target_feat["threshold"]
            }
        if self.on_off_sensor is not None and self.restart_time is not None:
            query["restart_filter"] = {
                "on_off_sensor": self.on_off_sensor,
                "stop_restart_time": self.restart_time
            }

        if self.sensitivity is not None:
            query["sensitivity"] = self.sensitivity

        if self.extra_data is not None:
            query["extra_data"] = self.extra_data

        return query

    def from_json(self, json_data):
        if "id" in json_data.keys():
            self.request_id = uuid.UUID(json_data["id"])

        if "name" in json_data.keys():
            self.name = json_data["name"]

        datapoints = []
        if "equipments_list" in json_data.keys():
            for equipment in json_data["equipments_list"]:
                if "datapoints" not in equipment.keys():
                    raise KeyError("no 'datapoints' have been provided for equipment with id '" +
                                   str(equipment["id"]) + "'")
                datapoints.extend(equipment["datapoints"])

        if "datapoints" in json_data.keys():
            datapoints.extend(json_data["datapoints"])

        if "template" in json_data.keys():
            self.template = json_data["template"]

        if len(datapoints) == 0 and self.template is None:
            raise KeyError('at least one datapoint or template is required within a request')

        if len(datapoints) >= 0:
            self.datapoints = datapoints
        else:
            self._datapoints = []

        if "timeframe" in json_data.keys():
            if "start" not in json_data["timeframe"].keys():
                raise KeyError("No 'start time' have been selected, please set it up and re-try.")

            if isinstance(json_data["timeframe"]["start"], str):
                self.start = json_data["timeframe"]["start"]
            else:
                self.start = datetime.fromtimestamp(json_data["timeframe"]["start"] / 1000, timezone.utc)

            if "end" not in json_data["timeframe"].keys():
                raise KeyError("No 'end time' have been selected, please set it up and re-try.")

            if isinstance(json_data["timeframe"]["end"], str):
                self.end = json_data["timeframe"]["end"]
            else:
                self.end = datetime.fromtimestamp(json_data["timeframe"]["end"] / 1000, timezone.utc)
        else:
            if "group" not in json_data.keys():
                raise KeyError("No 'timeframe' and no 'group' found in object, please set a time or group selection.")

        if "aggregations" not in json_data.keys():
            raise KeyError("No 'aggregations' have been selected, please set it up and re-try.")

        if "agg_method" not in json_data["aggregations"].keys():
            self.aggregation = None
        elif json_data["aggregations"]["agg_method"] not in self.list_agg_methods():
            raise KeyError(f'unsupported agg_method {json_data["aggregations"]["agg_method"]}.')
        else:
            self.aggregation = json_data["aggregations"]["agg_method"]

        if "interval" in json_data["aggregations"].keys():
            self.interval = int(json_data["aggregations"]["interval"] / 1000)

        if "filters" in json_data.keys():
            filters = {}
            for filter_data in json_data["filters"]:
                filter_reformat = {}
                for operator in json_data["filters"][filter_data]:
                    if operator in filter_map.keys():
                        filter_reformat[filter_map[operator]] = json_data["filters"][filter_data][operator]
                    elif operator not in filter_map.values():
                        raise ValueError(f'invalid request filter operator {operator}')
                    else:
                        filter_reformat[operator] = json_data["filters"][filter_data][operator]
                filters[filter_data] = filter_reformat
            self.filters = filters
        else:
            self.filters = {}

        if "group" in json_data.keys():
            self.group = json_data["group"]
        else:
            self.group = {}

        if "options" in json_data.keys():
            self.options = json_data["options"]
        else:
            self.options = {}

        if "field" in json_data.keys():
            self.field = json_data["field"]

        if "bucket" in json_data.keys():
            self.bucket = json_data["bucket"]

        if "tags" in json_data.keys():
            self.tags = json_data["tags"]

        if "connections" in json_data.keys():
            self.connections = json_data["connections"]

        if "null" in json_data.keys():
            self.null = json_data["null"]

        if "target_feat" in json_data.keys():
            self.target_feat = json_data["target_feat"]
            if "sensor" not in self.target_feat.keys():
                raise KeyError("No 'sensor' have been declared inside the target feature, this is a technical error.")
            if "operator" not in self.target_feat.keys():
                raise KeyError("No 'operator' have been declared inside the target feature, this is a technical error.")
            if "threshold" not in self.target_feat.keys():
                raise KeyError("No 'threshold' have been declared inside the target feature, this is a technical error.")

        if "restart_filter" in json_data.keys():
            self.on_off_sensor = json_data["restart_filter"]["on_off_sensor"]
            self.restart_time = json_data["restart_filter"]["stop_restart_time"]

        if "sensitivity" in json_data.keys():
            self.sensitivity = json_data["sensitivity"]

        if "extra_data" in json_data.keys():
            self.extra_data = json_data["extra_data"]


