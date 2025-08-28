from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Groups(ApiManager):
    """Class that handles all the XAutomata groups APIs"""

    def groups(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Groups

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
            uuid_parent (string optional): additional filter - parameter
            uuid_site (string optional): additional filter - parameter
            uuid_virtual_domain (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
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
            'uuid_parent', 'uuid_site', 'uuid_virtual_domain', 'type',
            'name', 'description', 'status', 'extract_severity',
            'count_children', 'severity', 'skip', 'limit', 'like', 'join',
            'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'not_fields'), params.get('uuid_parent'), params.get('uuid_site'
            ), params.get('uuid_virtual_domain'), params.get('type'
            ), params.get('name'), params.get('description'), params.get(
            'status'), params.get('extract_severity'), params.get(
            'count_children'), params.get('severity'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.groups.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/groups/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def groups_create(self, kwargs: dict = None, **payload) -> list:
        """Create Group

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_parent (string optional): additional filter - payload
            uuid_site (string required): additional filter - payload
            uuid_virtual_domain (string required): additional filter - payload
            type (string required): additional filter - payload
            name (string required): additional filter - payload
            description (string required): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            status (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_parent', 'uuid_site',
            'uuid_virtual_domain', 'type', 'name', 'description',
            'automata_domain', 'status']
        payload.get('uuid_parent'), payload.get('uuid_site'), payload.get(
            'uuid_virtual_domain'), payload.get('type'), payload.get('name'
            ), payload.get('description'), payload.get('automata_domain'
            ), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.groups_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/groups/', payload=payload,
            **kwargs)
        return response

    def group(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Group

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
            warning_wrong_parameters(self.group.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/groups/{uuid}', warm_start=
            warm_start, params=params, **kwargs)
        return response

    def groups_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Group

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_parent (string optional): additional filter - payload
            uuid_site (string optional): additional filter - payload
            uuid_virtual_domain (string optional): additional filter - payload
            type (string optional): additional filter - payload
            name (string optional): additional filter - payload
            description (string optional): additional filter - payload
            automata_domain (array object optional): additional filter - payload
            status (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_parent', 'uuid_site',
            'uuid_virtual_domain', 'type', 'name', 'description',
            'automata_domain', 'status']
        payload.get('uuid_parent'), payload.get('uuid_site'), payload.get(
            'uuid_virtual_domain'), payload.get('type'), payload.get('name'
            ), payload.get('description'), payload.get('automata_domain'
            ), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.groups_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/groups/{uuid}', payload=
            payload, **kwargs)
        return response

    def groups_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Group

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/groups/{uuid}', **kwargs)
        return response

    def groups_objects(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """List Objects

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            not_fields (string optional): additional filter - parameter
            not_in (boolean optional): additional filter - parameter
            name (string optional): additional filter - parameter
            profile (string optional): additional filter - parameter
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter
            count_children (boolean optional): additional filter - parameter
            object_profile (string optional): additional filter - parameter
            severity (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'not_fields', 'not_in', 'name',
            'profile', 'extract_severity', 'count_children',
            'object_profile', 'severity', 'status', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('sort_by'), params.get('not_fields'), params.get('not_in'
            ), params.get('name'), params.get('profile'), params.get(
            'extract_severity'), params.get('count_children'), params.get(
            'object_profile'), params.get('severity'), params.get('status'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.groups_objects.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/groups/{uuid}/objects',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def groups_objects_create(self, uuid: str, uuid_object: str,
        kwargs: dict = None) -> list:
        """Add Object

        Args:
            uuid (str, required): uuid
            uuid_object (str, required): uuid_object
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/groups/{uuid}/objects/{uuid_object}', **kwargs)
        return response

    def groups_objects_delete(self, uuid: str, uuid_object: str,
        kwargs: dict = None) -> list:
        """Remove Object

        Args:
            uuid (str, required): uuid
            uuid_object (str, required): uuid_object
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/groups/{uuid}/objects/{uuid_object}', **kwargs)
        return response

    def groups_users(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.groups_users.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/groups/{uuid}/users',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def groups_users_create(self, uuid: str, name: str, kwargs: dict = None
        ) -> list:
        """Add User

        Args:
            uuid (str, required): uuid
            name (str, required): name
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/groups/{uuid}/users/{name}',
            **kwargs)
        return response

    def groups_users_delete(self, uuid: str, name: str, kwargs: dict = None
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
            f'/groups/{uuid}/users/{name}', **kwargs)
        return response

    def groups_downtimes(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.groups_downtimes.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/groups/{uuid}/downtimes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def groups_downtimes_create(self, uuid: str, uuid_downtime: str,
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
            f'/groups/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def groups_downtimes_delete(self, uuid: str, uuid_downtime: str,
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
            f'/groups/{uuid}/downtimes/{uuid_downtime}', **kwargs)
        return response

    def groups_dispatchers(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.groups_dispatchers.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/groups/{uuid}/dispatchers',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def groups_dispatchers_create(self, uuid: str, uuid_dispatcher: str,
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
            f'/groups/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def groups_dispatchers_delete(self, uuid: str, uuid_dispatcher: str,
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
            f'/groups/{uuid}/dispatchers/{uuid_dispatcher}', **kwargs)
        return response

    def groups_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Read Groups

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
            warning_wrong_parameters(self.groups_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/groups/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def groups_read_by_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Read Groups By Uuid Site And Uuid Virtual Domain And Name

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
            "uuid_site": "string", required
            "uuid_virtual_domain": "string", required
            "name": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/groups/bulk/read_by/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, payload=payload, **kwargs)
        return response

    def groups_create_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Create Groups

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
            "uuid_site": "string", required
            "uuid_virtual_domain": "string", required
            "type": "string", required
            "name": "string", required
            "description": "string", required
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
            warning_wrong_parameters(self.groups_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/groups/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def groups_delete_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Delete Groups

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
        response = self.execute('POST', path=f'/groups/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def groups_objects_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Objects

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
            warning_wrong_parameters(self.groups_objects_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/groups/bulk/create/objects',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def groups_objects_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Objects

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
        response = self.execute('POST', path=f'/groups/bulk/delete/objects',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def groups_downtimes_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read Groups Downtimes

        Args:
            payload (list[dict], optional): List dict to create.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            active_at_timestamp (string optional): additional filter - parameter
            active_after_timestamp (string optional): additional filter - parameter
            active_at_or_after_timestamp (string optional): additional filter - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter

        Examples:
            payload = 
          [
            "uuid": "str", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['active_at_timestamp',
            'active_after_timestamp', 'active_at_or_after_timestamp', 'join']
        params.get('active_at_timestamp'), params.get('active_after_timestamp'
            ), params.get('active_at_or_after_timestamp'), params.get('join')
        if not self._silence_warning:
            warning_wrong_parameters(self.groups_downtimes_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/groups/bulk/read/downtimes',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def groups_downtimes_create_bulk(self, payload: list,
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
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.groups_downtimes_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/groups/bulk/create/downtimes', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def groups_downtimes_delete_bulk(self, payload: list,
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
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/groups/bulk/delete/downtimes', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def groups_users_create_bulk(self, payload: list,
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
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.groups_users_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/groups/bulk/create/users',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def groups_users_delete_bulk(self, payload: list,
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
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/groups/bulk/delete/users',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response
