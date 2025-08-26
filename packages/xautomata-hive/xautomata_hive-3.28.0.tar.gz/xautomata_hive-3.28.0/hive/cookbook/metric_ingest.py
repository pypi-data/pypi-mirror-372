from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class MetricIngest(ApiManager):
    """Class that handles all the XAutomata metric_ingest APIs"""

    def metric_ingest_create(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Insert Metric

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "extended_attributes_0": "string", optional
            "uuid_metric_0": "string", required
            "uuid_probe_0": "string", required
            "timestamp_0": "integer", required
            "object_type_0": "string", optional
            "value_0": "string", required
            "unit_0": "string", required
            "description_0": "string", required
            "status_0": "None", required
            "ranking_0": "integer", required
            "extended_attributes_1": "string", optional
            "uuid_metric_1": "string", required
            "uuid_probe_1": "string", required
            "timestamp_1": "integer", required
            "object_type_1": "string", optional
            "status_1": "None", required
            "ranking_1": "integer", required
            "description_1": "string", required
            "extended_attributes_2": "string", required
            "uuid_metric_2": "string", required
            "uuid_probe_2": "string", required
            "timestamp_2": "integer", required
            "object_type_2": "string", optional
            "description_2": "string", optional
            "uuid_metric_3": "string", required
            "uuid_probe_3": "string", required
            "timestamp_3": "integer", required
            "object_type_3": "string", optional
            "unit_3": "string", required
            "value_3": "number", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/metric_ingest/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response
