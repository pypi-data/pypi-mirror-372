from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Metrics(ApiManager):
    """Class that handles all the XAutomata metrics APIs"""

    def metrics(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Metrics

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            not_fields (string optional): additional filter - parameter
            uuid_metric_type (string optional): additional filter - parameter
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            feedback_for_operator (string optional): additional filter - parameter
            profile (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            severity (string optional): additional filter - parameter
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'not_fields',
            'uuid_metric_type', 'name', 'description',
            'feedback_for_operator', 'profile', 'status', 'severity',
            'extract_severity', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'not_fields'), params.get('uuid_metric_type'), params.get('name'
            ), params.get('description'), params.get('feedback_for_operator'
            ), params.get('profile'), params.get('status'), params.get(
            'severity'), params.get('extract_severity'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/metrics/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def metrics_create(self, kwargs: dict = None, **payload) -> list:
        """Create Metric

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_metric_type (string required): additional filter - payload
            name (string required): additional filter - payload
            description (string optional): additional filter - payload
            feedback_for_operator (string optional): additional filter - payload
            profile (string required): additional filter - payload
            data_profile (array object optional): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            status (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_metric_type', 'name', 'description',
            'feedback_for_operator', 'profile', 'data_profile',
            'automata_domain', 'status']
        payload.get('uuid_metric_type'), payload.get('name'), payload.get(
            'description'), payload.get('feedback_for_operator'), payload.get(
            'profile'), payload.get('data_profile'), payload.get(
            'automata_domain'), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/metrics/', payload=payload,
            **kwargs)
        return response

    def metric(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Metric

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
            warning_wrong_parameters(self.metric.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/metrics/{uuid}', warm_start=
            warm_start, params=params, **kwargs)
        return response

    def metrics_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Metric

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_metric_type (string optional): additional filter - payload
            name (string optional): additional filter - payload
            description (string optional): additional filter - payload
            feedback_for_operator (string optional): additional filter - payload
            profile (string optional): additional filter - payload
            data_profile (array object optional): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            status (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_metric_type', 'name', 'description',
            'feedback_for_operator', 'profile', 'data_profile',
            'automata_domain', 'status']
        payload.get('uuid_metric_type'), payload.get('name'), payload.get(
            'description'), payload.get('feedback_for_operator'), payload.get(
            'profile'), payload.get('data_profile'), payload.get(
            'automata_domain'), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/metrics/{uuid}', payload=
            payload, **kwargs)
        return response

    def metrics_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Metric

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/metrics/{uuid}', **kwargs)
        return response

    def metrics_last_value(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Get Last Value

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/metrics/{uuid}/last_value',
            warm_start=warm_start, **kwargs)
        return response

    def metrics_services(self, uuid: str, warm_start: bool = False,
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
            name (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            not_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'status', 'not_fields',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('name'), params.get('status'
            ), params.get('not_fields'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_services.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/metrics/{uuid}/services',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def metrics_services_create(self, uuid: str, uuid_service: str,
        kwargs: dict = None) -> list:
        """Add Service

        Args:
            uuid (str, required): uuid
            uuid_service (str, required): uuid_service
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/metrics/{uuid}/services/{uuid_service}', **kwargs)
        return response

    def metrics_services_delete(self, uuid: str, uuid_service: str,
        kwargs: dict = None) -> list:
        """Remove Service

        Args:
            uuid (str, required): uuid
            uuid_service (str, required): uuid_service
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/metrics/{uuid}/services/{uuid_service}', **kwargs)
        return response

    def metrics_services_query(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Metrics Services Query

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            extract_valueless_metrics (boolean optional): additional filter - parameter
            extract_automata_domain (string optional): additional filter - parameter
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
            group_uuid_virtual_domain (string optional): additional filter - parameter
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
            topic (string optional): additional filter - parameter
            last_value_uuid_probe (string optional): additional filter - parameter
            last_value_timestamp_start (string optional): additional filter - parameter
            last_value_timestamp_end (string optional): additional filter - parameter
            last_value_object_type (string optional): additional filter - parameter
            last_value_name (string optional): additional filter - parameter
            last_value_value (string optional): additional filter - parameter
            last_value_unit (string optional): additional filter - parameter
            last_value_description (string optional): additional filter - parameter
            last_value_status (string optional): additional filter - parameter
            last_value_ranking (integer optional): additional filter - parameter
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
        official_params_list = ['extract_valueless_metrics',
            'extract_automata_domain', 'sort_by', 'null_fields',
            'uuid_customer', 'customer_code', 'customer_status',
            'uuid_site', 'site_code', 'site_description', 'site_address',
            'site_zip_code', 'site_city', 'site_country',
            'site_state_province', 'site_status', 'uuid_group',
            'group_uuid_virtual_domain', 'group_name', 'group_status',
            'group_type', 'uuid_object', 'object_name', 'object_status',
            'object_profile', 'uuid_metric_type', 'metric_type_name',
            'metric_type_status', 'uuid_metric', 'metric_name',
            'metric_status', 'metric_profile', 'topic',
            'last_value_uuid_probe', 'last_value_timestamp_start',
            'last_value_timestamp_end', 'last_value_object_type',
            'last_value_name', 'last_value_value', 'last_value_unit',
            'last_value_description', 'last_value_status',
            'last_value_ranking', 'service_uuid_parent', 'uuid_service',
            'service_profile', 'service_name', 'service_description',
            'service_status', 'service_automata_domain',
            'service_uuid_customer', 'skip', 'limit', 'like', 'join', 'count']
        params.get('extract_valueless_metrics'), params.get(
            'extract_automata_domain'), params.get('sort_by'), params.get(
            'null_fields'), params.get('uuid_customer'), params.get(
            'customer_code'), params.get('customer_status'), params.get(
            'uuid_site'), params.get('site_code'), params.get(
            'site_description'), params.get('site_address'), params.get(
            'site_zip_code'), params.get('site_city'), params.get(
            'site_country'), params.get('site_state_province'), params.get(
            'site_status'), params.get('uuid_group'), params.get(
            'group_uuid_virtual_domain'), params.get('group_name'), params.get(
            'group_status'), params.get('group_type'), params.get('uuid_object'
            ), params.get('object_name'), params.get('object_status'
            ), params.get('object_profile'), params.get('uuid_metric_type'
            ), params.get('metric_type_name'), params.get('metric_type_status'
            ), params.get('uuid_metric'), params.get('metric_name'
            ), params.get('metric_status'), params.get('metric_profile'
            ), params.get('topic'), params.get('last_value_uuid_probe'
            ), params.get('last_value_timestamp_start'), params.get(
            'last_value_timestamp_end'), params.get('last_value_object_type'
            ), params.get('last_value_name'), params.get('last_value_value'
            ), params.get('last_value_unit'), params.get(
            'last_value_description'), params.get('last_value_status'
            ), params.get('last_value_ranking'), params.get(
            'service_uuid_parent'), params.get('uuid_service'), params.get(
            'service_profile'), params.get('service_name'), params.get(
            'service_description'), params.get('service_status'), params.get(
            'service_automata_domain'), params.get('service_uuid_customer'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_services_query.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/metrics/services/query',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def metrics_services_query_bulk(self, payload: dict = False,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Metrics Services Query List

        Args:
            payload (dict, optional): additional parameters for the API.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            extract_valueless_metrics (boolean optional): additional filter - parameter
            extract_automata_domain (string optional): additional filter - parameter
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            last_value_timestamp_start (string optional): additional filter - parameter
            last_value_timestamp_end (string optional): additional filter - parameter
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
            "group_uuid_virtual_domain": "array", optional
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
            "topic": "array", optional
            "last_value_uuid_probe": "array", optional
            "last_value_object_type": "array", optional
            "last_value_name": "array", optional
            "last_value_value": "array", optional
            "last_value_unit": "array", optional
            "last_value_description": "array", optional
            "last_value_status": "array", optional
            "last_value_ranking": "array", optional
            "service_uuid_parent": "array", optional
            "uuid_service": "array", optional
            "service_profile": "array", optional
            "service_name": "array", optional
            "service_description": "array", optional
            "service_status": "array", optional
            "service_automata_domain": "array", optional
            "service_uuid_customer": "array", optional
           }

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['extract_valueless_metrics',
            'extract_automata_domain', 'sort_by', 'null_fields',
            'last_value_timestamp_start', 'last_value_timestamp_end',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('extract_valueless_metrics'), params.get(
            'extract_automata_domain'), params.get('sort_by'), params.get(
            'null_fields'), params.get('last_value_timestamp_start'
            ), params.get('last_value_timestamp_end'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_services_query_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/metrics/services/query',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def metrics_services_model_query(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Metrics Services Query Model

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            extract_valueless_metrics (boolean optional): additional filter - parameter
            extract_automata_domain (string optional): additional filter - parameter
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
            group_uuid_virtual_domain (string optional): additional filter - parameter
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
            topic (string optional): additional filter - parameter
            last_value_uuid_probe (string optional): additional filter - parameter
            last_value_timestamp_start (string optional): additional filter - parameter
            last_value_timestamp_end (string optional): additional filter - parameter
            last_value_object_type (string optional): additional filter - parameter
            last_value_name (string optional): additional filter - parameter
            last_value_value (string optional): additional filter - parameter
            last_value_unit (string optional): additional filter - parameter
            last_value_description (string optional): additional filter - parameter
            last_value_status (string optional): additional filter - parameter
            last_value_ranking (integer optional): additional filter - parameter
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
        official_params_list = ['extract_valueless_metrics',
            'extract_automata_domain', 'sort_by', 'null_fields',
            'uuid_customer', 'customer_code', 'customer_status',
            'uuid_site', 'site_code', 'site_description', 'site_address',
            'site_zip_code', 'site_city', 'site_country',
            'site_state_province', 'site_status', 'uuid_group',
            'group_uuid_virtual_domain', 'group_name', 'group_status',
            'group_type', 'uuid_object', 'object_name', 'object_status',
            'object_profile', 'uuid_metric_type', 'metric_type_name',
            'metric_type_status', 'uuid_metric', 'metric_name',
            'metric_status', 'metric_profile', 'topic',
            'last_value_uuid_probe', 'last_value_timestamp_start',
            'last_value_timestamp_end', 'last_value_object_type',
            'last_value_name', 'last_value_value', 'last_value_unit',
            'last_value_description', 'last_value_status',
            'last_value_ranking', 'service_uuid_parent', 'uuid_service',
            'service_profile', 'service_name', 'service_description',
            'service_status', 'service_automata_domain',
            'service_uuid_customer', 'skip', 'limit', 'like', 'join', 'count']
        params.get('extract_valueless_metrics'), params.get(
            'extract_automata_domain'), params.get('sort_by'), params.get(
            'null_fields'), params.get('uuid_customer'), params.get(
            'customer_code'), params.get('customer_status'), params.get(
            'uuid_site'), params.get('site_code'), params.get(
            'site_description'), params.get('site_address'), params.get(
            'site_zip_code'), params.get('site_city'), params.get(
            'site_country'), params.get('site_state_province'), params.get(
            'site_status'), params.get('uuid_group'), params.get(
            'group_uuid_virtual_domain'), params.get('group_name'), params.get(
            'group_status'), params.get('group_type'), params.get('uuid_object'
            ), params.get('object_name'), params.get('object_status'
            ), params.get('object_profile'), params.get('uuid_metric_type'
            ), params.get('metric_type_name'), params.get('metric_type_status'
            ), params.get('uuid_metric'), params.get('metric_name'
            ), params.get('metric_status'), params.get('metric_profile'
            ), params.get('topic'), params.get('last_value_uuid_probe'
            ), params.get('last_value_timestamp_start'), params.get(
            'last_value_timestamp_end'), params.get('last_value_object_type'
            ), params.get('last_value_name'), params.get('last_value_value'
            ), params.get('last_value_unit'), params.get(
            'last_value_description'), params.get('last_value_status'
            ), params.get('last_value_ranking'), params.get(
            'service_uuid_parent'), params.get('uuid_service'), params.get(
            'service_profile'), params.get('service_name'), params.get(
            'service_description'), params.get('service_status'), params.get(
            'service_automata_domain'), params.get('service_uuid_customer'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_services_model_query.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/metrics/services/query/model', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def metrics_services_model_query_bulk(self, payload: dict = False,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Metrics Services Query List Model

        Args:
            payload (dict, optional): additional parameters for the API.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            extract_valueless_metrics (boolean optional): additional filter - parameter
            extract_automata_domain (string optional): additional filter - parameter
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            last_value_timestamp_start (string optional): additional filter - parameter
            last_value_timestamp_end (string optional): additional filter - parameter
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
            "group_uuid_virtual_domain": "array", optional
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
            "topic": "array", optional
            "last_value_uuid_probe": "array", optional
            "last_value_object_type": "array", optional
            "last_value_name": "array", optional
            "last_value_value": "array", optional
            "last_value_unit": "array", optional
            "last_value_description": "array", optional
            "last_value_status": "array", optional
            "last_value_ranking": "array", optional
            "service_uuid_parent": "array", optional
            "uuid_service": "array", optional
            "service_profile": "array", optional
            "service_name": "array", optional
            "service_description": "array", optional
            "service_status": "array", optional
            "service_automata_domain": "array", optional
            "service_uuid_customer": "array", optional
           }

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['extract_valueless_metrics',
            'extract_automata_domain', 'sort_by', 'null_fields',
            'last_value_timestamp_start', 'last_value_timestamp_end',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('extract_valueless_metrics'), params.get(
            'extract_automata_domain'), params.get('sort_by'), params.get(
            'null_fields'), params.get('last_value_timestamp_start'
            ), params.get('last_value_timestamp_end'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_services_model_query_bulk
                .__name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/metrics/services/query/model', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def metrics_downtimes(self, uuid: str, warm_start: bool = False,
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
            status (string optional): additional filter - parameter
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
        official_params_list = ['not_in', 'code', 'status', 'fetch_all',
            'only_actives', 'active_at_timestamp', 'active_after_timestamp',
            'active_at_or_after_timestamp', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('code'), params.get('status'
            ), params.get('fetch_all'), params.get('only_actives'), params.get(
            'active_at_timestamp'), params.get('active_after_timestamp'
            ), params.get('active_at_or_after_timestamp'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_downtimes.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/metrics/{uuid}/downtimes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def metrics_downtimes_create(self, uuid: str, uuid_downtime: str,
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
            f'/metrics/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def metrics_downtimes_delete(self, uuid: str, uuid_downtime: str,
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
            f'/metrics/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def metrics_dispatchers(self, uuid: str, warm_start: bool = False,
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
        official_params_list = ['not_in', 'code', 'status', 'fetch_all',
            'only_actives', 'active_at_timestamp', 'active_after_timestamp',
            'active_at_or_after_timestamp', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('code'), params.get('status'
            ), params.get('fetch_all'), params.get('only_actives'), params.get(
            'active_at_timestamp'), params.get('active_after_timestamp'
            ), params.get('active_at_or_after_timestamp'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_dispatchers.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/metrics/{uuid}/dispatchers',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def metrics_dispatchers_create(self, uuid: str, uuid_dispatcher: str,
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
            f'/metrics/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def metrics_dispatchers_delete(self, uuid: str, uuid_dispatcher: str,
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
            f'/metrics/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def metrics_bulk(self, payload: list, warm_start: bool = False,
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
            warning_wrong_parameters(self.metrics_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/metrics/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def metrics_services_bulk(self, payload: list, warm_start: bool = False,
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
            warning_wrong_parameters(self.metrics_services_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/metrics/bulk/read/services/', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def metrics_downtimes_bulk(self, payload: list,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Read Metrics

        Args:
            payload (list[dict], optional): List dict to create.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            code (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
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

        Examples:
            payload = 
          [
            "uuid": "str", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['code', 'status', 'fetch_all',
            'only_actives', 'active_at_timestamp', 'active_after_timestamp',
            'active_at_or_after_timestamp', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('code'), params.get('status'), params.get('fetch_all'
            ), params.get('only_actives'), params.get('active_at_timestamp'
            ), params.get('active_after_timestamp'), params.get(
            'active_at_or_after_timestamp'), params.get('skip'), params.get(
            'limit'), params.get('like'), params.get('join'), params.get(
            'count')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_downtimes_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/metrics/bulk/read/downtimes/', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def metrics_read_by_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Read Metrics By Uuid Metric Type And Name

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
            "uuid_metric_type": "string", required
            "name": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/metrics/bulk/read_by/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, payload=payload, **kwargs)
        return response

    def metrics_create_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Create Metrics

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
            "uuid_metric_type": "string", required
            "name": "string", required
            "description": "string", optional
            "feedback_for_operator": "string", optional
            "profile": "string", required
            "data_profile": "array object", optional
            "automata_domain": "array object", optional
            "status": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/metrics/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def metrics_delete_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Delete Metrics

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
        response = self.execute('POST', path=f'/metrics/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def metrics_downtimes_create_bulk(self, payload: list,
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
            "uuid_metric": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_downtimes_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/metrics/bulk/create/downtimes', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def metrics_downtimes_delete_bulk(self, payload: list,
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
            "uuid_metric": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/metrics/bulk/delete/downtimes', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def metrics_services_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Services

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
            warning_wrong_parameters(self.metrics_services_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/metrics/bulk/create/services', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def metrics_services_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Services

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
            f'/metrics/bulk/delete/services', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def metrics_topic_consumer(self, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Kafka Consumer

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            num_messages (integer optional): additional filter - parameter
            group (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['num_messages', 'group']
        params.get('num_messages'), params.get('group')
        if not self._silence_warning:
            warning_wrong_parameters(self.metrics_topic_consumer.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/metrics/topic/consumer',
            warm_start=warm_start, params=params, **kwargs)
        return response
