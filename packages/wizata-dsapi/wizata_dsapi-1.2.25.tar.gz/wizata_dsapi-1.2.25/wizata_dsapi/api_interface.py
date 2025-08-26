import uuid
from .solution_component import SolutionComponent
from .paged_query_result import PagedQueryResult
from .pipeline import AlertType
from datetime import datetime
import pandas


class ApiInterface:
    """
    Interface with all methods available both to the pipeline runners and the Data Science API.
    """

    def __init__(self):
        self._dto_registry = {}

    def _set_registry(self, name: str, registry: dict):
        """
        internal call to set API registry definition.
        :param name: cloud_dsapi, context_dsapi, ...
        """
        if name not in ['cloud_dsapi', 'cloud_context']:
            raise ValueError(f'unsupported api type {name}')
        for entity_name in registry:
            if name in registry[entity_name] and len(registry[entity_name][name]) > 0:
                self._dto_registry[entity_name] = {
                    "class": registry[entity_name]["class"],
                    "operations": registry[entity_name][name]
                }

    def lists(self, entity):
        """
        lists all elements of a specific entity.
        :param entity: plural name of the entity or class (e.g. scripts, plots, mlmodels, dataframes...)
        :return: list of all elements with at least the id property.
        """
        pass

    def get(self,
            obj=None,
            id: uuid.UUID = None,
            key: str = None,
            entity=None):
        """
        get record content from DS API.

        - get will look first for obj then for id then for key (e.g. if id and key specified, key is ignored )

        :param obj: a wizata_dsapi.<Entity>() with UUID set - fetch using technical UUID

        :param id: a UUID of a specific object (use in combination of entity)
        :param key: a logical key of a specific object (e.g. hardware id for DataPoint and Twin (use in combination of entity)
        :param entity: plural name of the entity or class (use in combination of entity)(e.g. scripts, plots, mlmodels, dataframes...)
        :return: object with all properties or None if not found.
        """
        pass

    def create(self, obj):
        """
        create and save an object on the server
        :param obj: object from a supported entity
        :return: object created
        """
        pass

    def update(self, obj):
        """
        update and save an object on the server
        :param obj: object from a supported entity
        """
        pass

    def delete(self, obj):
        """
        delete an object on the server
        :param obj: object from a supported entity
        """
        pass

    def query(self,
              datapoints: list[str] = None,
              start: datetime = None,
              end: datetime = None,
              interval: int = None,
              agg_method: str = "mean",
              template: str = None,
              twin: str = None,
              null: str = None,
              filters: dict = None,
              options: dict = None,
              group: dict = None,
              field: str = None) -> pandas.DataFrame:
        """
        Query a dataframe from timeseries DB.
        :param agg_method:
        :param datapoints: list of datapoints to fetch.
        :param start: start datetime of range to fetch
        :param end: end datetime of range to fetch
        :param interval: interval in milliseconds.
        :param template: template to fetch.
        :param twin: hardware ID of twin to fetch based on template.
        :param null: default 'drop' will drop NaN values. If not intended behavior please set it to 'ignore' or 'all'.
        :param filters: dict of filters.
        :param options: dict of options.
        :param field: by default 'value' if none, can be used to retrieve 'eventId'
        :param group: can be used to set group system and event retrieving instructions.
        :return: dataframe
        """
        pass

    def _get_class(self,
                   entity,
                   operation: str = None):
        """
        get ApiDto class definition for a specific entity and valid that desired operation is supported.
        :param entity: str plural name of the entity or direct class definition.
        :param operation: optional - set operation name to verify it is valid on the class.
        """
        if isinstance(entity, str):
            if entity in self._dto_registry.keys():
                self._verify_operation(entity, operation)
                return self._dto_registry[entity]["class"]
            else:
                raise TypeError(f"Api entity {entity} is not supported.")
        else:
            for entity_name in self._dto_registry:
                if self._dto_registry[entity_name]["class"] == entity:
                    self._verify_operation(entity_name, operation)
                    return entity
            raise TypeError(f"Api entity {entity} is not supported.")

    def _verify_operation(self,
                          entity,
                          operation: str = None):
        """
        verify operation
        """
        if operation is not None and operation not in self._dto_registry[entity]["operations"]:
            raise NotImplementedError(f"Operation {operation} not supported for {entity} entity.")

    def get_components(self,
                       label_id: uuid.UUID = None,
                       twin_id: uuid.UUID = None,
                       template_id: uuid.UUID = None,
                       owner_id: uuid.UUID = None,
                       organization_only: bool = False,
                       name: str = None):
        """
        get components
        :param label_id: filter on a specific label
        :param template_id: filter on a specific template
        :param twin_id: filter on a specific twin
        :param owner_id: filter on a specific owner_id
        :param organization_only: work only with organization components (by default - False)
        :param name: filter on a specific name (contains)
        """
        pass

    def create_component(self, component: SolutionComponent):
        """
        create a component based on its ID.
        """
        pass

    def update_component(self, component: SolutionComponent):
        """
        update a component based on its ID.
        """
        pass

    def delete_component(self, component_id: uuid.UUID):
        """
        delete component
        """
        pass

    def get_business_labels(self) -> dict:
        """
        get a name / uuid dictionary with all business labels in platform.
        """
        pass

    def get_datapoint_mappings(self, registration):
        """
        get datapoint mapping from a registration.
        """
        pass

    def get_registrations(self, template) -> list:
        """
        retrieve all registrations for
        :param template: template object, UUID or str key.
        :return: list of twin registration.
        """
        pass

    def search_datapoints(self,
                          page: int = 1,
                          size: int = 20,
                          sort: str = "id",
                          direction: str = "asc",
                          hardware_id: str = None,
                          categories: list = None,
                          business_types: list = None,
                          twin=None,
                          recursive: bool = False) -> PagedQueryResult:
        """
        get datapoints with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param hardware_id: filter on a specific hardware ID name or partial name.
        :param business_types: list of BusinessType or str.
        :param categories: list of UUID or Category.
        :param twin: uuid or Twin element to search datapoints.
        :param recursive: set to True in combination of a twin to look inside all sub-twins recursively.
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        pass

    def search_twins(self,
                     page: int = 1,
                     size: int = 20,
                     sort: str = "id",
                     direction: str = "asc",
                     hardware_id: str = None,
                     name: str = None,
                     parents: list = None) -> PagedQueryResult:
        """
        get twins with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param hardware_id: filter on a specific hardware ID name or partial name.
        :param name: name or part of twin name.
        :param parents: list of all possible parents (Twin, UUID, or str UUID).
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        pass

    def search_insights(self,
                        page: int = 1,
                        size: int = 20,
                        sort: str = "id",
                        direction: str = "asc",
                        datapoint_id: str = None,
                        twin_id: str = None,
                        component_id: list = None):
        """
        get insights with a paged query.
        :param page: numero of the page - default 1.
        :param size: quantity per page - default 20 max 100.
        :param sort: column to sort results - default id.
        :param direction: sorting direction by default asc, accept also desc.
        :param datapoint_id: id of the datapoint on which filtering the insights.
        :param twin_id: id of the twin on which filtering the insights.
        :param component_id: id of the component on which filtering the insights.
        :return: PagedQueryResults, check total for number of potential results and results for the list of entity.
        """
        pass

    def send_alerts(self,
                    message: str,
                    recipients: list,
                    alert_type: AlertType = AlertType.SMS,
                    subject: str = "",
                    cc: list = None):
        """
        send alerts through backend
        :param str message: message to send.
        :param list recipients: list of recipients.
        :param wizata_dsapi.AlertType alert_type: type of alerts (default sms).
        :param str subject: for email only - subject of email.
        :param list cc: for email only - cc recipients list.
        """
        pass
