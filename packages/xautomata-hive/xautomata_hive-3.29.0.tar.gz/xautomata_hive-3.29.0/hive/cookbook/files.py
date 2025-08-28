from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Files(ApiManager):
    """Class that handles all the XAutomata files APIs"""

    def files(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """List User Files

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            name (string optional): additional filter - parameter
            username (string optional): additional filter - parameter
            uuid_service (string optional): additional filter - parameter
            type (string optional): additional filter - parameter
            start_ts (string optional): additional filter - parameter
            end_ts (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['name', 'username', 'uuid_service', 'type',
            'start_ts', 'end_ts', 'skip', 'limit', 'like', 'join', 'count']
        params.get('name'), params.get('username'), params.get('uuid_service'
            ), params.get('type'), params.get('start_ts'), params.get('end_ts'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.files.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/files/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def files_create(self, params: dict = False, kwargs: dict = None, **payload
        ) -> list:
        """Post User File

        Args:
            params (dict, optional): additional parameters for the API.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            uuid_service (string optional): additional filter - parameter
            file (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['file']
        payload.get('file')
        if not self._silence_warning:
            warning_wrong_parameters(self.files_create.__name__, payload,
                official_payload_list)
        response = self.execute('POST', path=f'/files/', params=params,
            payload=payload, **kwargs)
        return response

    def files_download(self, uuid: str, warm_start: bool = False,
        kwargs: dict = None) -> list:
        """Download User File

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/files/{uuid}/download',
            warm_start=warm_start, **kwargs)
        return response
