from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Probes(ApiManager):
    """Class that handles all the XAutomata probes APIs"""

    def probes(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Probes

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
            uuid_virtual_domain (string optional): additional filter - parameter
            uuid_probe_type (string optional): additional filter - parameter
            uuid_host (string optional): additional filter - parameter
            name (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            notes (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter
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
            'uuid_virtual_domain', 'uuid_probe_type', 'uuid_host', 'name',
            'description', 'notes', 'status', 'extract_severity',
            'severity', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'not_fields'), params.get('uuid_virtual_domain'), params.get(
            'uuid_probe_type'), params.get('uuid_host'), params.get('name'
            ), params.get('description'), params.get('notes'), params.get(
            'status'), params.get('extract_severity'), params.get('severity'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.probes.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/probes/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def probes_create(self, kwargs: dict = None, **payload) -> list:
        """Create Probe

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_virtual_domain (string required): additional filter - payload
            uuid_probe_type (string required): additional filter - payload
            uuid_host (string required): additional filter - payload
            name (string required): additional filter - payload
            description (string optional): additional filter - payload
            data_profile (array object required): additional filter - payload
            notes (string optional): additional filter - payload
            status (string required): additional filter - payload
            data_profile_backup (array object optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_virtual_domain', 'uuid_probe_type',
            'uuid_host', 'name', 'description', 'data_profile', 'notes',
            'status', 'data_profile_backup']
        payload.get('uuid_virtual_domain'), payload.get('uuid_probe_type'
            ), payload.get('uuid_host'), payload.get('name'), payload.get(
            'description'), payload.get('data_profile'), payload.get('notes'
            ), payload.get('status'), payload.get('data_profile_backup')
        if not self._silence_warning:
            warning_wrong_parameters(self.probes_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/probes/', payload=payload,
            **kwargs)
        return response

    def probe(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Probe

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            extract_severity (boolean optional): Se True nella risposta e' anche presente la severita, Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['join', 'extract_severity']
        params.get('join'), params.get('extract_severity')
        if not self._silence_warning:
            warning_wrong_parameters(self.probe.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/probes/{uuid}', warm_start=
            warm_start, params=params, **kwargs)
        return response

    def probes_put(self, uuid: str, kwargs: dict = None, **payload) -> list:
        """Update Probe

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_virtual_domain (string optional): additional filter - payload
            uuid_probe_type (string optional): additional filter - payload
            uuid_host (string optional): additional filter - payload
            name (string optional): additional filter - payload
            description (string optional): additional filter - payload
            data_profile (array object optional): additional filter - payload
            notes (string optional): additional filter - payload
            status (string optional): additional filter - payload
            data_profile_backup (array object optional): additional filter - payload
            last_seen (string optional): additional filter - payload
            ingest_frequency (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_virtual_domain', 'uuid_probe_type',
            'uuid_host', 'name', 'description', 'data_profile', 'notes',
            'status', 'data_profile_backup', 'last_seen', 'ingest_frequency']
        payload.get('uuid_virtual_domain'), payload.get('uuid_probe_type'
            ), payload.get('uuid_host'), payload.get('name'), payload.get(
            'description'), payload.get('data_profile'), payload.get('notes'
            ), payload.get('status'), payload.get('data_profile_backup'
            ), payload.get('last_seen'), payload.get('ingest_frequency')
        if not self._silence_warning:
            warning_wrong_parameters(self.probes_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/probes/{uuid}', payload=
            payload, **kwargs)
        return response

    def probes_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Probe

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/probes/{uuid}', **kwargs)
        return response

    def probes_agent_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Agent Update Probe

        Args:
            uuid (str, required): uuid
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
            warning_wrong_parameters(self.probes_agent_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/probes/agent/{uuid}',
            payload=payload, **kwargs)
        return response

    def probes_objects(self, uuid: str, warm_start: bool = False,
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
            not_in (boolean optional): additional filter - parameter
            name (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            profile (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'status', 'profile',
            'skip', 'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('name'), params.get('status'
            ), params.get('profile'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.probes_objects.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/probes/{uuid}/objects',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def probes_objects_create(self, uuid: str, uuid_object: str,
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
            f'/probes/{uuid}/objects/{uuid_object}', **kwargs)
        return response

    def probes_objects_delete(self, uuid: str, uuid_object: str,
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
            f'/probes/{uuid}/objects/{uuid_object}', **kwargs)
        return response

    def probes_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read Probes

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
            warning_wrong_parameters(self.probes_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/probes/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def probes_create_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Create Probes

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
            "uuid_virtual_domain": "string", required
            "uuid_probe_type": "string", required
            "uuid_host": "string", required
            "name": "string", required
            "description": "string", optional
            "data_profile": "array object", required
            "notes": "string", optional
            "status": "string", required
            "data_profile_backup": "array object", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.probes_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/probes/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def probes_delete_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Delete Probes

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
        response = self.execute('POST', path=f'/probes/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def probes_objects_create_bulk(self, payload: list,
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
            warning_wrong_parameters(self.probes_objects_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/probes/bulk/create/objects',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def probes_objects_delete_bulk(self, payload: list,
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
            "uuid_object": "string", required
            "uuid_probe": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/probes/bulk/delete/objects',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def probes_logs(self, uuid: str, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Consume Probe Log

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
            key (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['skip', 'limit', 'key']
        params.get('skip'), params.get('limit'), params.get('key')
        if not self._silence_warning:
            warning_wrong_parameters(self.probes_logs.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/probes/{uuid}/logs',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response
