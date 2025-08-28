from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Tests(ApiManager):
    """Class that handles all the XAutomata tests APIs"""

    def tests_last_values(self, warm_start: bool = False,
        kwargs: dict = None, **params) -> list:
        """Check Queues Or Ts Status

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            source (string required): additional filter - parameter
            ts_start (string optional): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        kwargs, params = handling_single_page_methods(kwargs=kwargs, params
            =params)
        official_params_list = ['source', 'ts_start']
        params.get('source'), params.get('ts_start')
        if not self._silence_warning:
            warning_wrong_parameters(self.tests_last_values.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/tests/last_values',
            warm_start=warm_start, params=params, **kwargs)
        return response
