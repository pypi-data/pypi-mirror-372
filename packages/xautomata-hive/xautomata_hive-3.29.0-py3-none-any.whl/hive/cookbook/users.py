from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Users(ApiManager):
    """Class that handles all the XAutomata users APIs"""

    def users_register_create(self, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Registration Form

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            app_id (string optional): additional filter - parameter
            password (string required): additional filter - payload
            name (string required): additional filter - payload
            email (string required): additional filter - payload
            phone (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['password', 'name', 'email', 'phone']
        payload.get('password'), payload.get('name'), payload.get('email'
            ), payload.get('phone')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_register_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/users/register', params=
            params, payload=payload, **kwargs)
        return response

    def users_verify_email(self, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Verify Me

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            verification_code (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['verification_code']
        params.get('verification_code')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_verify_email.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/users/verify_email',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def users_password_reset_create(self, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Send Mail Password Reset

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            app_id (string optional): additional filter - parameter
            username (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['username']
        payload.get('username')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_password_reset_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/users/password_reset',
            params=params, payload=payload, **kwargs)
        return response

    def users_password_reset_put(self, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Reset Password

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            app_id (string optional): additional filter - parameter
            verification_code (string required): additional filter - payload
            new_password (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['verification_code', 'new_password']
        payload.get('verification_code'), payload.get('new_password')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_password_reset_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/users/password_reset',
            params=params, payload=payload, **kwargs)
        return response

    def users(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Users

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
            active (boolean optional): additional filter - parameter
            email (string optional): additional filter - parameter
            phone (string optional): additional filter - parameter
            profile (string optional): additional filter - parameter
            uuid_acl_override (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'name', 'active',
            'email', 'phone', 'profile', 'uuid_acl_override', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('name'
            ), params.get('active'), params.get('email'), params.get('phone'
            ), params.get('profile'), params.get('uuid_acl_override'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/users/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def users_create(self, kwargs: dict = None, **payload) -> list:
        """Create User

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            password (string required): additional filter - payload
            phone (string optional): additional filter - payload
            profile (string optional): additional filter - payload
            name (string required): additional filter - payload
            email (string required): additional filter - payload
            active (boolean required): additional filter - payload
            acl (object required): additional filter - payload
            uuid_acl_override (string optional): additional filter - payload
            verified_email (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['password', 'phone', 'profile', 'name',
            'email', 'active', 'acl', 'uuid_acl_override', 'verified_email']
        payload.get('password'), payload.get('phone'), payload.get('profile'
            ), payload.get('name'), payload.get('email'), payload.get('active'
            ), payload.get('acl'), payload.get('uuid_acl_override'
            ), payload.get('verified_email')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/users/', payload=payload,
            **kwargs)
        return response

    def users_create_uuid_customer(self, uuid_customer: str,
        params: dict = False, kwargs: dict = None, **payload) -> list:
        """Create User Tenant

        Args:
            params (dict, optional): additional parameters for the API.
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            send_mail (boolean optional): additional filter - parameter
            phone (string optional): additional filter - payload
            profile (string optional): additional filter - payload
            name (string required): additional filter - payload
            email (string required): additional filter - payload
            active (boolean required): additional filter - payload
            acl (object required): additional filter - payload
            uuid_acl_override (string optional): additional filter - payload
            verified_email (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['phone', 'profile', 'name', 'email',
            'active', 'acl', 'uuid_acl_override', 'verified_email']
        payload.get('phone'), payload.get('profile'), payload.get('name'
            ), payload.get('email'), payload.get('active'), payload.get('acl'
            ), payload.get('uuid_acl_override'), payload.get('verified_email')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/users/{uuid_customer}',
            params=params, payload=payload, **kwargs)
        return response

    def user(self, name: str, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Read User

        Args:
            name (str, required): name
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/users/{name}', warm_start=
            warm_start, **kwargs)
        return response

    def users_put(self, name: str, kwargs: dict = None, **payload) -> list:
        """Update User

        Args:
            name (str, required): name
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            password (string optional): additional filter - payload
            phone (string optional): additional filter - payload
            profile (string optional): additional filter - payload
            email (string optional): additional filter - payload
            stage (string optional): additional filter - payload
            active (boolean optional): additional filter - payload
            acl (object optional): additional filter - payload
            uuid_acl_override (string optional): additional filter - payload
            verified_email (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['password', 'phone', 'profile', 'email',
            'stage', 'active', 'acl', 'uuid_acl_override', 'verified_email']
        payload.get('password'), payload.get('phone'), payload.get('profile'
            ), payload.get('email'), payload.get('stage'), payload.get('active'
            ), payload.get('acl'), payload.get('uuid_acl_override'
            ), payload.get('verified_email')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/users/{name}', payload=
            payload, **kwargs)
        return response

    def users_delete(self, name: str, kwargs: dict = None) -> list:
        """Delete User

        Args:
            name (str, required): name
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/users/{name}', **kwargs)
        return response

    def users_dashboards(self, name: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Dashboards

        Args:
            name (str, required): name
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            dashboard_name (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'dashboard_name', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('not_in'), params.get('dashboard_name'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_dashboards.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/users/{name}/dashboards',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def users_dashboards_create(self, name: str, uuid_dashboard: str,
        kwargs: dict = None) -> list:
        """Add Dashboard

        Args:
            name (str, required): name
            uuid_dashboard (str, required): uuid_dashboard
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/{name}/dashboards/{uuid_dashboard}', **kwargs)
        return response

    def users_dashboards_delete(self, name: str, uuid_dashboard: str,
        kwargs: dict = None) -> list:
        """Remove Dashboard

        Args:
            name (str, required): name
            uuid_dashboard (str, required): uuid_dashboard
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users/{name}/dashboards/{uuid_dashboard}', **kwargs)
        return response

    def users_groups(self, name: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Groups

        Args:
            name (str, required): name
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            group_name (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'group_name', 'status', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('group_name'), params.get('status'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_groups.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/users/{name}/groups',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def users_groups_create(self, name: str, uuid_group: str,
        kwargs: dict = None) -> list:
        """Add Group

        Args:
            name (str, required): name
            uuid_group (str, required): uuid_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/{name}/groups/{uuid_group}', **kwargs)
        return response

    def users_groups_delete(self, name: str, uuid_group: str,
        kwargs: dict = None) -> list:
        """Remove Group

        Args:
            name (str, required): name
            uuid_group (str, required): uuid_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users/{name}/groups/{uuid_group}', **kwargs)
        return response

    def users_virtual_domains(self, name: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Virtual Domains

        Args:
            name (str, required): name
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            domain_code (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'domain_code', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('not_in'), params.get('domain_code'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_virtual_domains.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/users/{name}/virtual_domains', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def users_virtual_domains_create(self, name: str,
        uuid_virtual_domain: str, kwargs: dict = None) -> list:
        """Add Virtual Domain

        Args:
            name (str, required): name
            uuid_virtual_domain (str, required): uuid_virtual_domain
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/{name}/virtual_domains/{uuid_virtual_domain}', **kwargs)
        return response

    def users_virtual_domains_delete(self, name: str,
        uuid_virtual_domain: str, kwargs: dict = None) -> list:
        """Remove Virtual Domain

        Args:
            name (str, required): name
            uuid_virtual_domain (str, required): uuid_virtual_domain
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users/{name}/virtual_domains/{uuid_virtual_domain}', **kwargs)
        return response

    def users_customers(self, name: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Customers

        Args:
            name (str, required): name
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            company_name (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'company_name', 'status', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('company_name'), params.get('status'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_customers.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/users/{name}/customers',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def users_customers_create(self, name: str, uuid_customer: str,
        kwargs: dict = None) -> list:
        """Add Customer

        Args:
            name (str, required): name
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/{name}/customers/{uuid_customer}', **kwargs)
        return response

    def users_customers_delete(self, name: str, uuid_customer: str,
        kwargs: dict = None) -> list:
        """Remove Customer

        Args:
            name (str, required): name
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users/{name}/customers/{uuid_customer}', **kwargs)
        return response

    def users_starred_customers(self, name: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Starred Customers

        Args:
            name (str, required): name
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            status (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'status', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('not_in'), params.get('status'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_starred_customers.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/users/{name}/starred_customers', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def users_starred_customers_create(self, name: str, uuid_customer: str,
        kwargs: dict = None) -> list:
        """Mark Customer As Starred

        Args:
            name (str, required): name
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/{name}/starred_customers/{uuid_customer}', **kwargs)
        return response

    def users_starred_customers_delete(self, name: str, uuid_customer: str,
        kwargs: dict = None) -> list:
        """Mark Customer As Not Starred

        Args:
            name (str, required): name
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users/{name}/starred_customers/{uuid_customer}', **kwargs)
        return response

    def users_widget_groups(self, name: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Widget Groups

        Args:
            name (str, required): name
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            group_name (string optional): additional filter - parameter
            active (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'group_name', 'active', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('group_name'), params.get('active'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_widget_groups.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/users/{name}/widget_groups',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def users_widget_groups_create(self, name: str, uuid_widget_group: str,
        kwargs: dict = None) -> list:
        """Create Wg Relation

        Args:
            name (str, required): name
            uuid_widget_group (str, required): uuid_widget_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/{name}/widget_groups/{uuid_widget_group}', **kwargs)
        return response

    def users_widget_groups_delete(self, name: str, uuid_widget_group: str,
        kwargs: dict = None) -> list:
        """Mark Customer As Not Starred

        Args:
            name (str, required): name
            uuid_widget_group (str, required): uuid_widget_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users/{name}/widget_groups/{uuid_widget_group}', **kwargs)
        return response

    def users_cost_views(self, name: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List User Cost Views

        Args:
            name (str, required): name
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
            warning_wrong_parameters(self.users_cost_views.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/users/{name}/cost_views',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def users_cost_views_create(self, name: str, uuid: str, kwargs: dict = None
        ) -> list:
        """Create Association With Cost View

        Args:
            name (str, required): name
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/{name}/cost_views/{uuid}', **kwargs)
        return response

    def users_cost_views_delete(self, name: str, uuid: str, kwargs: dict = None
        ) -> list:
        """Delete Association With User

        Args:
            name (str, required): name
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/users/{name}/cost_views/{uuid}', **kwargs)
        return response

    def users_customers_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Customers

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
            "uuid_customer": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_customers_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/users/bulk/create/customers', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def users_customers_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Customers

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
            "uuid_customer": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/bulk/delete/customers', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def users_groups_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Groups

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
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_groups_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/users/bulk/create/groups',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def users_groups_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Groups

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
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/users/bulk/delete/groups',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def users_dashboards_create_bulk(self, payload: list,
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
            warning_wrong_parameters(self.users_dashboards_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/users/bulk/create/dashboards', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def users_dashboards_delete_bulk(self, payload: list,
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
           {
            "username": "string", required
            "uuid_dashboard": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/bulk/delete/dashboards', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def users_virtual_domains_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Virtual Domains

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
            "uuid_virtual_domain": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_virtual_domains_create_bulk
                .__name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/users/bulk/create/virtual_domains', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def users_virtual_domains_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Virtual Domains

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
            "uuid_virtual_domain": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/users/bulk/delete/virtual_domains', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def users_send_email_template_create(self, template_name: str,
        kwargs: dict = None, **payload) -> list:
        """Send Email Template

        Args:
            template_name (str, required): template_name
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            subject (string required): additional filter - payload
            recipients (array required): additional filter - payload
            ccn_recipients (array optional): additional filter - payload
            attachments (array optional): additional filter - payload
            template_parameters (object optional): additional filter - payload
            domain (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['subject', 'recipients', 'ccn_recipients',
            'attachments', 'template_parameters', 'domain']
        payload.get('subject'), payload.get('recipients'), payload.get(
            'ccn_recipients'), payload.get('attachments'), payload.get(
            'template_parameters'), payload.get('domain')
        if not self._silence_warning:
            warning_wrong_parameters(self.users_send_email_template_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=
            f'/users/send_email_template/{template_name}', payload=payload,
            **kwargs)
        return response
