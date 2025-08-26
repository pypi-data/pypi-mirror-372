from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class CostTreeNodes(ApiManager):
    """Class that handles all the XAutomata cost_tree_nodes APIs"""

    def cost_tree_nodes(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Cost Tree Nodes

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            uuid_parent (string optional): additional filter - parameter
            code (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            uuid_view (string optional): additional filter - parameter
            budget (integer optional): additional filter - parameter
            null_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'uuid_parent', 'code',
            'description', 'uuid_view', 'budget', 'null_fields', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('uuid_parent'), params.get('code'
            ), params.get('description'), params.get('uuid_view'), params.get(
            'budget'), params.get('null_fields'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tree_nodes.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/cost_tree_nodes/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def cost_tree_nodes_create(self, kwargs: dict = None, **payload) -> list:
        """Create Cost Tree Node

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_parent (string optional): additional filter - payload
            code (string required): additional filter - payload
            description (string optional): additional filter - payload
            uuid_view (string required): additional filter - payload
            budget (integer optional): additional filter - payload
            criteria (array object optional): additional filter - payload
            virtual (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_parent', 'code', 'description',
            'uuid_view', 'budget', 'criteria', 'virtual']
        payload.get('uuid_parent'), payload.get('code'), payload.get(
            'description'), payload.get('uuid_view'), payload.get('budget'
            ), payload.get('criteria'), payload.get('virtual')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tree_nodes_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/cost_tree_nodes/', payload=
            payload, **kwargs)
        return response

    def cost_tree_node(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Cost Tree Node

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
            warning_wrong_parameters(self.cost_tree_node.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/cost_tree_nodes/{uuid}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def cost_tree_nodes_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Cost Tree Node

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_parent (string optional): additional filter - payload
            code (string optional): additional filter - payload
            description (string optional): additional filter - payload
            uuid_view (string optional): additional filter - payload
            budget (integer optional): additional filter - payload
            criteria (array object optional): additional filter - payload
            virtual (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_parent', 'code', 'description',
            'uuid_view', 'budget', 'criteria', 'virtual']
        payload.get('uuid_parent'), payload.get('code'), payload.get(
            'description'), payload.get('uuid_view'), payload.get('budget'
            ), payload.get('criteria'), payload.get('virtual')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tree_nodes_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/cost_tree_nodes/{uuid}',
            payload=payload, **kwargs)
        return response

    def cost_tree_nodes_delete(self, uuid: str, kwargs: dict = None, **params
        ) -> list:
        """Delete Cost Tree Node

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            delete_resources (boolean optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['delete_resources']
        params.get('delete_resources')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tree_nodes_delete.__name__,
                params, official_params_list)
        response = self.execute('DELETE', path=f'/cost_tree_nodes/{uuid}',
            params=params, **kwargs)
        return response

    def cost_tree_nodes_navigate_tree(self, uuid: str,
        warm_start: bool = False, kwargs: dict = None, **params) -> list:
        """Get Tree From Node V2

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter
            resource_id (string optional): additional filter - parameter
            previous_period (boolean optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end', 'resource_id',
            'previous_period']
        params.get('date_start'), params.get('date_end'), params.get(
            'resource_id'), params.get('previous_period')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tree_nodes_navigate_tree.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/cost_tree_nodes/navigate_tree/{uuid}', warm_start=warm_start,
            params=params, **kwargs)
        return response

    def cost_tree_nodes_get_node_resources(self, uuid: str,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Get Resources From Node

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter
            resource_id (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end', 'resource_id',
            'skip', 'limit', 'sort_by']
        params.get('date_start'), params.get('date_end'), params.get(
            'resource_id'), params.get('skip'), params.get('limit'
            ), params.get('sort_by')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                cost_tree_nodes_get_node_resources.__name__, params,
                official_params_list)
        response = self.execute('GET', path=
            f'/cost_tree_nodes/get_node_resources/{uuid}', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def cost_tree_nodes_resources_by_criteria(self, uuid: str,
        warm_start: bool = False, kwargs: dict = None, **params) -> list:
        """Get Resources From Node By Criteria

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                cost_tree_nodes_resources_by_criteria.__name__, params,
                official_params_list)
        response = self.execute('GET', path=
            f'/cost_tree_nodes/{uuid}/resources_by_criteria', warm_start=
            warm_start, params=params, **kwargs)
        return response
