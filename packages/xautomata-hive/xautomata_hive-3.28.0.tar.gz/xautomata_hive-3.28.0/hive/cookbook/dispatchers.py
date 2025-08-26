from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Dispatchers(ApiManager):
    """Class that handles all the XAutomata dispatchers APIs"""

    def dispatchers(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Dispatchers

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            uuid_notification_provider (string optional): additional filter - parameter
            uuid_calendar (string optional): additional filter - parameter
            uuid_message (string optional): additional filter - parameter
            uuid_opening_reason (string optional): additional filter - parameter
            uuid_reason_for_closure (string optional): additional filter - parameter
            code (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            level (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields',
            'uuid_notification_provider', 'uuid_calendar', 'uuid_message',
            'uuid_opening_reason', 'uuid_reason_for_closure', 'code',
            'description', 'level', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'uuid_notification_provider'), params.get('uuid_calendar'
            ), params.get('uuid_message'), params.get('uuid_opening_reason'
            ), params.get('uuid_reason_for_closure'), params.get('code'
            ), params.get('description'), params.get('level'), params.get(
            'skip'), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/dispatchers/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def dispatchers_create(self, kwargs: dict = None, **payload) -> list:
        """Create Dispatcher

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_notification_provider (string optional): additional filter - payload
            uuid_calendar (string required): additional filter - payload
            uuid_message (string required): additional filter - payload
            uuid_opening_reason (string optional): additional filter - payload
            uuid_reason_for_closure (string optional): additional filter - payload
            code (string required): additional filter - payload
            description (string optional): additional filter - payload
            delay (integer optional): additional filter - payload
            status (string required): additional filter - payload
            country (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            data_profile (array object optional): additional filter - payload
            remember_it (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_notification_provider',
            'uuid_calendar', 'uuid_message', 'uuid_opening_reason',
            'uuid_reason_for_closure', 'code', 'description', 'delay',
            'status', 'country', 'state_province', 'data_profile',
            'remember_it']
        payload.get('uuid_notification_provider'), payload.get('uuid_calendar'
            ), payload.get('uuid_message'), payload.get('uuid_opening_reason'
            ), payload.get('uuid_reason_for_closure'), payload.get('code'
            ), payload.get('description'), payload.get('delay'), payload.get(
            'status'), payload.get('country'), payload.get('state_province'
            ), payload.get('data_profile'), payload.get('remember_it')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/dispatchers/', payload=
            payload, **kwargs)
        return response

    def dispatcher(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read Dispatcher

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
            warning_wrong_parameters(self.dispatcher.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/dispatchers/{uuid}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def dispatchers_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Dispatcher

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_notification_provider (string optional): additional filter - payload
            uuid_calendar (string optional): additional filter - payload
            uuid_message (string optional): additional filter - payload
            uuid_opening_reason (string optional): additional filter - payload
            uuid_reason_for_closure (string optional): additional filter - payload
            code (string optional): additional filter - payload
            description (string optional): additional filter - payload
            delay (integer optional): additional filter - payload
            status (string optional): additional filter - payload
            country (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            data_profile (array object optional): additional filter - payload
            remember_it (boolean optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_notification_provider',
            'uuid_calendar', 'uuid_message', 'uuid_opening_reason',
            'uuid_reason_for_closure', 'code', 'description', 'delay',
            'status', 'country', 'state_province', 'data_profile',
            'remember_it']
        payload.get('uuid_notification_provider'), payload.get('uuid_calendar'
            ), payload.get('uuid_message'), payload.get('uuid_opening_reason'
            ), payload.get('uuid_reason_for_closure'), payload.get('code'
            ), payload.get('description'), payload.get('delay'), payload.get(
            'status'), payload.get('country'), payload.get('state_province'
            ), payload.get('data_profile'), payload.get('remember_it')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/dispatchers/{uuid}', payload
            =payload, **kwargs)
        return response

    def dispatchers_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Dispatcher

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/dispatchers/{uuid}', **kwargs
            )
        return response

    def dispatchers_contacts(self, uuid: str, warm_start: bool = False,
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
            send_email (boolean optional): additional filter - parameter
            role_email (string optional): additional filter - parameter
            send_sms (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['not_in', 'name', 'send_email',
            'role_email', 'send_sms', 'skip', 'limit', 'like', 'join', 'count']
        params.get('not_in'), params.get('name'), params.get('send_email'
            ), params.get('role_email'), params.get('send_sms'), params.get(
            'skip'), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_contacts.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/dispatchers/{uuid}/contacts',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dispatchers_contacts_create(self, uuid: str, uuid_contact: str,
        kwargs: dict = None, **payload) -> list:
        """Add Contact

        Args:
            uuid (str, required): uuid
            uuid_contact (str, required): uuid_contact
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            send_email (boolean required): additional filter - payload
            role_email ( optional): additional filter - payload
            send_sms (boolean required): additional filter - payload
            endpoint (array object optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['send_email', 'role_email', 'send_sms',
            'endpoint']
        payload.get('send_email'), payload.get('role_email'), payload.get(
            'send_sms'), payload.get('endpoint')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_contacts_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=
            f'/dispatchers/{uuid}/contacts/{uuid_contact}', payload=payload,
            **kwargs)
        return response

    def dispatchers_contacts_put(self, uuid: str, uuid_contact: str,
        kwargs: dict = None, **payload) -> list:
        """Update Contact

        Args:
            uuid (str, required): uuid
            uuid_contact (str, required): uuid_contact
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            send_email (boolean optional): additional filter - payload
            role_email ( optional): additional filter - payload
            send_sms (boolean optional): additional filter - payload
            endpoint (array object optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['send_email', 'role_email', 'send_sms',
            'endpoint']
        payload.get('send_email'), payload.get('role_email'), payload.get(
            'send_sms'), payload.get('endpoint')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_contacts_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=
            f'/dispatchers/{uuid}/contacts/{uuid_contact}', payload=payload,
            **kwargs)
        return response

    def dispatchers_contacts_delete(self, uuid: str, uuid_contact: str,
        kwargs: dict = None) -> list:
        """Delete Contact

        Args:
            uuid (str, required): uuid
            uuid_contact (str, required): uuid_contact
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/dispatchers/{uuid}/contacts/{uuid_contact}', **kwargs)
        return response

    def dispatchers_groups(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.dispatchers_groups.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/dispatchers/{uuid}/groups',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dispatchers_groups_create(self, uuid: str, uuid_group: str,
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
            f'/dispatchers/{uuid}/groups/{uuid_group}', **kwargs)
        return response

    def dispatchers_groups_delete(self, uuid: str, uuid_group: str,
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
            f'/dispatchers/{uuid}/groups/{uuid_group}', **kwargs)
        return response

    def dispatchers_objects(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.dispatchers_objects.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/dispatchers/{uuid}/objects',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dispatchers_objects_create(self, uuid: str, uuid_object: str,
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
            f'/dispatchers/{uuid}/objects/{uuid_object}', **kwargs)
        return response

    def dispatchers_objects_delete(self, uuid: str, uuid_object: str,
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
            f'/dispatchers/{uuid}/objects/{uuid_object}', **kwargs)
        return response

    def dispatchers_metrics(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.dispatchers_metrics.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/dispatchers/{uuid}/metrics',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dispatchers_metrics_create(self, uuid: str, uuid_metric: str,
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
            f'/dispatchers/{uuid}/metrics/{uuid_metric}', **kwargs)
        return response

    def dispatchers_metrics_delete(self, uuid: str, uuid_metric: str,
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
            f'/dispatchers/{uuid}/metrics/{uuid_metric}', **kwargs)
        return response

    def dispatchers_metric_types(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.dispatchers_metric_types.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/dispatchers/{uuid}/metric_types', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params, **kwargs
            )
        return response

    def dispatchers_metric_types_create(self, uuid: str,
        uuid_metric_type: str, kwargs: dict = None) -> list:
        """Add Metric Type

        Args:
            uuid (str, required): uuid
            uuid_metric_type (str, required): uuid_metric_type
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dispatchers/{uuid}/metric_types/{uuid_metric_type}', **kwargs)
        return response

    def dispatchers_metric_types_delete(self, uuid: str,
        uuid_metric_type: str, kwargs: dict = None) -> list:
        """Remove Metric Type

        Args:
            uuid (str, required): uuid
            uuid_metric_type (str, required): uuid_metric_type
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/dispatchers/{uuid}/metric_types/{uuid_metric_type}', **kwargs)
        return response

    def dispatchers_services(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.dispatchers_services.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/dispatchers/{uuid}/services',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def dispatchers_services_create(self, uuid: str, uuid_service: str,
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
            f'/dispatchers/{uuid}/services/{uuid_service}', **kwargs)
        return response

    def dispatchers_services_delete(self, uuid: str, uuid_service: str,
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
            f'/dispatchers/{uuid}/services/{uuid_service}', **kwargs)
        return response

    def dispatchers_bulk(self, payload: list, warm_start: bool = False,
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
            warning_wrong_parameters(self.dispatchers_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/dispatchers/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def dispatchers_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Create Dispatchers

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
            "uuid_notification_provider": "string", optional
            "uuid_calendar": "string", required
            "uuid_message": "string", required
            "uuid_opening_reason": "string", optional
            "uuid_reason_for_closure": "string", optional
            "code": "string", required
            "description": "string", optional
            "delay": "integer", optional
            "status": "string", required
            "country": "string", optional
            "state_province": "string", optional
            "data_profile": "array object", optional
            "remember_it": "boolean", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/dispatchers/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def dispatchers_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Delete Dispatchers

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
        response = self.execute('POST', path=f'/dispatchers/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def dispatchers_contacts_create_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "send_email": "boolean", optional
            "role_email": "", optional
            "send_sms": "boolean", optional
            "endpoint": "array object", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_contacts_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/create/contacts', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def dispatchers_contacts_delete_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dispatchers/bulk/delete/contacts', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def dispatchers_groups_bulk(self, payload: list,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Read Groups Dispatchers

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
            warning_wrong_parameters(self.dispatchers_groups_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/read/groups', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def dispatchers_groups_create_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_groups_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/create/groups', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def dispatchers_groups_delete_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_group": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dispatchers/bulk/delete/groups', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def dispatchers_objects_bulk(self, payload: list,
        warm_start: bool = False, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Read Objects Dispatchers

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
            warning_wrong_parameters(self.dispatchers_objects_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/read/objects', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def dispatchers_objects_create_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_object": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_objects_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/create/objects', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def dispatchers_objects_delete_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_object": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dispatchers/bulk/delete/objects', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def dispatchers_metric_types_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Link Metric Types

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
            "uuid_dispatcher": "string", required
            "uuid_metric_type": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                dispatchers_metric_types_create_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/create/metric_types', single_page=
            single_page, page_size=page_size, params=params, payload=
            payload, **kwargs)
        return response

    def dispatchers_metric_types_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Unlink Metric Types

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "uuid_dispatcher": "string", required
            "uuid_metric_type": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dispatchers/bulk/delete/metric_types', single_page=
            single_page, page_size=page_size, payload=payload, **kwargs)
        return response

    def dispatchers_metrics_create_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_metric": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_metrics_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/create/metrics', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def dispatchers_metrics_delete_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_metric": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dispatchers/bulk/delete/metrics', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def dispatchers_services_create_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_service": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.dispatchers_services_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/dispatchers/bulk/create/services', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response

    def dispatchers_services_delete_bulk(self, payload: list,
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
            "uuid_dispatcher": "string", required
            "uuid_service": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/dispatchers/bulk/delete/services', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response
