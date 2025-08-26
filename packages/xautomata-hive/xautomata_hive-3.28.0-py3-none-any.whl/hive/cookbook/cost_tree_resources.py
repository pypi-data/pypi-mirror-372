from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class CostTreeResources(ApiManager):
    """Class that handles all the XAutomata cost_tree_resources APIs"""

    def cost_tree_resources(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Cost Tree Resources

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            uuid_tree_node (string optional): additional filter - parameter
            uuid_view (string optional): additional filter - parameter
            cost_category (string optional): additional filter - parameter
            cost_category_value (string optional): additional filter - parameter
            percentage (number optional): additional filter - parameter
            null_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'uuid_tree_node', 'uuid_view',
            'cost_category', 'cost_category_value', 'percentage',
            'null_fields', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('uuid_tree_node'), params.get(
            'uuid_view'), params.get('cost_category'), params.get(
            'cost_category_value'), params.get('percentage'), params.get(
            'null_fields'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tree_resources.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/cost_tree_resources/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def cost_tree_resources_create(self, kwargs: dict = None, **payload
        ) -> list:
        """Create Cost Tree Resource

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_tree_node (string required): additional filter - payload
            cost_category (string required): additional filter - payload
            cost_category_value (string required): additional filter - payload
            percentage (number optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_tree_node', 'cost_category',
            'cost_category_value', 'percentage']
        payload.get('uuid_tree_node'), payload.get('cost_category'
            ), payload.get('cost_category_value'), payload.get('percentage')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tree_resources_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/cost_tree_resources/',
            payload=payload, **kwargs)
        return response

    def cost_tree_resources_all_resource_ids(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Get Resource Ids V2

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter
            uuid_customer (string optional): additional filter - parameter
            uuid_view (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end', 'uuid_customer',
            'uuid_view', 'skip', 'limit', 'like', 'join', 'count']
        params.get('date_start'), params.get('date_end'), params.get(
            'uuid_customer'), params.get('uuid_view'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                cost_tree_resources_all_resource_ids.__name__, params,
                official_params_list)
        response = self.execute('GET', path=
            f'/cost_tree_resources/all_resource_ids/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def cost_tree_resources_unfully_assigned_resource_ids(self,
        uuid_view: str, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Get Unfully Assigned Resource Ids V2

        Args:
            uuid_view (str, required): uuid_view
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
            warning_wrong_parameters(self.
                cost_tree_resources_unfully_assigned_resource_ids.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/cost_tree_resources/{uuid_view}/unfully_assigned_resource_ids/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def cost_tree_resources_unfully_assigned_resources(self, uuid_view: str,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Get Unfully Assigned Resources

        Args:
            uuid_view (str, required): uuid_view
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
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end', 'resource_id',
            'skip', 'limit', 'count', 'sort_by']
        params.get('date_start'), params.get('date_end'), params.get(
            'resource_id'), params.get('skip'), params.get('limit'
            ), params.get('count'), params.get('sort_by')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                cost_tree_resources_unfully_assigned_resources.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/cost_tree_resources/{uuid_view}/unfully_assigned_resources/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def cost_tree_resources_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Delete Tree Resources

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "uuid_tree_node": "string", required
            "cost_category": "string", required
            "cost_category_value": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/cost_tree_resources/bulk/delete/', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def cost_tree_resources_delete(self, uuid_tree_node: str,
        kwargs: dict = None) -> list:
        """Delete For Uuid Tree Node

        Args:
            uuid_tree_node (str, required): uuid_tree_node
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/cost_tree_resources/delete/{uuid_tree_node}', **kwargs)
        return response
