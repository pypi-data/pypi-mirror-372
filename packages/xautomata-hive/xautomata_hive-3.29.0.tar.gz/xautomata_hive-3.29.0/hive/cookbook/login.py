from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Login(ApiManager):
    """Class that handles all the XAutomata login APIs"""

    def login_access_token_create(self, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Login Access Token Oauth2

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            value_refresh_token (string optional): additional filter - parameter
            refresh (string optional): additional filter - parameter
            grant_type (string optional): additional filter - payload
            username (string required): additional filter - payload
            password (string required): additional filter - payload
            scope (string optional): additional filter - payload
            client_id (string optional): additional filter - payload
            client_secret (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['grant_type', 'username', 'password',
            'scope', 'client_id', 'client_secret']
        payload.get('grant_type'), payload.get('username'), payload.get(
            'password'), payload.get('scope'), payload.get('client_id'
            ), payload.get('client_secret')
        if not self._silence_warning:
            warning_wrong_parameters(self.login_access_token_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/login/access-token', params
            =params, payload=payload, **kwargs)
        return response

    def login_refresh_create(self, kwargs: dict = None, **params) -> list:
        """Refresh Token

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            refresh (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['refresh']
        params.get('refresh')
        if not self._silence_warning:
            warning_wrong_parameters(self.login_refresh_create.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/login/refresh', params=
            params, **kwargs)
        return response

    def login_refresh_invalidate_create(self, kwargs: dict = None, **params
        ) -> list:
        """Invalidate Token

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            refresh (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['refresh']
        params.get('refresh')
        if not self._silence_warning:
            warning_wrong_parameters(self.login_refresh_invalidate_create.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/login/refresh/invalidate',
            params=params, **kwargs)
        return response

    def login_refresh_invalidate_user_create(self, kwargs: dict = None, **
        params) -> list:
        """Invalidate User Tokens

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            username (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['username']
        params.get('username')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                login_refresh_invalidate_user_create.__name__, params,
                official_params_list)
        response = self.execute('POST', path=
            f'/login/refresh/invalidate_user', params=params, **kwargs)
        return response

    def login_refresh_invalidate_tokens_create(self, kwargs: dict = None
        ) -> list:
        """Invalidate User Tokens

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/login/refresh/invalidate_tokens', **kwargs)
        return response

    def login_current_user(self, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Get Current User

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/login/current_user',
            warm_start=warm_start, **kwargs)
        return response

    def login_current_user_put(self, kwargs: dict = None, **payload) -> list:
        """Update User

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            password (string optional): additional filter - payload
            phone (string optional): additional filter - payload
            profile (string optional): additional filter - payload
            email (string optional): additional filter - payload
            stage (string optional): additional filter - payload
            active (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['password', 'phone', 'profile', 'email',
            'stage', 'active']
        payload.get('password'), payload.get('phone'), payload.get('profile'
            ), payload.get('email'), payload.get('stage'), payload.get('active'
            )
        if not self._silence_warning:
            warning_wrong_parameters(self.login_current_user_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/login/current_user', payload
            =payload, **kwargs)
        return response

    def login_current_user_dashboards(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Get Current User

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('sort_by'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.login_current_user_dashboards.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/login/current_user/dashboards', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def login_current_user_image(self, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Get Image

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/login/current_user/image',
            warm_start=warm_start, **kwargs)
        return response

    def login_current_user_image_put(self, kwargs: dict = None, **payload
        ) -> list:
        """Update Image

        Args:
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
            warning_wrong_parameters(self.login_current_user_image_put.
                __name__, payload, official_payload_list)
        response = self.execute('PUT', path=f'/login/current_user/image',
            payload=payload, **kwargs)
        return response

    def login_current_user_push_tokens(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Tokens

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            token (string optional): additional filter - parameter
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['token', 'sort_by', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('token'), params.get('sort_by'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.login_current_user_push_tokens.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/login/current_user/push_tokens', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def login_current_user_push_tokens_create(self, kwargs: dict = None, **
        payload) -> list:
        """Create Or Update Token

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            token (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['token']
        payload.get('token')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                login_current_user_push_tokens_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=
            f'/login/current_user/push_tokens', payload=payload, **kwargs)
        return response

    def login_current_user_push_tokens_delete(self, token: str,
        kwargs: dict = None) -> list:
        """Delete Downtime

        Args:
            token (str, required): token
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/login/current_user/push_tokens/{token}', **kwargs)
        return response

    def login_current_user_notifications(self, warm_start: bool = False,
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
        official_params_list = ['sort_by', 'null_fields', 'title', 'body',
            'read', 'sent', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('title'
            ), params.get('body'), params.get('read'), params.get('sent'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.login_current_user_notifications.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/login/current_user/notifications', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def login_current_user_notifications_put(self, uuid: str,
        kwargs: dict = None) -> list:
        """Update Notification

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('PUT', path=
            f'/login/current_user/notifications/{uuid}', **kwargs)
        return response

    def login_current_user_notifications_delete(self, uuid: str,
        kwargs: dict = None) -> list:
        """Delete Notification

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/login/current_user/notifications/{uuid}', **kwargs)
        return response

    def login_current_user_notifications_put_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Set Read

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
            f'/login/current_user/notifications/bulk/update', single_page=
            single_page, page_size=page_size, payload=payload, **kwargs)
        return response

    def login_current_user_terms_and_conditions(self,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Check If User Approved Tc

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            tc_version (integer optional): additional filter - parameter
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['tc_version', 'sort_by', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('tc_version'), params.get('sort_by'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                login_current_user_terms_and_conditions.__name__, params,
                official_params_list)
        response = self.execute('GET', path=
            f'/login/current_user/terms_and_conditions', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def login_current_user_terms_and_conditions_create(self,
        kwargs: dict = None, **payload) -> list:
        """User Approved Or Declined Tc

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            tc_version (integer required): additional filter - payload
            accepted (boolean required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['tc_version', 'accepted']
        payload.get('tc_version'), payload.get('accepted')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                login_current_user_terms_and_conditions_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=
            f'/login/current_user/terms_and_conditions', payload=payload,
            **kwargs)
        return response

    def login_current_user_verify_email_create(self, kwargs: dict = None
        ) -> list:
        """Send Request To Verify Current User Email

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/login/current_user/verify_email', **kwargs)
        return response

    def login_current_user_verify_email_put(self, kwargs: dict = None, **params
        ) -> list:
        """Verify Current User Email

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            verification_code (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['verification_code']
        params.get('verification_code')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                login_current_user_verify_email_put.__name__, params,
                official_params_list)
        response = self.execute('PUT', path=
            f'/login/current_user/verify_email', params=params, **kwargs)
        return response
