from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class Apple(ApiManager):
    """Class that handles all the XAutomata apple APIs"""

    def apple_login(self, warm_start: bool = False, kwargs: dict = None
        ) -> list:
        """Apple Login

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/apple/login', warm_start=
            warm_start, **kwargs)
        return response

    def apple_callback_create(self, kwargs: dict = None) -> list:
        """Apple Callback

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=f'/apple/callback', **kwargs)
        return response
