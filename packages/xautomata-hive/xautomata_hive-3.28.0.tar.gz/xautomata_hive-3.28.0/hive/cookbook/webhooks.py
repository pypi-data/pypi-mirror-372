from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Webhooks(ApiManager):
    """Class that handles all the XAutomata webhooks APIs"""

    def webhooks(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Webhooks

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            webhook_type (string optional): additional filter - parameter
            uuid_probe (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'webhook_type',
            'uuid_probe', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'webhook_type'), params.get('uuid_probe'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.webhooks.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/webhooks/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def webhooks_create(self, kwargs: dict = None, **payload) -> list:
        """Create Webhook

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            data_profile (array object optional): additional filter - payload
            webhook_type (string required): additional filter - payload
            auth_token (string required): additional filter - payload
            uuid_probe (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['data_profile', 'webhook_type',
            'auth_token', 'uuid_probe']
        payload.get('data_profile'), payload.get('webhook_type'), payload.get(
            'auth_token'), payload.get('uuid_probe')
        if not self._silence_warning:
            warning_wrong_parameters(self.webhooks_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/webhooks/', payload=payload,
            **kwargs)
        return response

    def webhook(self, uuid: str, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Read Webhook

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/webhooks/{uuid}', warm_start
            =warm_start, **kwargs)
        return response

    def webhooks_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Webhook

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            data_profile (array object optional): additional filter - payload
            webhook_type (string optional): additional filter - payload
            auth_token (string optional): additional filter - payload
            uuid_probe (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['data_profile', 'webhook_type',
            'auth_token', 'uuid_probe']
        payload.get('data_profile'), payload.get('webhook_type'), payload.get(
            'auth_token'), payload.get('uuid_probe')
        if not self._silence_warning:
            warning_wrong_parameters(self.webhooks_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/webhooks/{uuid}', payload=
            payload, **kwargs)
        return response

    def webhooks_create_webhook_type(self, payload: list, webhook_type: str,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Post Webhook

        Args:
            payload (list[dict], optional): List dict to create.
            webhook_type (str, required): webhook_type
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            xa-auth-token (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['xa-auth-token']
        params.get('xa-auth-token')
        if not self._silence_warning:
            warning_wrong_parameters(self.webhooks_create.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/webhooks/{webhook_type}',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response
