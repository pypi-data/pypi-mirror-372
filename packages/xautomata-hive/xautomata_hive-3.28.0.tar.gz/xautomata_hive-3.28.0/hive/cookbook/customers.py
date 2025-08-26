from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Customers(ApiManager):
    """Class that handles all the XAutomata customers APIs"""

    def customers(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Get Customers

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            code (string optional): additional filter - parameter
            company_name (string optional): additional filter - parameter
            address (string optional): additional filter - parameter
            zip_code (string optional): additional filter - parameter
            city (string optional): additional filter - parameter
            country (string optional): additional filter - parameter
            notes (string optional): additional filter - parameter
            vat_id (string optional): additional filter - parameter
            currency (string optional): additional filter - parameter
            state_province (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            registration_date (string optional): additional filter - parameter
            paying_customer (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'type', 'code',
            'company_name', 'address', 'zip_code', 'city', 'country',
            'notes', 'vat_id', 'currency', 'state_province', 'status',
            'registration_date', 'paying_customer', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('type'
            ), params.get('code'), params.get('company_name'), params.get(
            'address'), params.get('zip_code'), params.get('city'), params.get(
            'country'), params.get('notes'), params.get('vat_id'), params.get(
            'currency'), params.get('state_province'), params.get('status'
            ), params.get('registration_date'), params.get('paying_customer'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/customers/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def customers_create(self, kwargs: dict = None, **payload) -> list:
        """Create Customer

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            type (string optional): additional filter - payload
            code (string required): additional filter - payload
            company_name (string required): additional filter - payload
            address (string required): additional filter - payload
            zip_code (string required): additional filter - payload
            city (string required): additional filter - payload
            country (string required): additional filter - payload
            notes (string optional): additional filter - payload
            vat_id (string optional): additional filter - payload
            currency (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            status (string required): additional filter - payload
            profile (string optional): additional filter - payload
            registration_date (string optional): additional filter - payload
            paying_customer (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['type', 'code', 'company_name', 'address',
            'zip_code', 'city', 'country', 'notes', 'vat_id', 'currency',
            'state_province', 'status', 'profile', 'registration_date',
            'paying_customer']
        payload.get('type'), payload.get('code'), payload.get('company_name'
            ), payload.get('address'), payload.get('zip_code'), payload.get(
            'city'), payload.get('country'), payload.get('notes'), payload.get(
            'vat_id'), payload.get('currency'), payload.get('state_province'
            ), payload.get('status'), payload.get('profile'), payload.get(
            'registration_date'), payload.get('paying_customer')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/customers/', payload=
            payload, **kwargs)
        return response

    def customer(self, uuid: str, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Read Customer

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/customers/{uuid}',
            warm_start=warm_start, **kwargs)
        return response

    def customers_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Customer

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            type (string optional): additional filter - payload
            code (string optional): additional filter - payload
            company_name (string optional): additional filter - payload
            address (string optional): additional filter - payload
            zip_code (string optional): additional filter - payload
            city (string optional): additional filter - payload
            country (string optional): additional filter - payload
            notes (string optional): additional filter - payload
            vat_id (string optional): additional filter - payload
            currency (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            status (string optional): additional filter - payload
            profile (string optional): additional filter - payload
            registration_date (string optional): additional filter - payload
            paying_customer (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['type', 'code', 'company_name', 'address',
            'zip_code', 'city', 'country', 'notes', 'vat_id', 'currency',
            'state_province', 'status', 'profile', 'registration_date',
            'paying_customer']
        payload.get('type'), payload.get('code'), payload.get('company_name'
            ), payload.get('address'), payload.get('zip_code'), payload.get(
            'city'), payload.get('country'), payload.get('notes'), payload.get(
            'vat_id'), payload.get('currency'), payload.get('state_province'
            ), payload.get('status'), payload.get('profile'), payload.get(
            'registration_date'), payload.get('paying_customer')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/customers/{uuid}', payload=
            payload, **kwargs)
        return response

    def customers_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Customer

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/customers/{uuid}', **kwargs)
        return response

    def customers_register_create(self, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Registration Form

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            app_id (string optional): additional filter - parameter
            vat_id (string required): additional filter - payload
            company_name (string required): additional filter - payload
            address (string required): additional filter - payload
            zip_code (string required): additional filter - payload
            city (string required): additional filter - payload
            country (string required): additional filter - payload
            state_province (string optional): additional filter - payload
            currency (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['vat_id', 'company_name', 'address',
            'zip_code', 'city', 'country', 'state_province', 'currency']
        payload.get('vat_id'), payload.get('company_name'), payload.get(
            'address'), payload.get('zip_code'), payload.get('city'
            ), payload.get('country'), payload.get('state_province'
            ), payload.get('currency')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_register_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/customers/register/',
            params=params, payload=payload, **kwargs)
        return response

    def customers_relation_request_create(self, uuid_customer: str,
        kwargs: dict = None, **params) -> list:
        """Create Relation Request

        Args:
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            app_id (string optional): additional filter - parameter
            refresh (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['app_id', 'refresh']
        params.get('app_id'), params.get('refresh')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_relation_request_create
                .__name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/customers/relation_request/{uuid_customer}', params=params,
            **kwargs)
        return response

    def customers_relation_request_verify_create(self,
        verification_code: str, kwargs: dict = None) -> list:
        """Verify Relation Request

        Args:
            verification_code (str, required): verification_code
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/customers/relation_request/verify/{verification_code}', **kwargs
            )
        return response

    def customers_groups(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Groups

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            uuid_parent (string optional): additional filter - parameter
            uuid_site (string optional): additional filter - parameter
            uuid_virtual_domain (string optional): additional filter - parameter
            object_profile (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'uuid_parent',
            'uuid_site', 'uuid_virtual_domain', 'object_profile', 'type',
            'name', 'description', 'status', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'uuid_parent'), params.get('uuid_site'), params.get(
            'uuid_virtual_domain'), params.get('object_profile'), params.get(
            'type'), params.get('name'), params.get('description'), params.get(
            'status'), params.get('skip'), params.get('limit'), params.get(
            'like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_groups.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/customers/{uuid}/groups/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_image(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Get Customer Image

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/customers/{uuid}/image',
            warm_start=warm_start, **kwargs)
        return response

    def customers_image_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Customer Image

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
            warning_wrong_parameters(self.customers_image_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/customers/{uuid}/image',
            payload=payload, **kwargs)
        return response

    def customers_services(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Services

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_services.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/customers/{uuid}/services',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_service_profiles(self, uuid: str,
        warm_start: bool = False, kwargs: dict = None, **params) -> list:
        """List Services

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['not_in']
        params.get('not_in')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_service_profiles.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/customers/{uuid}/service_profiles', warm_start=warm_start,
            params=params, **kwargs)
        return response

    def customers_retention_rules(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Retention Rules

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_retention_rules.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/customers/{uuid}/retention_rules', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def customers_sites(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Sites

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            not_in (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_sites.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/customers/{uuid}/sites',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_contacts(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Contacts

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
            type (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'type', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('not_in'), params.get('name'), params.get('type'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_contacts.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/customers/{uuid}/contacts',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_contacts_create(self, uuid: str, uuid_contact: str,
        kwargs: dict = None, **payload) -> list:
        """Add Contact

        Args:
            uuid (str, required): uuid
            uuid_contact (str, required): uuid_contact
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            type (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['type']
        payload.get('type')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_contacts_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=
            f'/customers/{uuid}/contacts/{uuid_contact}', payload=payload,
            **kwargs)
        return response

    def customers_contacts_put(self, uuid: str, uuid_contact: str,
        kwargs: dict = None, **payload) -> list:
        """Update Contact

        Args:
            uuid (str, required): uuid
            uuid_contact (str, required): uuid_contact
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            type (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['type']
        payload.get('type')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_contacts_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=
            f'/customers/{uuid}/contacts/{uuid_contact}', payload=payload,
            **kwargs)
        return response

    def customers_contacts_delete(self, uuid: str, uuid_contact: str,
        kwargs: dict = None) -> list:
        """Remove Contact

        Args:
            uuid (str, required): uuid
            uuid_contact (str, required): uuid_contact
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/customers/{uuid}/contacts/{uuid_contact}', **kwargs)
        return response

    def customers_users(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.customers_users.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/customers/{uuid}/users',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_users_create(self, uuid: str, name: str, kwargs: dict = None
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
            f'/customers/{uuid}/users/{name}', **kwargs)
        return response

    def customers_users_delete(self, uuid: str, name: str, kwargs: dict = None
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
            f'/customers/{uuid}/users/{name}', **kwargs)
        return response

    def customers_with_dashboard(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Get Customers With Dashboard

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            type (string optional): additional filter - parameter
            code (string optional): additional filter - parameter
            company_name (string optional): additional filter - parameter
            address (string optional): additional filter - parameter
            zip_code (string optional): additional filter - parameter
            city (string optional): additional filter - parameter
            country (string optional): additional filter - parameter
            notes (string optional): additional filter - parameter
            vat_id (string optional): additional filter - parameter
            currency (string optional): additional filter - parameter
            state_province (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            starred (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'type', 'code', 'company_name',
            'address', 'zip_code', 'city', 'country', 'notes', 'vat_id',
            'currency', 'state_province', 'status', 'starred', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('type'), params.get('code'
            ), params.get('company_name'), params.get('address'), params.get(
            'zip_code'), params.get('city'), params.get('country'), params.get(
            'notes'), params.get('vat_id'), params.get('currency'), params.get(
            'state_province'), params.get('status'), params.get('starred'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_with_dashboard.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/customers/with_dashboard/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_by_vat(self, vat_id: str, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Get Customer By Vat Id

        Args:
            vat_id (str, required): vat_id
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/customers/by_vat/{vat_id}',
            warm_start=warm_start, **kwargs)
        return response

    def customers_dashboards(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.customers_dashboards.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/customers/{uuid}/dashboards',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_dashboards_create(self, uuid: str, uuid_dashboard: str,
        kwargs: dict = None) -> list:
        """Create Customer Dashboard Association

        Args:
            uuid (str, required): uuid
            uuid_dashboard (str, required): uuid_dashboard
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/customers/{uuid}/dashboards/{uuid_dashboard}', **kwargs)
        return response

    def customers_dashboards_delete(self, uuid: str, uuid_dashboard: str,
        kwargs: dict = None) -> list:
        """Remove Customer Dashboard Association

        Args:
            uuid (str, required): uuid
            uuid_dashboard (str, required): uuid_dashboard
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/customers/{uuid}/dashboards/{uuid_dashboard}', **kwargs)
        return response

    def customers_downtimes(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Downtimes

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
            warning_wrong_parameters(self.customers_downtimes.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/customers/{uuid}/downtimes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_dispatchers(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Dispatchers

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
            warning_wrong_parameters(self.customers_dispatchers.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/customers/{uuid}/dispatchers', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def customers_bulk(self, payload: list, warm_start: bool = False,
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
            warning_wrong_parameters(self.customers_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/customers/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def customers_read_by_bulk(self, payload: list,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Read By Code

        Args:
            payload (list[dict], optional): List dict to create.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
            "code": "string", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/customers/bulk/read_by/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, payload=payload, **kwargs)
        return response

    def customers_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Create Customers

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
            "type": "string", optional
            "code": "string", required
            "company_name": "string", required
            "address": "string", required
            "zip_code": "string", required
            "city": "string", required
            "country": "string", required
            "notes": "string", optional
            "vat_id": "string", optional
            "currency": "string", optional
            "state_province": "string", optional
            "status": "string", required
            "profile": "string", optional
            "registration_date": "string", optional
            "paying_customer": "boolean", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/customers/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def customers_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Delete Customers

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
        response = self.execute('POST', path=f'/customers/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def customers_contacts_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Contacts

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
            "uuid_contact": "string", required
            "uuid_customer": "string", required
            "type": "string", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_contacts_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/customers/bulk/create/contacts', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def customers_contacts_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Contacts

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "uuid_contact": "string", required
            "uuid_customer": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/customers/bulk/delete/contacts', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def customers_users_create_bulk(self, payload: list,
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
            "uuid_customer": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_users_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/customers/bulk/create/users', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def customers_users_delete_bulk(self, payload: list,
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
            "uuid_customer": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/customers/bulk/delete/users', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def customers_azure_v2_create(self, kwargs: dict = None, **payload
        ) -> list:
        """Create Azure Customer V2

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            customer (None required): additional filter - payload
            azure_customer (None required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['customer', 'azure_customer']
        payload.get('customer'), payload.get('azure_customer')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_azure_v2_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/customers/azure/v2/',
            payload=payload, **kwargs)
        return response

    def customers_azure_v2_subscription_create(self, kwargs: dict = None,
        **payload) -> list:
        """Create Azure Customer Sub

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            customer (None required): additional filter - payload
            azure_customer (None required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['customer', 'azure_customer']
        payload.get('customer'), payload.get('azure_customer')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                customers_azure_v2_subscription_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=
            f'/customers/azure/v2/subscription/', payload=payload, **kwargs)
        return response

    def customers_azure_v2_create_uuid(self, uuid: str, kwargs: dict = None,
        **payload) -> list:
        """Create Azure Customer From V2

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            target_company (string required): additional filter - payload
            target_code (string required): additional filter - payload
            address (string optional): additional filter - payload
            zip_code (string optional): additional filter - payload
            city (string optional): additional filter - payload
            country (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            paying_customer (boolean optional): additional filter - payload
            base_margin (number required): additional filter - payload
            reserved_margin (number required): additional filter - payload
            azure_customer_id (string required): additional filter - payload
            uuid_virtual_domain (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['target_company', 'target_code', 'address',
            'zip_code', 'city', 'country', 'state_province',
            'paying_customer', 'base_margin', 'reserved_margin',
            'azure_customer_id', 'uuid_virtual_domain']
        payload.get('target_company'), payload.get('target_code'), payload.get(
            'address'), payload.get('zip_code'), payload.get('city'
            ), payload.get('country'), payload.get('state_province'
            ), payload.get('paying_customer'), payload.get('base_margin'
            ), payload.get('reserved_margin'), payload.get('azure_customer_id'
            ), payload.get('uuid_virtual_domain')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_azure_v2_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/customers/azure/v2/{uuid}',
            payload=payload, **kwargs)
        return response

    def customers_azure_v2_subscription_create_uuid(self, uuid: str,
        kwargs: dict = None, **payload) -> list:
        """Create Azure Customer From V2 Sub

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            target_company (string required): additional filter - payload
            target_code (string required): additional filter - payload
            address (string optional): additional filter - payload
            zip_code (string optional): additional filter - payload
            city (string optional): additional filter - payload
            country (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            paying_customer (boolean optional): additional filter - payload
            uuid_virtual_domain (string optional): additional filter - payload
            uuid_probe_type (string optional): additional filter - payload
            uuid_object (string optional): additional filter - payload
            subscriptions (array required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['target_company', 'target_code', 'address',
            'zip_code', 'city', 'country', 'state_province',
            'paying_customer', 'uuid_virtual_domain', 'uuid_probe_type',
            'uuid_object', 'subscriptions']
        payload.get('target_company'), payload.get('target_code'), payload.get(
            'address'), payload.get('zip_code'), payload.get('city'
            ), payload.get('country'), payload.get('state_province'
            ), payload.get('paying_customer'), payload.get(
            'uuid_virtual_domain'), payload.get('uuid_probe_type'
            ), payload.get('uuid_object'), payload.get('subscriptions')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                customers_azure_v2_subscription_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=
            f'/customers/azure/v2/subscription/{uuid}', payload=payload, **
            kwargs)
        return response

    def customers_aws_v2_subscription_create(self, kwargs: dict = None, **
        payload) -> list:
        """Create Aws Customer Sub

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            customer (None required): additional filter - payload
            aws_customer (None required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['customer', 'aws_customer']
        payload.get('customer'), payload.get('aws_customer')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                customers_aws_v2_subscription_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=
            f'/customers/aws/v2/subscription/', payload=payload, **kwargs)
        return response

    def customers_aws_v2_subscription_create_uuid(self, uuid: str,
        kwargs: dict = None, **payload) -> list:
        """Create Aws Customer From V2 Sub

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            target_company (string required): additional filter - payload
            target_code (string required): additional filter - payload
            address (string optional): additional filter - payload
            zip_code (string optional): additional filter - payload
            city (string optional): additional filter - payload
            country (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            paying_customer (boolean optional): additional filter - payload
            uuid_virtual_domain (string optional): additional filter - payload
            uuid_probe_type (string optional): additional filter - payload
            uuid_object (string optional): additional filter - payload
            subscriptions (array required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['target_company', 'target_code', 'address',
            'zip_code', 'city', 'country', 'state_province',
            'paying_customer', 'uuid_virtual_domain', 'uuid_probe_type',
            'uuid_object', 'subscriptions']
        payload.get('target_company'), payload.get('target_code'), payload.get(
            'address'), payload.get('zip_code'), payload.get('city'
            ), payload.get('country'), payload.get('state_province'
            ), payload.get('paying_customer'), payload.get(
            'uuid_virtual_domain'), payload.get('uuid_probe_type'
            ), payload.get('uuid_object'), payload.get('subscriptions')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                customers_aws_v2_subscription_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=
            f'/customers/aws/v2/subscription/{uuid}', payload=payload, **kwargs
            )
        return response

    def customers_gcp_v2_subscription_create(self, kwargs: dict = None, **
        payload) -> list:
        """Create Gcp Customer Sub

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            customer (None required): additional filter - payload
            gcp_customer (None required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['customer', 'gcp_customer']
        payload.get('customer'), payload.get('gcp_customer')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                customers_gcp_v2_subscription_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=
            f'/customers/gcp/v2/subscription/', payload=payload, **kwargs)
        return response

    def customers_gcp_v2_subscription_create_uuid(self, uuid: str,
        kwargs: dict = None, **payload) -> list:
        """Create Gcp Customer From V2 Sub

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            target_company (string required): additional filter - payload
            target_code (string required): additional filter - payload
            address (string optional): additional filter - payload
            zip_code (string optional): additional filter - payload
            city (string optional): additional filter - payload
            country (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            paying_customer (boolean optional): additional filter - payload
            uuid_virtual_domain (string optional): additional filter - payload
            uuid_probe_type (string optional): additional filter - payload
            uuid_object (string optional): additional filter - payload
            subscriptions (array required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['target_company', 'target_code', 'address',
            'zip_code', 'city', 'country', 'state_province',
            'paying_customer', 'uuid_virtual_domain', 'uuid_probe_type',
            'uuid_object', 'subscriptions']
        payload.get('target_company'), payload.get('target_code'), payload.get(
            'address'), payload.get('zip_code'), payload.get('city'
            ), payload.get('country'), payload.get('state_province'
            ), payload.get('paying_customer'), payload.get(
            'uuid_virtual_domain'), payload.get('uuid_probe_type'
            ), payload.get('uuid_object'), payload.get('subscriptions')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                customers_gcp_v2_subscription_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=
            f'/customers/gcp/v2/subscription/{uuid}', payload=payload, **kwargs
            )
        return response

    def customers_networks(self, uuid_customer: str,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Query Networks By Customer

        Args:
            uuid_customer (str, required): uuid_customer
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            uuid_object (string optional): additional filter - parameter
            country (string optional): additional filter - parameter
            city (string optional): additional filter - parameter
            address (string optional): additional filter - parameter
            zip_code (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            name (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'uuid_object',
            'country', 'city', 'address', 'zip_code', 'status',
            'description', 'name', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'uuid_object'), params.get('country'), params.get('city'
            ), params.get('address'), params.get('zip_code'), params.get(
            'status'), params.get('description'), params.get('name'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_networks.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/customers/networks/{uuid_customer}', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def customers_it_availability(self, uuid_customer: str,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Query It Availability By Customer

        Args:
            uuid_customer (str, required): uuid_customer
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            timestamp_start (string required): additional filter - parameter
            timestamp_end (string required): additional filter - parameter
            active_objects_only (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['timestamp_start', 'timestamp_end',
            'active_objects_only', 'skip', 'limit', 'like', 'join', 'count']
        params.get('timestamp_start'), params.get('timestamp_end'), params.get(
            'active_objects_only'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_it_availability.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/customers/it_availability/{uuid_customer}', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def customers_it_availability_history(self, uuid_customer: str,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Query It Availability History By Customer

        Args:
            uuid_customer (str, required): uuid_customer
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            timestamp_start (string required): additional filter - parameter
            timestamp_end (string required): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['timestamp_start', 'timestamp_end', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('timestamp_start'), params.get('timestamp_end'), params.get(
            'skip'), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_it_availability_history
                .__name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/customers/it_availability_history/{uuid_customer}',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_acknowledged(self, uuid_customer: str,
        warm_start: bool = False, kwargs: dict = None, **params) -> list:
        """Consume Acknowledged Log

        Args:
            uuid_customer (str, required): uuid_customer
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            offset (integer optional): additional filter - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['offset', 'limit']
        params.get('offset'), params.get('limit')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_acknowledged.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/customers/{uuid_customer}/acknowledged/', warm_start=
            warm_start, params=params, **kwargs)
        return response

    def customers_acknowledged_create(self, uuid_customer: str,
        kwargs: dict = None, **payload) -> list:
        """Produce Acknowledged Message

        Args:
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid (str required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid']
        payload.get('uuid')
        if not self._silence_warning:
            warning_wrong_parameters(self.customers_acknowledged_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=
            f'/customers/{uuid_customer}/acknowledged/', payload=payload,
            **kwargs)
        return response
