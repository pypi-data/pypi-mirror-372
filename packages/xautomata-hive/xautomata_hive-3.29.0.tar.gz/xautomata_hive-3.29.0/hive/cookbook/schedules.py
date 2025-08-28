from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Schedules(ApiManager):
    """Class that handles all the XAutomata schedules APIs"""

    def schedules(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Tracking Schedules

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            uuid_customer (string optional): additional filter - parameter
            code (string optional): additional filter - parameter
            ical (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'uuid_customer', 'code', 'ical',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('uuid_customer'), params.get('code'
            ), params.get('ical'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.schedules.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/schedules/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def schedules_create(self, kwargs: dict = None, **payload) -> list:
        """Create Tracking Schedule

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_customer (string required): additional filter - payload
            code (string required): additional filter - payload
            ical (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'code', 'ical']
        payload.get('uuid_customer'), payload.get('code'), payload.get('ical')
        if not self._silence_warning:
            warning_wrong_parameters(self.schedules_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/schedules/', payload=
            payload, **kwargs)
        return response

    def schedule(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Tracking Schedule

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['join']
        params.get('join')
        if not self._silence_warning:
            warning_wrong_parameters(self.schedule.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/schedules/{uuid}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def schedules_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Tracking Schedule

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_customer (string optional): additional filter - payload
            code (string optional): additional filter - payload
            ical (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'code', 'ical']
        payload.get('uuid_customer'), payload.get('code'), payload.get('ical')
        if not self._silence_warning:
            warning_wrong_parameters(self.schedules_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/schedules/{uuid}', payload=
            payload, **kwargs)
        return response

    def schedules_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Tracking Schedule

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/schedules/{uuid}', **kwargs)
        return response
