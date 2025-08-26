from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class QrCode(ApiManager):
    """Class that handles all the XAutomata qr_code APIs"""

    def qr_code(self, warm_start: bool = False, kwargs: dict = None) -> list:
        """Get Qr Code

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('GET', path=f'/qr_code', warm_start=
            warm_start, **kwargs)
        return response
