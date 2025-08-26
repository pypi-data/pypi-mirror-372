from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class UsersNotifications(ApiManager):
    """Class that handles all the XAutomata users_notifications APIs"""

    def users_notifications(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Notifications

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            username (string optional): additional filter - parameter
            title (string optional): additional filter - parameter
            body (string optional): additional filter - parameter
            read (boolean optional): additional filter - parameter
            sent (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'username',
            'title', 'body', 'read', 'sent', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('username'
            ), params.get('title'), params.get('body'), params.get('read'
            ), params.get('sent'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_notifications.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/users_notifications/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def users_notifications_create(self, kwargs: dict = None, **payload
        ) -> list:
        """Create Notification

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            username (string required): additional filter - payload
            title (string required): additional filter - payload
            body (array object optional): additional filter - payload
            read (boolean optional): additional filter - payload
            sent (boolean optional): additional filter - payload
            timestamp (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['username', 'title', 'body', 'read',
            'sent', 'timestamp']
        payload.get('username'), payload.get('title'), payload.get('body'
            ), payload.get('read'), payload.get('sent'), payload.get(
            'timestamp')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_notifications_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/users_notifications/',
            payload=payload, **kwargs)
        return response

    def users_notifications_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Notification

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            title (string optional): additional filter - payload
            body (array object optional): additional filter - payload
            read (boolean optional): additional filter - payload
            sent (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['title', 'body', 'read', 'sent']
        payload.get('title'), payload.get('body'), payload.get('read'
            ), payload.get('sent')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_notifications_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/users_notifications/{uuid}',
            payload=payload, **kwargs)
        return response

    def users_notifications_delete(self, uuid: str, kwargs: dict = None
        ) -> list:
        """Delete Notifcation

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users_notifications/{uuid}', **kwargs)
        return response

    def users_notifications_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Create Bulk Notification

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
            "title": "string", required
            "body": "array object", optional
            "read": "boolean", optional
            "sent": "boolean", optional
            "timestamp": "string", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_notifications_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/users_notifications/bulk/create/', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response
