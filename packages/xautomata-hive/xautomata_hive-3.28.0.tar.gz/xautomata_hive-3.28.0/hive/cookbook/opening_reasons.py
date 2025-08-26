from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class OpeningReasons(ApiManager):
    """Class that handles all the XAutomata opening_reasons APIs"""

    def opening_reasons(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Opening Reasons

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            code (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            severity (string optional): additional filter - parameter
            sla_l1 (integer optional): additional filter - parameter
            sla_l2 (integer optional): additional filter - parameter
            sla_l3 (integer optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'code',
            'description', 'severity', 'sla_l1', 'sla_l2', 'sla_l3', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('code'
            ), params.get('description'), params.get('severity'), params.get(
            'sla_l1'), params.get('sla_l2'), params.get('sla_l3'), params.get(
            'skip'), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.opening_reasons.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/opening_reasons/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def opening_reasons_create(self, kwargs: dict = None, **payload) -> list:
        """Create Opening Reason

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            code (string required): additional filter - payload
            description (string optional): additional filter - payload
            severity (string required): additional filter - payload
            sla_l1 (integer required): additional filter - payload
            sla_l2 (integer required): additional filter - payload
            sla_l3 (integer required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['code', 'description', 'severity',
            'sla_l1', 'sla_l2', 'sla_l3']
        payload.get('code'), payload.get('description'), payload.get('severity'
            ), payload.get('sla_l1'), payload.get('sla_l2'), payload.get(
            'sla_l3')
        if not self._silence_warning:
            warning_wrong_parameters(self.opening_reasons_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/opening_reasons/', payload=
            payload, **kwargs)
        return response

    def opening_reason(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Read Opening Reason

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/opening_reasons/{uuid}',
            warm_start=warm_start, **kwargs)
        return response

    def opening_reasons_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Opening Reason

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            code (string optional): additional filter - payload
            description (string optional): additional filter - payload
            severity (string optional): additional filter - payload
            sla_l1 (integer optional): additional filter - payload
            sla_l2 (integer optional): additional filter - payload
            sla_l3 (integer optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['code', 'description', 'severity',
            'sla_l1', 'sla_l2', 'sla_l3']
        payload.get('code'), payload.get('description'), payload.get('severity'
            ), payload.get('sla_l1'), payload.get('sla_l2'), payload.get(
            'sla_l3')
        if not self._silence_warning:
            warning_wrong_parameters(self.opening_reasons_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/opening_reasons/{uuid}',
            payload=payload, **kwargs)
        return response

    def opening_reasons_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Opening Reason

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/opening_reasons/{uuid}',
            **kwargs)
        return response

    def opening_reasons_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read Opening Reasons

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
            warning_wrong_parameters(self.opening_reasons_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/opening_reasons/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def opening_reasons_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Create Opening Reasons

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
            "code": "string", required
            "description": "string", optional
            "severity": "string", required
            "sla_l1": "integer", required
            "sla_l2": "integer", required
            "sla_l3": "integer", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.opening_reasons_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/opening_reasons/bulk/create/', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def opening_reasons_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Delete Opening Reasons

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
        response = self.execute('POST', path=
            f'/opening_reasons/bulk/delete/', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response
