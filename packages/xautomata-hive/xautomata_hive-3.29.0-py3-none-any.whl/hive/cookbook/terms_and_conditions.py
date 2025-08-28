from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class TermsAndConditions(ApiManager):
    """Class that handles all the XAutomata terms_and_conditions APIs"""

    def terms_and_conditions(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Get Terms And Conditions

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            version (integer optional): additional filter - parameter
            privacy (string optional): additional filter - parameter
            terms (string optional): additional filter - parameter
            publication_date_start (string optional): additional filter - parameter
            publication_date_end (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'version',
            'privacy', 'terms', 'publication_date_start',
            'publication_date_end', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get('version'
            ), params.get('privacy'), params.get('terms'), params.get(
            'publication_date_start'), params.get('publication_date_end'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.terms_and_conditions.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/terms_and_conditions/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def terms_and_conditions_create(self, kwargs: dict = None, **payload
        ) -> list:
        """Create Terms And Conditions

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            privacy (string optional): additional filter - payload
            terms (string optional): additional filter - payload
            version (integer required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['privacy', 'terms', 'version']
        payload.get('privacy'), payload.get('terms'), payload.get('version')
        if not self._silence_warning:
            warning_wrong_parameters(self.terms_and_conditions_create.
                __name__, payload, official_payload_list)
        response = self.execute('POST', path=f'/terms_and_conditions/',
            payload=payload, **kwargs)
        return response
