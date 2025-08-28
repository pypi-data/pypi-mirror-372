from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class ProbesLogIngest(ApiManager):
    """Class that handles all the XAutomata probes_log_ingest APIs"""

    def probes_log_ingest_create(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Insert Probe Log

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            uuid_probe (string required): additional filter - parameter
            key (string optional): additional filter - parameter

        Examples:
            payload = 
          [
            "uuid": "str", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['uuid_probe', 'key']
        params.get('uuid_probe'), params.get('key')
        if not self._silence_warning:
            warning_wrong_parameters(self.probes_log_ingest_create.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/probes_log_ingest/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response
