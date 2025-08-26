from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Objects(ApiManager):
    """Class that handles all the XAutomata objects APIs"""

    def objects(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Objects

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
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            feedback_for_operator (string optional): additional filter - parameter
            profile (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter
            count_children (boolean optional): additional filter - parameter
            severity (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'not_fields',
            'name', 'description', 'feedback_for_operator', 'profile',
            'status', 'extract_severity', 'count_children', 'severity',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'not_fields'), params.get('name'), params.get('description'
            ), params.get('feedback_for_operator'), params.get('profile'
            ), params.get('status'), params.get('extract_severity'
            ), params.get('count_children'), params.get('severity'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/objects/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def objects_create(self, kwargs: dict = None, **payload) -> list:
        """Create Object

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            name (string required): additional filter - payload
            description (string optional): additional filter - payload
            feedback_for_operator (string optional): additional filter - payload
            ip_cidr (array object optional): additional filter - payload
            profile (string required): additional filter - payload
            data_profile (array object optional): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            status (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['name', 'description',
            'feedback_for_operator', 'ip_cidr', 'profile', 'data_profile',
            'automata_domain', 'status']
        payload.get('name'), payload.get('description'), payload.get(
            'feedback_for_operator'), payload.get('ip_cidr'), payload.get(
            'profile'), payload.get('data_profile'), payload.get(
            'automata_domain'), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/objects/', payload=payload,
            **kwargs)
        return response

    def object(self, uuid: str, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Read Object

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/objects/{uuid}', warm_start=
            warm_start, **kwargs)
        return response

    def objects_put(self, uuid: str, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Update Object

        Args:
            params (dict, optional): additional parameters for the API.
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_probe (string optional): additional filter - parameter
            name (string optional): additional filter - payload
            description (string optional): additional filter - payload
            feedback_for_operator (string optional): additional filter - payload
            ip_cidr (array object optional): additional filter - payload
            profile (string optional): additional filter - payload
            data_profile (array object optional): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            status (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['name', 'description',
            'feedback_for_operator', 'ip_cidr', 'profile', 'data_profile',
            'automata_domain', 'status']
        payload.get('name'), payload.get('description'), payload.get(
            'feedback_for_operator'), payload.get('ip_cidr'), payload.get(
            'profile'), payload.get('data_profile'), payload.get(
            'automata_domain'), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/objects/{uuid}', params=
            params, payload=payload, **kwargs)
        return response

    def objects_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Object

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/objects/{uuid}', **kwargs)
        return response

    def objects_metric_types(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Metric Types

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
            warning_wrong_parameters(self.objects_metric_types.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/objects/{uuid}/metric_types',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def objects_hosted(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Hosteds

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
            warning_wrong_parameters(self.objects_hosted.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/objects/{uuid}/hosted',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def objects_groups(self, uuid: str, warm_start: bool = False,
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
            not_in (boolean optional): additional filter - parameter
            count_children (boolean optional): additional filter - parameter
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
        official_params_list = ['not_in', 'count_children', 'name',
            'status', 'skip', 'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('count_children'), params.get('name'
            ), params.get('status'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_groups.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/objects/{uuid}/groups',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def objects_groups_create(self, uuid: str, uuid_group: str,
        kwargs: dict = None) -> list:
        """Add Group

        Args:
            uuid (str, required): uuid
            uuid_group (str, required): uuid_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/objects/{uuid}/groups/{uuid_group}', **kwargs)
        return response

    def objects_groups_delete(self, uuid: str, uuid_group: str,
        kwargs: dict = None) -> list:
        """Remove Group

        Args:
            uuid (str, required): uuid
            uuid_group (str, required): uuid_group
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/objects/{uuid}/groups/{uuid_group}', **kwargs)
        return response

    def objects_probes(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Probes

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
            warning_wrong_parameters(self.objects_probes.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/objects/{uuid}/probes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def objects_probes_create(self, uuid: str, uuid_probe: str,
        kwargs: dict = None) -> list:
        """Add Probe

        Args:
            uuid (str, required): uuid
            uuid_probe (str, required): uuid_probe
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/objects/{uuid}/probes/{uuid_probe}', **kwargs)
        return response

    def objects_probes_delete(self, uuid: str, uuid_probe: str,
        kwargs: dict = None) -> list:
        """Remove Probe

        Args:
            uuid (str, required): uuid
            uuid_probe (str, required): uuid_probe
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/objects/{uuid}/probes/{uuid_probe}', **kwargs)
        return response

    def objects_downtimes(self, uuid: str, warm_start: bool = False,
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
            status (boolean optional): additional filter - parameter
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
        official_params_list = ['not_in', 'code', 'status',
            'active_at_timestamp', 'active_after_timestamp',
            'active_at_or_after_timestamp', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('code'), params.get('status'
            ), params.get('active_at_timestamp'), params.get(
            'active_after_timestamp'), params.get(
            'active_at_or_after_timestamp'), params.get('skip'), params.get(
            'limit'), params.get('like'), params.get('join'), params.get(
            'count')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_downtimes.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/objects/{uuid}/downtimes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def objects_downtimes_create(self, uuid: str, uuid_downtime: str,
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
            f'/objects/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def objects_downtimes_delete(self, uuid: str, uuid_downtime: str,
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
            f'/objects/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def objects_dispatchers(self, uuid: str, warm_start: bool = False,
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
        official_params_list = ['not_in', 'code', 'status',
            'active_at_timestamp', 'active_after_timestamp',
            'active_at_or_after_timestamp', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('not_in'), params.get('code'), params.get('status'
            ), params.get('active_at_timestamp'), params.get(
            'active_after_timestamp'), params.get(
            'active_at_or_after_timestamp'), params.get('skip'), params.get(
            'limit'), params.get('like'), params.get('join'), params.get(
            'count')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_dispatchers.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/objects/{uuid}/dispatchers',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def objects_dispatchers_create(self, uuid: str, uuid_dispatcher: str,
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
            f'/objects/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def objects_dispatchers_delete(self, uuid: str, uuid_dispatcher: str,
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
            f'/objects/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def objects_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Read Objects

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
            warning_wrong_parameters(self.objects_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/objects/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def objects_read_by_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read By Name

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
            "name": "string", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['join']
        params.get('join')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_read_by_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/objects/bulk/read_by/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def objects_create_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Create Objects With Relationship

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
            "description": "string", optional
            "feedback_for_operator": "string", optional
            "ip_cidr": "array object", optional
            "profile": "string", required
            "data_profile": "array object", optional
            "automata_domain": "array object", optional
            "status": "string", required
            "uuid_groups": "array", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/objects/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def objects_delete_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Delete Objects

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
        response = self.execute('POST', path=f'/objects/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def objects_groups_create_bulk(self, payload: list,
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
            "uuid_group": "string", required
            "uuid_object": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_groups_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/objects/bulk/create/groups',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def objects_groups_delete_bulk(self, payload: list,
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
            "uuid_group": "string", required
            "uuid_object": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/objects/bulk/delete/groups',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def objects_downtimes_bulk(self, payload: list,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Read Downtimes

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
        official_params_list = ['code', 'status', 'active_at_timestamp',
            'active_after_timestamp', 'active_at_or_after_timestamp',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('code'), params.get('status'), params.get(
            'active_at_timestamp'), params.get('active_after_timestamp'
            ), params.get('active_at_or_after_timestamp'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_downtimes_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/objects/bulk/read/downtimes', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def objects_downtimes_create_bulk(self, payload: list,
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
            "uuid_object": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_downtimes_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/objects/bulk/create/downtimes', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def objects_downtimes_delete_bulk(self, payload: list,
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
            "uuid_object": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/objects/bulk/delete/downtimes', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def objects_probes_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Probes

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
            "uuid_object": "string", required
            "uuid_probe": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.objects_probes_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/objects/bulk/create/probes',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def objects_probes_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Probes

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "uuid_object": "string", required
            "uuid_probe": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/objects/bulk/delete/probes',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response
