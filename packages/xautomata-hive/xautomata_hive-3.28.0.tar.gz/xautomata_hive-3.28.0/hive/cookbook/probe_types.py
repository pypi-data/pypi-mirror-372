from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class ProbeTypes(ApiManager):
    """Class that handles all the XAutomata probe_types APIs"""

    def probe_types(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Probe Types

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            app_code (string optional): additional filter - parameter
            app_name (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'app_code',
            'app_name', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('app_code'
            ), params.get('app_name'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.probe_types.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/probe_types/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def probe_types_create(self, kwargs: dict = None, **payload) -> list:
        """Create Probe Type

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            app_code (string required): additional filter - payload
            app_name (string optional): additional filter - payload
            endpoint (array object optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['app_code', 'app_name', 'endpoint']
        payload.get('app_code'), payload.get('app_name'), payload.get(
            'endpoint')
        if not self._silence_warning:
            warning_wrong_parameters(self.probe_types_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/probe_types/', payload=
            payload, **kwargs)
        return response

    def probe_type(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Read Probe Type

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/probe_types/{uuid}',
            warm_start=warm_start, **kwargs)
        return response

    def probe_types_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Probe Type

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            app_code (string optional): additional filter - payload
            app_name (string optional): additional filter - payload
            endpoint (array object optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['app_code', 'app_name', 'endpoint']
        payload.get('app_code'), payload.get('app_name'), payload.get(
            'endpoint')
        if not self._silence_warning:
            warning_wrong_parameters(self.probe_types_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/probe_types/{uuid}', payload
            =payload, **kwargs)
        return response

    def probe_types_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Probe Type

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/probe_types/{uuid}', **kwargs
            )
        return response

    def probe_types_probes(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Probes

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['extract_severity', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('extract_severity'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.probe_types_probes.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/probe_types/{uuid}/probes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def probe_types_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read Probe Types

        Args:
            payload (list[dict], optional): List dict to create.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter

        Examples:
            payload = 
          [
            "uuid": "str", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['join']
        params.get('join')
        if not self._silence_warning:
            warning_wrong_parameters(self.probe_types_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/probe_types/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def probe_types_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Create Probe Types

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            best_effort (boolean optional): additional filter - parameter

        Examples:
            payload = 
          [
           {
            "app_code": "string", required
            "app_name": "string", optional
            "endpoint": "array object", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.probe_types_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/probe_types/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def probe_types_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Delete Probe Types

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
            "uuid": "str", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/probe_types/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response
