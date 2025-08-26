from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Jobs(ApiManager):
    """Class that handles all the XAutomata jobs APIs"""

    def jobs(self, warm_start: bool = False, single_page: bool = False,
        page_size: int = 5000, kwargs: dict = None, **params) -> list:
        """Get Jobs

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            name (string optional): additional filter - parameter
            state (string optional): additional filter - parameter
            exception (string optional): additional filter - parameter
            result (string optional): additional filter - parameter
            username (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'name', 'state',
            'exception', 'result', 'username', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('name'
            ), params.get('state'), params.get('exception'), params.get(
            'result'), params.get('username'), params.get('skip'), params.get(
            'limit'), params.get('like'), params.get('join'), params.get(
            'count')
        if not self._silence_warning:
            warning_wrong_parameters(self.jobs.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/jobs/', single_page=
            single_page, page_size=page_size, warm_start=warm_start, params
            =params, **kwargs)
        return response

    def job(self, uuid: str, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Get Job By Uuid

        Args:
            uuid (str, required): uuid
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/jobs/{uuid}', warm_start=
            warm_start, **kwargs)
        return response
