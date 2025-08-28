from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Services(ApiManager):
    """Class that handles all the XAutomata services APIs"""

    def services(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Services

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            uuid_parent (string optional): additional filter - parameter
            uuid_customer (string optional): additional filter - parameter
            profile (string optional): additional filter - parameter
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
            'uuid_customer', 'profile', 'name', 'description', 'status',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'uuid_parent'), params.get('uuid_customer'), params.get('profile'
            ), params.get('name'), params.get('description'), params.get(
            'status'), params.get('skip'), params.get('limit'), params.get(
            'like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/services/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def services_create(self, kwargs: dict = None, **payload) -> list:
        """Create Service

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_parent (string optional): additional filter - payload
            uuid_customer (string required): additional filter - payload
            profile (string required): additional filter - payload
            name (string required): additional filter - payload
            description (string required): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            rule (array object optional): additional filter - payload
            status (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_parent', 'uuid_customer', 'profile',
            'name', 'description', 'automata_domain', 'rule', 'status']
        payload.get('uuid_parent'), payload.get('uuid_customer'), payload.get(
            'profile'), payload.get('name'), payload.get('description'
            ), payload.get('automata_domain'), payload.get('rule'
            ), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/services/', payload=payload,
            **kwargs)
        return response

    def service(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Service

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
            warning_wrong_parameters(self.service.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/services/{uuid}', warm_start
            =warm_start, params=params, **kwargs)
        return response

    def services_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Service

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_parent (string optional): additional filter - payload
            uuid_customer (string optional): additional filter - payload
            profile (string optional): additional filter - payload
            name (string optional): additional filter - payload
            description (string optional): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            rule (array object optional): additional filter - payload
            status (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_parent', 'uuid_customer', 'profile',
            'name', 'description', 'automata_domain', 'rule', 'status']
        payload.get('uuid_parent'), payload.get('uuid_customer'), payload.get(
            'profile'), payload.get('name'), payload.get('description'
            ), payload.get('automata_domain'), payload.get('rule'
            ), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/services/{uuid}', payload=
            payload, **kwargs)
        return response

    def services_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Service

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/services/{uuid}', **kwargs)
        return response

    def services_metrics(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Metrics

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
            status (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'status', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('not_in'), params.get('name'), params.get('status'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_metrics.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/services/{uuid}/metrics',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def services_metrics_create(self, uuid: str, uuid_metric: str,
        kwargs: dict = None) -> list:
        """Add Metric

        Args:
            uuid (str, required): uuid
            uuid_metric (str, required): uuid_metric
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/services/{uuid}/metrics/{uuid_metric}', **kwargs)
        return response

    def services_metrics_delete(self, uuid: str, uuid_metric: str,
        kwargs: dict = None) -> list:
        """Remove Metric

        Args:
            uuid (str, required): uuid
            uuid_metric (str, required): uuid_metric
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/services/{uuid}/metrics/{uuid_metric}', **kwargs)
        return response

    def services_downtimes(self, uuid: str, warm_start: bool = False,
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
            not_in (boolean optional): additional filter - parameter
            code (string optional): additional filter - parameter
            fetch_all (boolean optional): additional filter - parameter
            only_actives (boolean optional): additional filter - parameter
            active_at_timestamp (string optional): additional filter - parameter
            active_after_timestamp (string optional): additional filter - parameter
            active_at_or_after_timestamp (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'code', 'fetch_all',
            'only_actives', 'active_at_timestamp', 'active_after_timestamp',
            'active_at_or_after_timestamp', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('code'), params.get('fetch_all'
            ), params.get('only_actives'), params.get('active_at_timestamp'
            ), params.get('active_after_timestamp'), params.get(
            'active_at_or_after_timestamp'), params.get('skip'), params.get(
            'limit'), params.get('like'), params.get('join'), params.get(
            'count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_downtimes.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/services/{uuid}/downtimes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def services_downtimes_create(self, uuid: str, uuid_downtime: str,
        kwargs: dict = None) -> list:
        """Add Downtime

        Args:
            uuid (str, required): uuid
            uuid_downtime (str, required): uuid_downtime
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/services/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def services_downtimes_delete(self, uuid: str, uuid_downtime: str,
        kwargs: dict = None) -> list:
        """Remove Downtime

        Args:
            uuid (str, required): uuid
            uuid_downtime (str, required): uuid_downtime
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/services/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def services_dispatchers(self, uuid: str, warm_start: bool = False,
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
            not_in (boolean optional): additional filter - parameter
            code (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            fetch_all (boolean optional): additional filter - parameter
            only_actives (boolean optional): additional filter - parameter
            active_at_timestamp (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'code', 'status', 'fetch_all',
            'only_actives', 'active_at_timestamp', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('not_in'), params.get('code'), params.get('status'
            ), params.get('fetch_all'), params.get('only_actives'), params.get(
            'active_at_timestamp'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_dispatchers.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/services/{uuid}/dispatchers',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def services_dispatchers_create(self, uuid: str, uuid_dispatcher: str,
        kwargs: dict = None) -> list:
        """Add Dispatcher

        Args:
            uuid (str, required): uuid
            uuid_dispatcher (str, required): uuid_dispatcher
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/services/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def services_dispatchers_delete(self, uuid: str, uuid_dispatcher: str,
        kwargs: dict = None) -> list:
        """Remove Dispatcher

        Args:
            uuid (str, required): uuid
            uuid_dispatcher (str, required): uuid_dispatcher
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/services/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def services_query(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Service Query

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            uuid_customer (string optional): additional filter - parameter
            customer_code (string optional): additional filter - parameter
            customer_status (string optional): additional filter - parameter
            uuid_site (string optional): additional filter - parameter
            site_code (string optional): additional filter - parameter
            site_description (string optional): additional filter - parameter
            site_address (string optional): additional filter - parameter
            site_zip_code (string optional): additional filter - parameter
            site_city (string optional): additional filter - parameter
            site_country (string optional): additional filter - parameter
            site_state_province (string optional): additional filter - parameter
            site_status (string optional): additional filter - parameter
            uuid_group (string optional): additional filter - parameter
            group_name (string optional): additional filter - parameter
            group_status (string optional): additional filter - parameter
            group_type (string optional): additional filter - parameter
            uuid_object (string optional): additional filter - parameter
            object_name (string optional): additional filter - parameter
            object_status (string optional): additional filter - parameter
            object_profile (string optional): additional filter - parameter
            uuid_metric_type (string optional): additional filter - parameter
            metric_type_name (string optional): additional filter - parameter
            metric_type_status (string optional): additional filter - parameter
            uuid_metric (string optional): additional filter - parameter
            metric_name (string optional): additional filter - parameter
            metric_status (string optional): additional filter - parameter
            metric_profile (string optional): additional filter - parameter
            service_uuid_parent (string optional): additional filter - parameter
            uuid_service (string optional): additional filter - parameter
            service_profile (string optional): additional filter - parameter
            service_name (string optional): additional filter - parameter
            service_description (string optional): additional filter - parameter
            service_status (string optional): additional filter - parameter
            service_automata_domain (string optional): additional filter - parameter
            service_uuid_customer (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'uuid_customer',
            'customer_code', 'customer_status', 'uuid_site', 'site_code',
            'site_description', 'site_address', 'site_zip_code',
            'site_city', 'site_country', 'site_state_province',
            'site_status', 'uuid_group', 'group_name', 'group_status',
            'group_type', 'uuid_object', 'object_name', 'object_status',
            'object_profile', 'uuid_metric_type', 'metric_type_name',
            'metric_type_status', 'uuid_metric', 'metric_name',
            'metric_status', 'metric_profile', 'service_uuid_parent',
            'uuid_service', 'service_profile', 'service_name',
            'service_description', 'service_status',
            'service_automata_domain', 'service_uuid_customer', 'skip',
            'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'uuid_customer'), params.get('customer_code'), params.get(
            'customer_status'), params.get('uuid_site'), params.get('site_code'
            ), params.get('site_description'), params.get('site_address'
            ), params.get('site_zip_code'), params.get('site_city'
            ), params.get('site_country'), params.get('site_state_province'
            ), params.get('site_status'), params.get('uuid_group'), params.get(
            'group_name'), params.get('group_status'), params.get('group_type'
            ), params.get('uuid_object'), params.get('object_name'
            ), params.get('object_status'), params.get('object_profile'
            ), params.get('uuid_metric_type'), params.get('metric_type_name'
            ), params.get('metric_type_status'), params.get('uuid_metric'
            ), params.get('metric_name'), params.get('metric_status'
            ), params.get('metric_profile'), params.get('service_uuid_parent'
            ), params.get('uuid_service'), params.get('service_profile'
            ), params.get('service_name'), params.get('service_description'
            ), params.get('service_status'), params.get(
            'service_automata_domain'), params.get('service_uuid_customer'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_query.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/services/query/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def services_query_bulk(self, payload: dict = False,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Service Query Lists

        Args:
            payload (dict, optional): additional parameters for the API.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Examples:
            payload = 
           {
            "uuid_customer": "array", optional
            "customer_code": "array", optional
            "customer_status": "array", optional
            "uuid_site": "array", optional
            "site_code": "array", optional
            "site_description": "array", optional
            "site_address": "array", optional
            "site_zip_code": "array", optional
            "site_city": "array", optional
            "site_country": "array", optional
            "site_state_province": "array", optional
            "site_status": "array", optional
            "uuid_group": "array", optional
            "group_name": "array", optional
            "group_status": "array", optional
            "group_type": "array", optional
            "uuid_object": "array", optional
            "object_name": "array", optional
            "object_status": "array", optional
            "object_profile": "array", optional
            "uuid_metric_type": "array", optional
            "metric_type_name": "array", optional
            "metric_type_status": "array", optional
            "uuid_metric": "array", optional
            "metric_name": "array", optional
            "metric_status": "array", optional
            "metric_profile": "array", optional
            "service_uuid_parent": "array", optional
            "uuid_service": "array", optional
            "service_profile": "array", optional
            "service_name": "array", optional
            "service_description": "array", optional
            "service_status": "array", optional
            "service_uuid_customer": "array", optional
           }

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_query_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/services/query/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def services_last_status_query(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Service Query Last Status

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            uuid_customer (string optional): additional filter - parameter
            customer_code (string optional): additional filter - parameter
            customer_status (string optional): additional filter - parameter
            uuid_site (string optional): additional filter - parameter
            site_code (string optional): additional filter - parameter
            site_description (string optional): additional filter - parameter
            site_address (string optional): additional filter - parameter
            site_zip_code (string optional): additional filter - parameter
            site_city (string optional): additional filter - parameter
            site_country (string optional): additional filter - parameter
            site_state_province (string optional): additional filter - parameter
            site_status (string optional): additional filter - parameter
            uuid_group (string optional): additional filter - parameter
            group_name (string optional): additional filter - parameter
            group_status (string optional): additional filter - parameter
            group_type (string optional): additional filter - parameter
            group_uuid_virtual_domain (string optional): additional filter - parameter
            uuid_object (string optional): additional filter - parameter
            object_name (string optional): additional filter - parameter
            object_status (string optional): additional filter - parameter
            object_profile (string optional): additional filter - parameter
            uuid_metric_type (string optional): additional filter - parameter
            metric_type_name (string optional): additional filter - parameter
            metric_type_status (string optional): additional filter - parameter
            uuid_metric (string optional): additional filter - parameter
            metric_name (string optional): additional filter - parameter
            metric_status (string optional): additional filter - parameter
            metric_profile (string optional): additional filter - parameter
            service_uuid_parent (string optional): additional filter - parameter
            uuid_service (string optional): additional filter - parameter
            service_profile (string optional): additional filter - parameter
            service_name (string optional): additional filter - parameter
            service_description (string optional): additional filter - parameter
            service_status (string optional): additional filter - parameter
            service_automata_domain (string optional): additional filter - parameter
            service_uuid_customer (string optional): additional filter - parameter
            timestamp_start (string optional): additional filter - parameter
            timestamp_end (string optional): additional filter - parameter
            database_timestamp_start (string optional): additional filter - parameter
            database_timestamp_end (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            ranking (integer optional): additional filter - parameter
            description (string optional): additional filter - parameter
            unit (string optional): additional filter - parameter
            value (number optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'uuid_customer',
            'customer_code', 'customer_status', 'uuid_site', 'site_code',
            'site_description', 'site_address', 'site_zip_code',
            'site_city', 'site_country', 'site_state_province',
            'site_status', 'uuid_group', 'group_name', 'group_status',
            'group_type', 'group_uuid_virtual_domain', 'uuid_object',
            'object_name', 'object_status', 'object_profile',
            'uuid_metric_type', 'metric_type_name', 'metric_type_status',
            'uuid_metric', 'metric_name', 'metric_status', 'metric_profile',
            'service_uuid_parent', 'uuid_service', 'service_profile',
            'service_name', 'service_description', 'service_status',
            'service_automata_domain', 'service_uuid_customer',
            'timestamp_start', 'timestamp_end', 'database_timestamp_start',
            'database_timestamp_end', 'status', 'ranking', 'description',
            'unit', 'value', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'uuid_customer'), params.get('customer_code'), params.get(
            'customer_status'), params.get('uuid_site'), params.get('site_code'
            ), params.get('site_description'), params.get('site_address'
            ), params.get('site_zip_code'), params.get('site_city'
            ), params.get('site_country'), params.get('site_state_province'
            ), params.get('site_status'), params.get('uuid_group'), params.get(
            'group_name'), params.get('group_status'), params.get('group_type'
            ), params.get('group_uuid_virtual_domain'), params.get(
            'uuid_object'), params.get('object_name'), params.get(
            'object_status'), params.get('object_profile'), params.get(
            'uuid_metric_type'), params.get('metric_type_name'), params.get(
            'metric_type_status'), params.get('uuid_metric'), params.get(
            'metric_name'), params.get('metric_status'), params.get(
            'metric_profile'), params.get('service_uuid_parent'), params.get(
            'uuid_service'), params.get('service_profile'), params.get(
            'service_name'), params.get('service_description'), params.get(
            'service_status'), params.get('service_automata_domain'
            ), params.get('service_uuid_customer'), params.get(
            'timestamp_start'), params.get('timestamp_end'), params.get(
            'database_timestamp_start'), params.get('database_timestamp_end'
            ), params.get('status'), params.get('ranking'), params.get(
            'description'), params.get('unit'), params.get('value'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_last_status_query.
                __name__, params, official_params_list)
        response = self.execute('GET', path=f'/services/query/last_status',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def services_last_status_query_bulk(self, payload: dict = False,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Service Query Last Status List

        Args:
            payload (dict, optional): additional parameters for the API.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            timestamp_start (string optional): additional filter - parameter
            timestamp_end (string optional): additional filter - parameter
            database_timestamp_start (string optional): additional filter - parameter
            database_timestamp_end (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Examples:
            payload = 
           {
            "uuid_customer": "array", optional
            "customer_code": "array", optional
            "customer_status": "array", optional
            "uuid_site": "array", optional
            "site_code": "array", optional
            "site_description": "array", optional
            "site_address": "array", optional
            "site_zip_code": "array", optional
            "site_city": "array", optional
            "site_country": "array", optional
            "site_state_province": "array", optional
            "site_status": "array", optional
            "uuid_group": "array", optional
            "group_name": "array", optional
            "group_status": "array", optional
            "group_type": "array", optional
            "group_uuid_virtual_domain": "array", optional
            "uuid_object": "array", optional
            "object_name": "array", optional
            "object_status": "array", optional
            "object_profile": "array", optional
            "uuid_metric_type": "array", optional
            "metric_type_name": "array", optional
            "metric_type_status": "array", optional
            "uuid_metric": "array", optional
            "metric_name": "array", optional
            "metric_status": "array", optional
            "metric_profile": "array", optional
            "service_uuid_parent": "array", optional
            "uuid_service": "array", optional
            "service_profile": "array", optional
            "service_name": "array", optional
            "service_description": "array", optional
            "service_status": "array", optional
            "service_automata_domain": "array", optional
            "service_uuid_customer": "array", optional
            "status": "array", optional
            "ranking": "array", optional
            "description": "array", optional
            "unit": "array", optional
            "value": "array", optional
           }

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'timestamp_start',
            'timestamp_end', 'database_timestamp_start',
            'database_timestamp_end', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'timestamp_start'), params.get('timestamp_end'), params.get(
            'database_timestamp_start'), params.get('database_timestamp_end'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_last_status_query_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/services/query/last_status',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def services_check_rules_create(self, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Check Service Rules

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_group (string optional): additional filter - parameter
            uuid_object (string optional): additional filter - parameter
            uuid_metric (string optional): additional filter - parameter
            services_rules (array required): additional filter - payload
            default_service (None required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['services_rules', 'default_service']
        payload.get('services_rules'), payload.get('default_service')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_check_rules_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/services/check_rules/',
            params=params, payload=payload, **kwargs)
        return response

    def services_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Read Services

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
            warning_wrong_parameters(self.services_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/services/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def services_metrics_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Read Metrics

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
            warning_wrong_parameters(self.services_metrics_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/services/bulk/read/metrics/', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def services_read_by_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Read Services By Uuid Customer And Name And Profile

        Args:
            payload (list[dict], optional): List dict to create.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "uuid_customer": "string", required
            "profile": "string", required
            "name": "string", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/services/bulk/read_by/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, payload=payload, **kwargs)
        return response

    def services_create_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Create Services

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
            "uuid_parent": "string", optional
            "uuid_customer": "string", required
            "profile": "string", required
            "name": "string", required
            "description": "string", required
            "automata_domain": "array object", optional
            "rule": "array object", optional
            "status": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/services/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def services_delete_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Delete Services

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
        response = self.execute('POST', path=f'/services/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def services_metrics_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Metrics

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
            "uuid_metric": "string", required
            "uuid_service": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_metrics_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/services/bulk/create/metrics', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def services_metrics_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Metrics

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "uuid_metric": "string", required
            "uuid_service": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/services/bulk/delete/metrics', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def services_downtimes_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Downtimes

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
            "uuid_downtime": "string", required
            "uuid_service": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.services_downtimes_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/services/bulk/create/downtimes', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def services_downtimes_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Downtimes

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "uuid_downtime": "string", required
            "uuid_service": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/services/bulk/delete/downtimes', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response
