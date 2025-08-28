from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class CostViews(ApiManager):
    """Class that handles all the XAutomata cost_views APIs"""

    def cost_views(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Cost Views

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            uuid_customer (string optional): additional filter - parameter
            null_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'name', 'description', 'type',
            'uuid_customer', 'null_fields', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('sort_by'), params.get('name'), params.get('description'
            ), params.get('type'), params.get('uuid_customer'), params.get(
            'null_fields'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_views.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/cost_views/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def cost_views_create(self, kwargs: dict = None, **payload) -> list:
        """Create Cost View

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_customer (string required): additional filter - payload
            name (string required): additional filter - payload
            description (string optional): additional filter - payload
            type (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'name', 'description', 'type'
            ]
        payload.get('uuid_customer'), payload.get('name'), payload.get(
            'description'), payload.get('type')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_views_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/cost_views/', payload=
            payload, **kwargs)
        return response

    def cost_view(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Cost View

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
            warning_wrong_parameters(self.cost_view.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/cost_views/{uuid}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def cost_views_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Cost View

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            name (string optional): additional filter - payload
            description (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['name', 'description']
        payload.get('name'), payload.get('description')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_views_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/cost_views/{uuid}', payload=
            payload, **kwargs)
        return response

    def cost_views_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Cost View

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/cost_views/{uuid}', **kwargs)
        return response

    def cost_views_users(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Cost View Users

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['skip', 'limit', 'like', 'join', 'count']
        params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_views_users.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/cost_views/{uuid}/users',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def cost_views_users_create(self, uuid: str, name: str, kwargs: dict = None
        ) -> list:
        """Create Association With User

        Args:
            uuid (str, required): uuid
            name (str, required): name
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/cost_views/{uuid}/users/{name}', **kwargs)
        return response

    def cost_views_users_delete(self, uuid: str, name: str, kwargs: dict = None
        ) -> list:
        """Delete Association With User

        Args:
            uuid (str, required): uuid
            name (str, required): name
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/cost_views/{uuid}/users/{name}', **kwargs)
        return response

    def cost_views_assign_resources_create(self, uuid: str,
        kwargs: dict = None, **params) -> list:
        """Set Resources From Node By Criteria

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                cost_views_assign_resources_create.__name__, params,
                official_params_list)
        response = self.execute('POST', path=
            f'/cost_views/{uuid}/assign_resources', params=params, **kwargs)
        return response
