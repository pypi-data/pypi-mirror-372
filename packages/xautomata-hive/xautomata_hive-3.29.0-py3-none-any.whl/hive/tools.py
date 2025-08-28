def dict_by_request(responce_list: list, univocal_keys: list) -> dict:
    """
    Given a responce list it turn the List[Dict] into a Dict[Dict] where the keys are the univocal_keys given in the arguments.

    Args:
        responce_list (list[dict]): API responce
        univocal_keys (list[str]): list of keys to use to identify the univocal arguments to be turned into the new dict keys

    Returns: dict
    """
    responce_dict = dict()
    for cont in responce_list:
        chiave = tuple(cont[k] for k in univocal_keys)
        responce_dict[chiave] = cont
    return responce_dict


def order_by_request(params_list, responce_list, univocal_keys) -> list:
    """
    Given a API responce, its univocal keys and the params list used to get that responce, a new
    Args:
        params_list: params given to the API
        responce_list: API responce
        univocal_keys: keys that represents the univocal field of the responce

    Returns: List

    """
    responce_dict = dict_by_request(responce_list, univocal_keys)
    response_content = [None for _ in range(len(params_list))]
    for i, ele in enumerate(params_list):
        chiave = tuple(ele[k] for k in univocal_keys)
        if chiave in responce_dict:
            response_content[i] = responce_dict[chiave]
        else:
            response_content[i] = None
    return response_content
