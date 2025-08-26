from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Dashboards(ApiManager):
    """Class that handles all the XAutomata dashboards APIs"""

    def dashboards(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Get Dashboards

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            username (string optional): additional filter - parameter
            priority (integer optional): additional filter - parameter
            refresh_interval (integer optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'name',
            'description', 'type', 'username', 'priority',
            'refresh_interval', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('name'
            ), params.get('description'), params.get('type'), params.get(
            'username'), params.get('priority'), params.get('refresh_interval'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/dashboards/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def dashboards_create(self, kwargs: dict = None, **payload) -> list:
        """Create Dashboard

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            name (string required): additional filter - payload
            type (string optional): additional filter - payload
            username (string optional): additional filter - payload
            description (string optional): additional filter - payload
            priority (integer optional): additional filter - payload
            refresh_interval (integer optional): additional filter - payload
            image_name (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['name', 'type', 'username', 'description',
            'priority', 'refresh_interval', 'image_name']
        payload.get('name'), payload.get('type'), payload.get('username'
            ), payload.get('description'), payload.get('priority'
            ), payload.get('refresh_interval'), payload.get('image_name')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/dashboards/', payload=
            payload, **kwargs)
        return response

    def dashboard(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Dashboard

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
            warning_wrong_parameters(self.dashboard.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/dashboards/{uuid}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def dashboards_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Dashboard

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            name (string optional): additional filter - payload
            type (string optional): additional filter - payload
            username (string optional): additional filter - payload
            description (string optional): additional filter - payload
            priority (integer optional): additional filter - payload
            refresh_interval (integer optional): additional filter - payload
            image_name (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['name', 'type', 'username', 'description',
            'priority', 'refresh_interval', 'image_name']
        payload.get('name'), payload.get('type'), payload.get('username'
            ), payload.get('description'), payload.get('priority'
            ), payload.get('refresh_interval'), payload.get('image_name')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/dashboards/{uuid}', payload=
            payload, **kwargs)
        return response

    def dashboards_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Dashboard

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/dashboards/{uuid}', **kwargs)
        return response

    def dashboards_image(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Get Dashboard Image

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/dashboards/{uuid}/image',
            warm_start=warm_start, **kwargs)
        return response

    def dashboards_image_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Dashboard Image

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            image (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['image']
        payload.get('image')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_image_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/dashboards/{uuid}/image',
            payload=payload, **kwargs)
        return response

    def dashboards_users(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Users

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
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('not_in'), params.get('name'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_users.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/dashboards/{uuid}/users',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dashboards_users_create(self, uuid: str, name: str, kwargs: dict = None
        ) -> list:
        """Add User

        Args:
            uuid (str, required): uuid
            name (str, required): name
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dashboards/{uuid}/users/{name}', **kwargs)
        return response

    def dashboards_users_delete(self, uuid: str, name: str, kwargs: dict = None
        ) -> list:
        """Remove User

        Args:
            uuid (str, required): uuid
            name (str, required): name
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/dashboards/{uuid}/users/{name}', **kwargs)
        return response

    def dashboards_widgets(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Widgets

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
            grid_x (integer optional): additional filter - parameter
            grid_y (integer optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'index', 'width',
            'height', 'grid_x', 'grid_y', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('name'), params.get('index'
            ), params.get('width'), params.get('height'), params.get('grid_x'
            ), params.get('grid_y'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_widgets.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/dashboards/{uuid}/widgets',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dashboards_widgets_create(self, uuid: str, uuid_widget: str,
        kwargs: dict = None, **payload) -> list:
        """Add Widget

        Args:
            uuid (str, required): uuid
            uuid_widget (str, required): uuid_widget
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
            warning_wrong_parameters(self.dashboards_widgets_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=
            f'/dashboards/{uuid}/widgets/{uuid_widget}', payload=payload,
            **kwargs)
        return response

    def dashboards_dashboard_widget_put(self, uuid: str,
        kwargs: dict = None, **payload) -> list:
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
            warning_wrong_parameters(self.dashboards_dashboard_widget_put.
                __name__, payload, official_payload_list)
        response = self.execute('PUT', path=
            f'/dashboards/dashboard_widget/{uuid}', payload=payload, **kwargs)
        return response

    def dashboards_dashboard_widget_delete(self, uuid: str, kwargs: dict = None
        ) -> list:
        """Remove Dashboard Widget Association

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/dashboards/dashboard_widget/{uuid}', **kwargs)
        return response

    def dashboards_customers(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Dashboard

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            company_name (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'company_name', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('not_in'), params.get('company_name'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_customers.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/dashboards/{uuid}/customers',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dashboards_customers_create(self, uuid: str, uuid_customer: str,
        kwargs: dict = None) -> list:
        """Create Customer Dashboard Association

        Args:
            uuid (str, required): uuid
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dashboards/{uuid}/customers/{uuid_customer}', **kwargs)
        return response

    def dashboards_customers_delete(self, uuid: str, uuid_customer: str,
        kwargs: dict = None) -> list:
        """Remove Customer Dashboard Association

        Args:
            uuid (str, required): uuid
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/dashboards/{uuid}/customers/{uuid_customer}', **kwargs)
        return response

    def dashboards_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read Widgets

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
            warning_wrong_parameters(self.dashboards_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/dashboards/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def dashboards_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Create Dashboards

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
            "name": "string", required
            "type": "string", optional
            "username": "string", optional
            "description": "string", optional
            "priority": "integer", optional
            "refresh_interval": "integer", optional
            "image_name": "string", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/dashboards/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def dashboards_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Delete Dashboards

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
        response = self.execute('POST', path=f'/dashboards/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def dashboards_users_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Users

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
            "username": "string", required
            "uuid_dashboard": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dashboards_users_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/dashboards/bulk/create/users', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def dashboards_users_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Users

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "username": "string", required
            "uuid_dashboard": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dashboards/bulk/delete/users', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def dashboards_widgets_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Widgets

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
            warning_wrong_parameters(self.dashboards_widgets_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/dashboards/bulk/create/widgets', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def dashboards_widgets_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Widgets

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
            f'/dashboards/bulk/delete/widgets', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response
