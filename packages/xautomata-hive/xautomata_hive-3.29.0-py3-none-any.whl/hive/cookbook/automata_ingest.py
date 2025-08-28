from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class AutomataIngest(ApiManager):
    """Class that handles all the XAutomata automata_ingest APIs"""

    def automata_ingest_create(self, kwargs: dict = None, **payload) -> list:
        """Insert Automata

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            extended_attributes (string optional): additional filter - payload
            uuid_automata_instance (string required): additional filter - payload
            timestamp (integer required): additional filter - payload
            group_label (string optional): additional filter - payload
            xal_name (string optional): additional filter - payload
            automata_name (string optional): additional filter - payload
            automata_version (string optional): additional filter - payload
            current_state (string optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['extended_attributes',
            'uuid_automata_instance', 'timestamp', 'group_label',
            'xal_name', 'automata_name', 'automata_version', 'current_state']
        payload.get('extended_attributes'), payload.get(
            'uuid_automata_instance'), payload.get('timestamp'), payload.get(
            'group_label'), payload.get('xal_name'), payload.get(
            'automata_name'), payload.get('automata_version'), payload.get(
            'current_state')
        if not self._silence_warning:
            warning_wrong_parameters(self.automata_ingest_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/automata_ingest/', payload=
            payload, **kwargs)
        return response
