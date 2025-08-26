from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class CostTagging(ApiManager):
    """Class that handles all the XAutomata cost_tagging APIs"""

    def cost_tagging(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Cost Taggings

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            uuid_view (string optional): additional filter - parameter
            uuid_tag (string optional): additional filter - parameter
            tag_code (string optional): additional filter - parameter
            cost_category (string optional): additional filter - parameter
            cost_category_value (string optional): additional filter - parameter
            null_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'uuid_view', 'uuid_tag',
            'tag_code', 'cost_category', 'cost_category_value',
            'null_fields', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('uuid_view'), params.get('uuid_tag'
            ), params.get('tag_code'), params.get('cost_category'), params.get(
            'cost_category_value'), params.get('null_fields'), params.get(
            'skip'), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tagging.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/cost_tagging/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def cost_tagging_create(self, kwargs: dict = None, **payload) -> list:
        """Create Cost Tagging

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            cost_category_value (string required): additional filter - payload
            cost_category (string required): additional filter - payload
            uuid_view (string required): additional filter - payload
            uuid_tag (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['cost_category_value', 'cost_category',
            'uuid_view', 'uuid_tag']
        payload.get('cost_category_value'), payload.get('cost_category'
            ), payload.get('uuid_view'), payload.get('uuid_tag')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tagging_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/cost_tagging/', payload=
            payload, **kwargs)
        return response

    def cost_tagging_uuid(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Cost Tagging

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
            warning_wrong_parameters(self.cost_tagging.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/cost_tagging/{uuid}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def cost_tagging_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Cost Tagging

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            tag_code (string optional): additional filter - payload
            cost_category_value (string optional): additional filter - payload
            cost_category (string optional): additional filter - payload
            uuid_view (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['tag_code', 'cost_category_value',
            'cost_category', 'uuid_view']
        payload.get('tag_code'), payload.get('cost_category_value'
            ), payload.get('cost_category'), payload.get('uuid_view')
        if not self._silence_warning:
            warning_wrong_parameters(self.cost_tagging_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/cost_tagging/{uuid}',
            payload=payload, **kwargs)
        return response

    def cost_tagging_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Cost Tagging

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/cost_tagging/{uuid}', **
            kwargs)
        return response
