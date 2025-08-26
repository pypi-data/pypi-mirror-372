from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Sites(ApiManager):
    """Class that handles all the XAutomata sites APIs"""

    def sites(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Read Sites

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
            uuid_customer (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            code (string optional): additional filter - parameter
            description (string optional): additional filter - parameter
            address (string optional): additional filter - parameter
            zip_code (string optional): additional filter - parameter
            city (string optional): additional filter - parameter
            country (string optional): additional filter - parameter
            notes (string optional): additional filter - parameter
            state_province (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            severity (string optional): additional filter - parameter
            filter_group_types (string optional): additional filter - parameter
            count_children (boolean optional): additional filter - parameter
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
            'uuid_customer', 'type', 'code', 'description', 'address',
            'zip_code', 'city', 'country', 'notes', 'state_province',
            'status', 'severity', 'filter_group_types', 'count_children',
            'extract_severity', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'not_fields'), params.get('uuid_customer'), params.get('type'
            ), params.get('code'), params.get('description'), params.get(
            'address'), params.get('zip_code'), params.get('city'), params.get(
            'country'), params.get('notes'), params.get('state_province'
            ), params.get('status'), params.get('severity'), params.get(
            'filter_group_types'), params.get('count_children'), params.get(
            'extract_severity'), params.get('skip'), params.get('limit'
            ), params.get('like'), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/sites/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def sites_create(self, params: dict = False, kwargs: dict = None, **payload
        ) -> list:
        """Create Site

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            geocode (boolean optional): additional filter - parameter
            uuid_customer (string required): additional filter - payload
            type (string optional): additional filter - payload
            code (string required): additional filter - payload
            description (string required): additional filter - payload
            address (string required): additional filter - payload
            zip_code (string required): additional filter - payload
            city (string required): additional filter - payload
            country (string required): additional filter - payload
            notes (string optional): additional filter - payload
            state_province (string required): additional filter - payload
            status (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'type', 'code',
            'description', 'address', 'zip_code', 'city', 'country',
            'notes', 'state_province', 'status']
        payload.get('uuid_customer'), payload.get('type'), payload.get('code'
            ), payload.get('description'), payload.get('address'), payload.get(
            'zip_code'), payload.get('city'), payload.get('country'
            ), payload.get('notes'), payload.get('state_province'
            ), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/sites/', params=params,
            payload=payload, **kwargs)
        return response

    def site(self, uuid: str, warm_start: bool = False, kwargs: dict = None,
        **params) -> list:
        """Read Site

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
            warning_wrong_parameters(self.site.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/sites/{uuid}', warm_start=
            warm_start, params=params, **kwargs)
        return response

    def sites_put(self, uuid: str, params: dict = False,
        kwargs: dict = None, **payload) -> list:
        """Update Site

        Args:
            params (dict, optional): additional parameters for the API.
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            geocode (boolean optional): additional filter - parameter
            uuid_customer (string optional): additional filter - payload
            type (string optional): additional filter - payload
            code (string optional): additional filter - payload
            description (string optional): additional filter - payload
            address (string optional): additional filter - payload
            zip_code (string optional): additional filter - payload
            city (string optional): additional filter - payload
            country (string optional): additional filter - payload
            notes (string optional): additional filter - payload
            state_province (string optional): additional filter - payload
            status (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['uuid_customer', 'type', 'code',
            'description', 'address', 'zip_code', 'city', 'country',
            'notes', 'state_province', 'status']
        payload.get('uuid_customer'), payload.get('type'), payload.get('code'
            ), payload.get('description'), payload.get('address'), payload.get(
            'zip_code'), payload.get('city'), payload.get('country'
            ), payload.get('notes'), payload.get('state_province'
            ), payload.get('status')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_put.__name__, payload,
                official_payload_list)
        response = self.execute('PUT', path=f'/sites/{uuid}', params=params,
            payload=payload, **kwargs)
        return response

    def sites_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Site

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/sites/{uuid}', **kwargs)
        return response

    def sites_groups(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.sites_groups.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/sites/{uuid}/groups',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def sites_contacts(self, uuid: str, warm_start: bool = False,
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
            warning_wrong_parameters(self.sites_contacts.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/sites/{uuid}/contacts',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def sites_contacts_create(self, uuid: str, uuid_contact: str,
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
            warning_wrong_parameters(self.sites_contacts_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=
            f'/sites/{uuid}/contacts/{uuid_contact}', payload=payload, **kwargs
            )
        return response

    def sites_contacts_put(self, uuid: str, uuid_contact: str,
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
            warning_wrong_parameters(self.sites_contacts_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=
            f'/sites/{uuid}/contacts/{uuid_contact}', payload=payload, **kwargs
            )
        return response

    def sites_contacts_delete(self, uuid: str, uuid_contact: str,
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
            f'/sites/{uuid}/contacts/{uuid_contact}', **kwargs)
        return response

    def sites_coordinates(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Coordinates

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            uuid_site (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'uuid_site', 'skip', 'limit',
            'like', 'join', 'count']
        params.get('sort_by'), params.get('uuid_site'), params.get('skip'
            ), params.get('limit'), params.get('like'), params.get('join'
            ), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_coordinates.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/sites/coordinates/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def sites_coordinates_create(self, kwargs: dict = None, **payload) -> list:
        """Create Coordinates

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            longitude (number required): additional filter - payload
            latitude (number required): additional filter - payload
            uuid_site (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['longitude', 'latitude', 'uuid_site']
        payload.get('longitude'), payload.get('latitude'), payload.get(
            'uuid_site')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_coordinates_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/sites/coordinates/',
            payload=payload, **kwargs)
        return response

    def sites_coordinates_put(self, uuid_site: str, kwargs: dict = None, **
        payload) -> list:
        """Update Coordinates

        Args:
            uuid_site (str, required): uuid_site
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            longitude (number optional): additional filter - payload
            latitude (number optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['longitude', 'latitude']
        payload.get('longitude'), payload.get('latitude')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_coordinates_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=
            f'/sites/coordinates/{uuid_site}', payload=payload, **kwargs)
        return response

    def sites_coordinates_delete(self, uuid_site: str, kwargs: dict = None
        ) -> list:
        """Delete Coordinates

        Args:
            uuid_site (str, required): uuid_site
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=
            f'/sites/coordinates/{uuid_site}', **kwargs)
        return response

    def sites_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read Sites

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
            warning_wrong_parameters(self.sites_bulk.__name__, params,
                official_params_list)
        response = self.execute('POST', path=f'/sites/bulk/read/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, payload=payload, **kwargs)
        return response

    def sites_read_by_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Read Sites By Uuid Customer And Code

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
            "code": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/sites/bulk/read_by/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, payload=payload, **kwargs)
        return response

    def sites_create_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None, **params) -> list:
        """Bulk Create Sites

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            geocode (boolean optional): additional filter - parameter
            best_effort (boolean optional): additional filter - parameter

        Examples:
            payload = 
          [
           {
            "uuid_customer": "string", required
            "type": "string", optional
            "code": "string", required
            "description": "string", required
            "address": "string", required
            "zip_code": "string", required
            "city": "string", required
            "country": "string", required
            "notes": "string", optional
            "state_province": "string", required
            "status": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['geocode', 'best_effort']
        params.get('geocode'), params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_create_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=f'/sites/bulk/create/',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def sites_delete_bulk(self, payload: list, single_page: bool = False,
        page_size: int = 50, kwargs: dict = None) -> list:
        """Bulk Delete Sites

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
        response = self.execute('POST', path=f'/sites/bulk/delete/',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def sites_contacts_create_bulk(self, payload: list,
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
            "uuid_site": "string", required
            "type": "string", optional
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_contacts_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=f'/sites/bulk/create/contacts',
            single_page=single_page, page_size=page_size, params=params,
            payload=payload, **kwargs)
        return response

    def sites_contacts_delete_bulk(self, payload: list,
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
            "uuid_site": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/sites/bulk/delete/contacts',
            single_page=single_page, page_size=page_size, payload=payload,
            **kwargs)
        return response

    def sites_coordinates_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Create Coordinates

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
            "longitude": "number", required
            "latitude": "number", required
            "uuid_site": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['best_effort']
        params.get('best_effort')
        if not self._silence_warning:
            warning_wrong_parameters(self.sites_coordinates_create_bulk.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/sites/coordinates/bulk/create/', single_page=single_page,
            page_size=page_size, params=params, payload=payload, **kwargs)
        return response
