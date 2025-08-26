from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Widgets(ApiManager):
    """Class that handles all the XAutomata widgets APIs"""

    def widgets(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Widgets

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
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'code', 'name',
            'description', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('code'
            ), params.get('name'), params.get('description'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/widgets/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def widgets_create(self, kwargs: dict = None, **payload) -> list:
        """Create Widget

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            code (string required): additional filter - payload
            name (string required): additional filter - payload
            description (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['code', 'name', 'description']
        payload.get('code'), payload.get('name'), payload.get('description')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/widgets/', payload=payload,
            **kwargs)
        return response

    def widget(self, uuid: str, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Read Widget

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/widgets/{uuid}', warm_start=
            warm_start, **kwargs)
        return response

    def widgets_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Widget

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            code (string optional): additional filter - payload
            name (string optional): additional filter - payload
            description (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['code', 'name', 'description']
        payload.get('code'), payload.get('name'), payload.get('description')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/widgets/{uuid}', payload=
            payload, **kwargs)
        return response

    def widgets_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Widget

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/widgets/{uuid}', **kwargs)
        return response

    def widgets_dashboards(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Dashboards

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            name (string optional): additional filter - parameter
            index (integer optional): additional filter - parameter
            width (integer optional): additional filter - parameter
            height (integer optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'index', 'width',
            'height', 'skip', 'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('name'), params.get('index'
            ), params.get('width'), params.get('height'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_dashboards.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/widgets/{uuid}/dashboards',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def widgets_dashboards_create(self, uuid: str, uuid_dashboard: str,
        kwargs: dict = None, **payload) -> list:
        """Add Dashboard

        Args:
            uuid (str, required): uuid
            uuid_dashboard (str, required): uuid_dashboard
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            index (integer optional): additional filter - payload
            width (integer optional): additional filter - payload
            height (integer optional): additional filter - payload
            grid_x (integer optional): additional filter - payload
            grid_y (integer optional): additional filter - payload
            settings (array object optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['index', 'width', 'height', 'grid_x',
            'grid_y', 'settings']
        payload.get('index'), payload.get('width'), payload.get('height'
            ), payload.get('grid_x'), payload.get('grid_y'), payload.get(
            'settings')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_dashboards_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=
            f'/widgets/{uuid}/dashboards/{uuid_dashboard}', payload=payload,
            **kwargs)
        return response

    def widgets_dashboard_widget_put(self, uuid: str, kwargs: dict = None,
        **payload) -> list:
        """Update Dashboard Widget Association

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            index (integer optional): additional filter - payload
            width (integer optional): additional filter - payload
            height (integer optional): additional filter - payload
            grid_x (integer optional): additional filter - payload
            grid_y (integer optional): additional filter - payload
            settings (array object optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['index', 'width', 'height', 'grid_x',
            'grid_y', 'settings']
        payload.get('index'), payload.get('width'), payload.get('height'
            ), payload.get('grid_x'), payload.get('grid_y'), payload.get(
            'settings')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_dashboard_widget_put.
                __name__, payload, official_payload_list)
        response = self.execute('PUT', path=
            f'/widgets/dashboard_widget/{uuid}', payload=payload, **kwargs)
        return response

    def widgets_dashboard_widget_delete(self, uuid: str, kwargs: dict = None
        ) -> list:
        """Remove Dashboard Widget Association

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/widgets/dashboard_widget/{uuid}', **kwargs)
        return response

    def widgets_widget_groups(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Widget Groups

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            name (string optional): additional filter - parameter
            active (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'active', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('not_in'), params.get('name'), params.get('active'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_widget_groups.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/widgets/{uuid}/widget_groups', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def widgets_widget_groups_create(self, uuid: str,
        uuid_widget_group: str, kwargs: dict = None) -> list:
        """Add To A Widget Group

        Args:
            uuid (str, required): uuid
            uuid_widget_group (str, required): uuid_widget_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/widgets/{uuid}/widget_groups/{uuid_widget_group}', **kwargs)
        return response

    def widgets_widget_groups_delete(self, uuid: str,
        uuid_widget_group: str, kwargs: dict = None) -> list:
        """Remove From Widget Group

        Args:
            uuid (str, required): uuid
            uuid_widget_group (str, required): uuid_widget_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/widgets/{uuid}/widget_groups/{uuid_widget_group}', **kwargs)
        return response

    def widgets_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read 

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
            warning_wrong_parameters(self.widgets_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/widgets/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def widgets_create_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Create Widgets

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
            "name": "string", required
            "description": "string", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/widgets/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def widgets_delete_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Delete Widgets

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
        response = self.execute('POST', path=f'/widgets/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def widgets_dashboards_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Dashboards

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
            "index": "integer", optional
            "width": "integer", optional
            "height": "integer", optional
            "grid_x": "integer", optional
            "grid_y": "integer", optional
            "settings": "array object", optional
            "uuid_dashboard": "string", required
            "uuid_widget": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.widgets_dashboards_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/widgets/bulk/create/dashboards', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def widgets_dashboards_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Dashboards

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
            f'/widgets/bulk/delete/dashboards', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response
