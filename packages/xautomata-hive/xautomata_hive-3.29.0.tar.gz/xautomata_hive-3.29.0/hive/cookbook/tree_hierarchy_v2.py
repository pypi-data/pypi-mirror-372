from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class TreeHierarchyV2(ApiManager):
    """Class that handles all the XAutomata tree_hierarchy_v2 APIs"""

    def tree_hierarchy_v2_groups(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Tree Hierarchy Groups

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter
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
            site_type (string optional): additional filter - parameter
            uuid_group (string optional): additional filter - parameter
            group_name (string optional): additional filter - parameter
            group_status (string optional): additional filter - parameter
            group_type (string optional): additional filter - parameter
            uuid_virtual_domain (string optional): additional filter - parameter
            virtual_domain_name (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['extract_severity', 'sort_by',
            'null_fields', 'uuid_customer', 'customer_code',
            'customer_status', 'uuid_site', 'site_code', 'site_description',
            'site_address', 'site_zip_code', 'site_city', 'site_country',
            'site_state_province', 'site_status', 'site_type', 'uuid_group',
            'group_name', 'group_status', 'group_type',
            'uuid_virtual_domain', 'virtual_domain_name', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('extract_severity'), params.get('sort_by'), params.get(
            'null_fields'), params.get('uuid_customer'), params.get(
            'customer_code'), params.get('customer_status'), params.get(
            'uuid_site'), params.get('site_code'), params.get(
            'site_description'), params.get('site_address'), params.get(
            'site_zip_code'), params.get('site_city'), params.get(
            'site_country'), params.get('site_state_province'), params.get(
            'site_status'), params.get('site_type'), params.get('uuid_group'
            ), params.get('group_name'), params.get('group_status'
            ), params.get('group_type'), params.get('uuid_virtual_domain'
            ), params.get('virtual_domain_name'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.tree_hierarchy_v2_groups.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/tree_hierarchy_v2/groups',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def tree_hierarchy_v2_objects(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Tree Hierarchy Objects

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            extract_data_profile (boolean optional): additional filter - parameter
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter
            extract_ip_cidr (boolean optional): additional filter - parameter
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
            uuid_virtual_domain (string optional): additional filter - parameter
            virtual_domain_name (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields',
            'extract_data_profile', 'extract_severity', 'extract_ip_cidr',
            'uuid_customer', 'customer_code', 'customer_status',
            'uuid_site', 'site_code', 'site_description', 'site_address',
            'site_zip_code', 'site_city', 'site_country',
            'site_state_province', 'site_status', 'uuid_group',
            'group_name', 'group_status', 'group_type', 'uuid_object',
            'object_name', 'object_status', 'object_profile',
            'uuid_virtual_domain', 'virtual_domain_name', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'extract_data_profile'), params.get('extract_severity'
            ), params.get('extract_ip_cidr'), params.get('uuid_customer'
            ), params.get('customer_code'), params.get('customer_status'
            ), params.get('uuid_site'), params.get('site_code'), params.get(
            'site_description'), params.get('site_address'), params.get(
            'site_zip_code'), params.get('site_city'), params.get(
            'site_country'), params.get('site_state_province'), params.get(
            'site_status'), params.get('uuid_group'), params.get('group_name'
            ), params.get('group_status'), params.get('group_type'
            ), params.get('uuid_object'), params.get('object_name'
            ), params.get('object_status'), params.get('object_profile'
            ), params.get('uuid_virtual_domain'), params.get(
            'virtual_domain_name'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.tree_hierarchy_v2_objects.
                __name__, params, official_params_list)
        response = self.execute('GET', path=f'/tree_hierarchy_v2/objects',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def tree_hierarchy_v2_metric_types(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Tree Hierarchy Metric Types

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
            metric_type_name (string optional): additional filter - parameter
            metric_type_status (string optional): additional filter - parameter
            metric_type_profile (string optional): additional filter - parameter
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
            'object_profile', 'metric_type_name', 'metric_type_status',
            'metric_type_profile', 'skip', 'limit', 'like', 'join', 'count']
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
            ), params.get('metric_type_name'), params.get('metric_type_status'
            ), params.get('metric_type_profile'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.tree_hierarchy_v2_metric_types.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/tree_hierarchy_v2/metric_types', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def tree_hierarchy_v2_metrics(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Tree Hierarchy Metrics

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
            metric_type_name (string optional): additional filter - parameter
            metric_type_status (string optional): additional filter - parameter
            uuid_metric (string optional): additional filter - parameter
            metric_name (string optional): additional filter - parameter
            metric_status (string optional): additional filter - parameter
            metric_profile (string optional): additional filter - parameter
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
            'object_profile', 'metric_type_name', 'metric_type_status',
            'uuid_metric', 'metric_name', 'metric_status', 'metric_profile',
            'skip', 'limit', 'like', 'join', 'count']
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
            ), params.get('metric_type_name'), params.get('metric_type_status'
            ), params.get('uuid_metric'), params.get('metric_name'
            ), params.get('metric_status'), params.get('metric_profile'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.tree_hierarchy_v2_metrics.
                __name__, params, official_params_list)
        response = self.execute('GET', path=f'/tree_hierarchy_v2/metrics',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response
