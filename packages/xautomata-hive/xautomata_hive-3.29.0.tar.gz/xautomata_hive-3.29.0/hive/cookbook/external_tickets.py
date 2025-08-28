from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class ExternalTickets(ApiManager):
    """Class that handles all the XAutomata external_tickets APIs"""

    def external_tickets(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read External Tickets

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            in_sla (boolean optional): additional filter - parameter
            uuid_customer (string optional): additional filter - parameter
            uuid_virtual_domain (string optional): additional filter - parameter
            uuid_object (string optional): additional filter - parameter
            object (string optional): additional filter - parameter
            metric_type (string optional): additional filter - parameter
            metric (string optional): additional filter - parameter
            external_itsm (string optional): additional filter - parameter
            external_ticket (string optional): additional filter - parameter
            opening_date_start (string optional): additional filter - parameter
            opening_date_end (string optional): additional filter - parameter
            closing_date_start (string optional): additional filter - parameter
            closing_date_end (string optional): additional filter - parameter
            ticket_type (string optional): additional filter - parameter
            mode (string optional): additional filter - parameter
            severity (string optional): additional filter - parameter
            organization (string optional): additional filter - parameter
            responsibility (string optional): additional filter - parameter
            stage_start_sla_l1 (string optional): additional filter - parameter
            working_period_l1 (string optional): additional filter - parameter
            target_stage_start_sla_l1 (string optional): additional filter - parameter
            stage_start_sla_l2 (string optional): additional filter - parameter
            working_period_l2 (string optional): additional filter - parameter
            target_stage_start_sla_l2 (string optional): additional filter - parameter
            resolution_sla (string optional): additional filter - parameter
            working_period_resolution (string optional): additional filter - parameter
            target_period_resolution (string optional): additional filter - parameter
            null_fields (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'in_sla', 'uuid_customer',
            'uuid_virtual_domain', 'uuid_object', 'object', 'metric_type',
            'metric', 'external_itsm', 'external_ticket',
            'opening_date_start', 'opening_date_end', 'closing_date_start',
            'closing_date_end', 'ticket_type', 'mode', 'severity',
            'organization', 'responsibility', 'stage_start_sla_l1',
            'working_period_l1', 'target_stage_start_sla_l1',
            'stage_start_sla_l2', 'working_period_l2',
            'target_stage_start_sla_l2', 'resolution_sla',
            'working_period_resolution', 'target_period_resolution',
            'null_fields', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('in_sla'), params.get('uuid_customer'
            ), params.get('uuid_virtual_domain'), params.get('uuid_object'
            ), params.get('object'), params.get('metric_type'), params.get(
            'metric'), params.get('external_itsm'), params.get(
            'external_ticket'), params.get('opening_date_start'), params.get(
            'opening_date_end'), params.get('closing_date_start'), params.get(
            'closing_date_end'), params.get('ticket_type'), params.get('mode'
            ), params.get('severity'), params.get('organization'), params.get(
            'responsibility'), params.get('stage_start_sla_l1'), params.get(
            'working_period_l1'), params.get('target_stage_start_sla_l1'
            ), params.get('stage_start_sla_l2'), params.get('working_period_l2'
            ), params.get('target_stage_start_sla_l2'), params.get(
            'resolution_sla'), params.get('working_period_resolution'
            ), params.get('target_period_resolution'), params.get('null_fields'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.external_tickets.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/external_tickets/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def external_tickets_create(self, kwargs: dict = None, **payload) -> list:
        """Create External Ticket

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_customer (string required): additional filter - payload
            uuid_virtual_domain (string optional): additional filter - payload
            uuid_object (string optional): additional filter - payload
            object (string optional): additional filter - payload
            metric_type (string optional): additional filter - payload
            metric (string optional): additional filter - payload
            external_itsm (string required): additional filter - payload
            external_ticket (string required): additional filter - payload
            opening_date (string required): additional filter - payload
            closing_date (string required): additional filter - payload
            ticket_type (None required): additional filter - payload
            mode (None required): additional filter - payload
            severity (None required): additional filter - payload
            organization (string required): additional filter - payload
            responsibility (None required): additional filter - payload
            stage_start_sla_l1 (string required): additional filter - payload
            working_period_l1 (string required): additional filter - payload
            target_stage_start_sla_l1 (string required): additional filter - payload
            stage_start_sla_l2 (string required): additional filter - payload
            working_period_l2 (string required): additional filter - payload
            target_stage_start_sla_l2 (string required): additional filter - payload
            resolution_sla (string required): additional filter - payload
            working_period_resolution (string required): additional filter - payload
            target_period_resolution (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'uuid_virtual_domain',
            'uuid_object', 'object', 'metric_type', 'metric',
            'external_itsm', 'external_ticket', 'opening_date',
            'closing_date', 'ticket_type', 'mode', 'severity',
            'organization', 'responsibility', 'stage_start_sla_l1',
            'working_period_l1', 'target_stage_start_sla_l1',
            'stage_start_sla_l2', 'working_period_l2',
            'target_stage_start_sla_l2', 'resolution_sla',
            'working_period_resolution', 'target_period_resolution']
        payload.get('uuid_customer'), payload.get('uuid_virtual_domain'
            ), payload.get('uuid_object'), payload.get('object'), payload.get(
            'metric_type'), payload.get('metric'), payload.get('external_itsm'
            ), payload.get('external_ticket'), payload.get('opening_date'
            ), payload.get('closing_date'), payload.get('ticket_type'
            ), payload.get('mode'), payload.get('severity'), payload.get(
            'organization'), payload.get('responsibility'), payload.get(
            'stage_start_sla_l1'), payload.get('working_period_l1'
            ), payload.get('target_stage_start_sla_l1'), payload.get(
            'stage_start_sla_l2'), payload.get('working_period_l2'
            ), payload.get('target_stage_start_sla_l2'), payload.get(
            'resolution_sla'), payload.get('working_period_resolution'
            ), payload.get('target_period_resolution')
        if not self._silence_warning:
            warning_wrong_parameters(self.external_tickets_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/external_tickets/', payload
            =payload, **kwargs)
        return response

    def external_ticket(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Read External Ticket

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
            warning_wrong_parameters(self.external_ticket.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/external_tickets/{uuid}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def external_tickets_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update External Ticket

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_customer (string optional): additional filter - payload
            uuid_virtual_domain (string optional): additional filter - payload
            uuid_object (string optional): additional filter - payload
            object (string optional): additional filter - payload
            metric_type (string optional): additional filter - payload
            metric (string optional): additional filter - payload
            external_itsm (string optional): additional filter - payload
            external_ticket (string optional): additional filter - payload
            opening_date (string optional): additional filter - payload
            closing_date (string optional): additional filter - payload
            ticket_type ( optional): additional filter - payload
            mode ( optional): additional filter - payload
            severity ( optional): additional filter - payload
            organization (string optional): additional filter - payload
            responsibility ( optional): additional filter - payload
            stage_start_sla_l1 (string optional): additional filter - payload
            working_period_l1 (string optional): additional filter - payload
            target_stage_start_sla_l1 (string optional): additional filter - payload
            stage_start_sla_l2 (string optional): additional filter - payload
            working_period_l2 (string optional): additional filter - payload
            target_stage_start_sla_l2 (string optional): additional filter - payload
            resolution_sla (string optional): additional filter - payload
            working_period_resolution (string optional): additional filter - payload
            target_period_resolution (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'uuid_virtual_domain',
            'uuid_object', 'object', 'metric_type', 'metric',
            'external_itsm', 'external_ticket', 'opening_date',
            'closing_date', 'ticket_type', 'mode', 'severity',
            'organization', 'responsibility', 'stage_start_sla_l1',
            'working_period_l1', 'target_stage_start_sla_l1',
            'stage_start_sla_l2', 'working_period_l2',
            'target_stage_start_sla_l2', 'resolution_sla',
            'working_period_resolution', 'target_period_resolution']
        payload.get('uuid_customer'), payload.get('uuid_virtual_domain'
            ), payload.get('uuid_object'), payload.get('object'), payload.get(
            'metric_type'), payload.get('metric'), payload.get('external_itsm'
            ), payload.get('external_ticket'), payload.get('opening_date'
            ), payload.get('closing_date'), payload.get('ticket_type'
            ), payload.get('mode'), payload.get('severity'), payload.get(
            'organization'), payload.get('responsibility'), payload.get(
            'stage_start_sla_l1'), payload.get('working_period_l1'
            ), payload.get('target_stage_start_sla_l1'), payload.get(
            'stage_start_sla_l2'), payload.get('working_period_l2'
            ), payload.get('target_stage_start_sla_l2'), payload.get(
            'resolution_sla'), payload.get('working_period_resolution'
            ), payload.get('target_period_resolution')
        if not self._silence_warning:
            warning_wrong_parameters(self.external_tickets_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/external_tickets/{uuid}',
            payload=payload, **kwargs)
        return response

    def external_tickets_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete External Ticket

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/external_tickets/{uuid}',
            **kwargs)
        return response

    def external_tickets_ticket_by_params(self, ticket_type: str,
        uuid_customer: str, warm_start: bool = False, kwargs: dict = None,
        **params) -> list:
        """Pie Charts

        Args:
            ticket_type (str, required): ticket_type
            uuid_customer (str, required): uuid_customer
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string optional): additional filter - parameter
            date_end (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.external_tickets_ticket_by_params
                .__name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/external_tickets/ticket_by_params/{ticket_type}/{uuid_customer}'
            , warm_start=warm_start, params=params, **kwargs)
        return response

    def external_tickets_ticket_by_sla(self, ticket_type: str,
        uuid_customer: str, warm_start: bool = False, kwargs: dict = None,
        **params) -> list:
        """Sla Charge And Resolution

        Args:
            ticket_type (str, required): ticket_type
            uuid_customer (str, required): uuid_customer
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string optional): additional filter - parameter
            date_end (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.external_tickets_ticket_by_sla.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/external_tickets/ticket_by_sla/{ticket_type}/{uuid_customer}',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def external_tickets_ticket_by_date(self, uuid_customer: str,
        warm_start: bool = False, kwargs: dict = None, **params) -> list:
        """History

        Args:
            uuid_customer (str, required): uuid_customer
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string optional): additional filter - parameter
            date_end (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.external_tickets_ticket_by_date.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/external_tickets/ticket_by_date/{uuid_customer}', warm_start
            =warm_start, params=params, **kwargs)
        return response

    def external_tickets_ticket_by_params_customers_filtering(self,
        ticket_type: str, warm_start: bool = False, kwargs: dict = None, **
        params) -> list:
        """Customers Filtering Pie Charts

        Args:
            ticket_type (str, required): ticket_type
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string optional): additional filter - parameter
            date_end (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                external_tickets_ticket_by_params_customers_filtering.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/external_tickets/ticket_by_params/customers_filtering/{ticket_type}/'
            , warm_start=warm_start, params=params, **kwargs)
        return response

    def external_tickets_ticket_by_sla_customers_filtering(self,
        ticket_type: str, warm_start: bool = False, kwargs: dict = None, **
        params) -> list:
        """Customers Filtering Sla Charge And Resolution

        Args:
            ticket_type (str, required): ticket_type
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string optional): additional filter - parameter
            date_end (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                external_tickets_ticket_by_sla_customers_filtering.__name__,
                params, official_params_list)
        response = self.execute('GET', path=
            f'/external_tickets/ticket_by_sla/customers_filtering/{ticket_type}/'
            , warm_start=warm_start, params=params, **kwargs)
        return response

    def external_tickets_ticket_by_date_customers_filtering(self,
        warm_start: bool = False, kwargs: dict = None, **params) -> list:
        """Customers Filtering History

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string optional): additional filter - parameter
            date_end (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                external_tickets_ticket_by_date_customers_filtering.
                __name__, params, official_params_list)
        response = self.execute('GET', path=
            f'/external_tickets/ticket_by_date/customers_filtering/',
            warm_start=warm_start, params=params, **kwargs)
        return response

    def external_tickets_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read External Tickets

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
            warning_wrong_parameters(self.external_tickets_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/external_tickets/bulk/read/', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response

    def external_tickets_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Create External Tickets

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
            "uuid_customer": "string", required
            "uuid_virtual_domain": "string", optional
            "uuid_object": "string", optional
            "object": "string", optional
            "metric_type": "string", optional
            "metric": "string", optional
            "external_itsm": "string", required
            "external_ticket": "string", required
            "opening_date": "string", required
            "closing_date": "string", required
            "ticket_type": "None", required
            "mode": "None", required
            "severity": "None", required
            "organization": "string", required
            "responsibility": "None", required
            "stage_start_sla_l1": "string", required
            "working_period_l1": "string", required
            "target_stage_start_sla_l1": "string", required
            "stage_start_sla_l2": "string", required
            "working_period_l2": "string", required
            "target_stage_start_sla_l2": "string", required
            "resolution_sla": "string", required
            "working_period_resolution": "string", required
            "target_period_resolution": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.external_tickets_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/external_tickets/bulk/create/', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response
