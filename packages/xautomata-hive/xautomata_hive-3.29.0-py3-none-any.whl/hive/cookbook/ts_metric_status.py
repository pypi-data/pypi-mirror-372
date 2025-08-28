from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class TsMetricStatus(ApiManager):
    """Class that handles all the XAutomata ts_metric_status APIs"""

    def ts_metric_status(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Status Metrics

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            uuid_metric (string optional): additional filter - parameter
            timestamp_start (string optional): additional filter - parameter
            timestamp_end (string optional): additional filter - parameter
            ingest_timestamp_start (string optional): additional filter - parameter
            ingest_timestamp_end (string optional): additional filter - parameter
            database_timestamp_start (string optional): additional filter - parameter
            database_timestamp_end (string optional): additional filter - parameter
            status (string optional): additional filter - parameter
            ranking (integer optional): additional filter - parameter
            description (string optional): additional filter - parameter
            null_fields (string optional): additional filter - parameter
            merge_last_value (boolean optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'uuid_metric', 'timestamp_start',
            'timestamp_end', 'ingest_timestamp_start',
            'ingest_timestamp_end', 'database_timestamp_start',
            'database_timestamp_end', 'status', 'ranking', 'description',
            'null_fields', 'merge_last_value', 'skip', 'limit', 'like',
            'join', 'count']
        params.get('sort_by'), params.get('uuid_metric'), params.get(
            'timestamp_start'), params.get('timestamp_end'), params.get(
            'ingest_timestamp_start'), params.get('ingest_timestamp_end'
            ), params.get('database_timestamp_start'), params.get(
            'database_timestamp_end'), params.get('status'), params.get(
            'ranking'), params.get('description'), params.get('null_fields'
            ), params.get('merge_last_value'), params.get('skip'), params.get(
            'limit'), params.get('like'), params.get('join'), params.get(
            'count')
        if not self._silence_warning:
            warning_wrong_parameters(self.ts_metric_status.__name__, params,
                official_params_list)
        response = self.execute('GET', path=f'/ts_metric_status/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def ts_metric_status_bulk(self, payload: list, warm_start: bool = False,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None,
        **params) -> list:
        """Bulk Read Status Metrics

        Args:
            payload (list[dict], optional): List dict to create.
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            ts_start (string required): additional filter - parameter
            ts_end (string required): additional filter - parameter
            merge_last_value (boolean optional): additional filter - parameter

        Examples:
            payload = 
          [
            "uuid": "str", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['ts_start', 'ts_end', 'merge_last_value']
        params.get('ts_start'), params.get('ts_end'), params.get(
            'merge_last_value')
        if not self._silence_warning:
            warning_wrong_parameters(self.ts_metric_status_bulk.__name__,
                params, official_params_list)
        response = self.execute('POST', path=
            f'/ts_metric_status/bulk/read/', single_page=single_page,
            page_size=page_size, warm_start=warm_start, params=params,
            payload=payload, **kwargs)
        return response
