from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Questions(ApiManager):
    """Class that handles all the XAutomata questions APIs"""

    def questions(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Tracking Questions

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            ts_response_start (string optional): additional filter - parameter
            ts_response_end (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'type',
            'ts_response_start', 'ts_response_end', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('type'
            ), params.get('ts_response_start'), params.get('ts_response_end'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.questions.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/questions/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def questions_create(self, kwargs: dict = None, **payload) -> list:
        """Create Tracking Question

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            type (string required): additional filter - payload
            expires_at (string required): additional filter - payload
            data_profile (array object required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['type', 'expires_at', 'data_profile']
        payload.get('type'), payload.get('expires_at'), payload.get(
            'data_profile')
        if not self._silence_warning:
            warning_wrong_parameters(self.questions_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/questions/', payload=
            payload, **kwargs)
        return response

    def question(self, uuid: str, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Read Tracking Question

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/questions/{uuid}',
            warm_start=warm_start, **kwargs)
        return response

    def questions_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Tracking Question

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            token (string required): additional filter - payload
            response (array object required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['token', 'response']
        payload.get('token'), payload.get('response')
        if not self._silence_warning:
            warning_wrong_parameters(self.questions_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/questions/{uuid}', payload=
            payload, **kwargs)
        return response

    def questions_by_token(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Tracking Question By Token

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            q-token (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['q-token']
        params.get('q-token')
        if not self._silence_warning:
            warning_wrong_parameters(self.questions_by_token.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/questions/{uuid}/by_token',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def questions_reset_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Reset Tracking Question

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            expires_at (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['expires_at']
        payload.get('expires_at')
        if not self._silence_warning:
            warning_wrong_parameters(self.questions_reset_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/questions/{uuid}/reset',
            payload=payload, **kwargs)
        return response
