from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class LastObjectStatus(ApiManager):
    """Class that handles all the XAutomata last_object_status APIs"""

    def last_object_status(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Last Object Status

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
            'group_name', 'group_status', 'group_type', 'uuid_object',
            'object_name', 'object_status', 'object_profile',
            'uuid_metric_type', 'metric_type_name', 'metric_type_status',
            'uuid_metric', 'metric_name', 'metric_status', 'metric_profile',
            'topic', 'last_value_uuid_probe', 'last_value_timestamp_start',
            'last_value_timestamp_end', 'last_value_object_type',
            'last_value_name', 'last_value_value', 'last_value_unit',
            'last_value_description', 'last_value_status',
            'last_value_ranking', 'skip', 'limit', 'like', 'join', 'count']
        params.get('extract_valueless_metrics'), params.get(
            'extract_automata_domain'), params.get('sort_by'), params.get(
            'null_fields'), params.get('uuid_customer'), params.get(
            'customer_code'), params.get('customer_status'), params.get(
            'uuid_site'), params.get('site_code'), params.get(
            'site_description'), params.get('site_address'), params.get(
            'site_zip_code'), params.get('site_city'), params.get(
            'site_country'), params.get('site_state_province'), params.get(
            'site_status'), params.get('uuid_group'), params.get('group_name'
            ), params.get('group_status'), params.get('group_type'
            ), params.get('uuid_object'), params.get('object_name'
            ), params.get('object_status'), params.get('object_profile'
            ), params.get('uuid_metric_type'), params.get('metric_type_name'
            ), params.get('metric_type_status'), params.get('uuid_metric'
            ), params.get('metric_name'), params.get('metric_status'
            ), params.get('metric_profile'), params.get('topic'), params.get(
            'last_value_uuid_probe'), params.get('last_value_timestamp_start'
            ), params.get('last_value_timestamp_end'), params.get(
            'last_value_object_type'), params.get('last_value_name'
            ), params.get('last_value_value'), params.get('last_value_unit'
            ), params.get('last_value_description'), params.get(
            'last_value_status'), params.get('last_value_ranking'), params.get(
            'skip'), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.last_object_status.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/last_object_status/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def last_object_status_create(self, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Read Last Object Status Lists

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter
            uuid_customer (array optional): additional filter - payload
            customer_code (array optional): additional filter - payload
            customer_status (array optional): additional filter - payload
            uuid_site (array optional): additional filter - payload
            site_code (array optional): additional filter - payload
            site_description (array optional): additional filter - payload
            site_address (array optional): additional filter - payload
            site_zip_code (array optional): additional filter - payload
            site_city (array optional): additional filter - payload
            site_country (array optional): additional filter - payload
            site_state_province (array optional): additional filter - payload
            site_status (array optional): additional filter - payload
            uuid_group (array optional): additional filter - payload
            group_name (array optional): additional filter - payload
            group_status (array optional): additional filter - payload
            group_type (array optional): additional filter - payload
            uuid_object (array optional): additional filter - payload
            object_name (array optional): additional filter - payload
            object_status (array optional): additional filter - payload
            object_profile (array optional): additional filter - payload
            uuid_metric_type (array optional): additional filter - payload
            metric_type_name (array optional): additional filter - payload
            metric_type_status (array optional): additional filter - payload
            uuid_metric (array optional): additional filter - payload
            metric_name (array optional): additional filter - payload
            metric_status (array optional): additional filter - payload
            metric_profile (array optional): additional filter - payload
            topic (array optional): additional filter - payload
            last_value_uuid_probe (array optional): additional filter - payload
            last_value_timestamp (array optional): additional filter - payload
            last_value_object_type (array optional): additional filter - payload
            last_value_name (array optional): additional filter - payload
            last_value_value (array optional): additional filter - payload
            last_value_unit (array optional): additional filter - payload
            last_value_description (array optional): additional filter - payload
            last_value_status (array optional): additional filter - payload
            last_value_ranking (array optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'customer_code',
            'customer_status', 'uuid_site', 'site_code', 'site_description',
            'site_address', 'site_zip_code', 'site_city', 'site_country',
            'site_state_province', 'site_status', 'uuid_group',
            'group_name', 'group_status', 'group_type', 'uuid_object',
            'object_name', 'object_status', 'object_profile',
            'uuid_metric_type', 'metric_type_name', 'metric_type_status',
            'uuid_metric', 'metric_name', 'metric_status', 'metric_profile',
            'topic', 'last_value_uuid_probe', 'last_value_timestamp',
            'last_value_object_type', 'last_value_name', 'last_value_value',
            'last_value_unit', 'last_value_description',
            'last_value_status', 'last_value_ranking']
        payload.get('uuid_customer'), payload.get('customer_code'
            ), payload.get('customer_status'), payload.get('uuid_site'
            ), payload.get('site_code'), payload.get('site_description'
            ), payload.get('site_address'), payload.get('site_zip_code'
            ), payload.get('site_city'), payload.get('site_country'
            ), payload.get('site_state_province'), payload.get('site_status'
            ), payload.get('uuid_group'), payload.get('group_name'
            ), payload.get('group_status'), payload.get('group_type'
            ), payload.get('uuid_object'), payload.get('object_name'
            ), payload.get('object_status'), payload.get('object_profile'
            ), payload.get('uuid_metric_type'), payload.get('metric_type_name'
            ), payload.get('metric_type_status'), payload.get('uuid_metric'
            ), payload.get('metric_name'), payload.get('metric_status'
            ), payload.get('metric_profile'), payload.get('topic'
            ), payload.get('last_value_uuid_probe'), payload.get(
            'last_value_timestamp'), payload.get('last_value_object_type'
            ), payload.get('last_value_name'), payload.get('last_value_value'
            ), payload.get('last_value_unit'), payload.get(
            'last_value_description'), payload.get('last_value_status'
            ), payload.get('last_value_ranking')
        if not self._silence_warning:
            warning_wrong_parameters(self.last_object_status_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/last_object_status/',
            params=params, payload=payload, **kwargs)
        return response
