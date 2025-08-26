import functools
import hashlib
import inspect
import os
import pickle
import time
import warnings
from datetime import datetime
from typing import Any, List
import requests.exceptions
from hive.exceptions import UnauthorizedException

ratelimiter_count_glob = 1
ratelimiter_daytime_glob = datetime.now()


def chunks(lst: list, n: int) -> List[list]:
    """
    metodo per suddividere una lista madre in una nuova lista composta di sotto liste piu piccole

    Args:
        lst (list): lista da suddividere
        n (int): numero di componenti dentro ogni sotto suddivisione

    Returns:
        chunked_list (list[list]): lista di liste, ogni elemento e' una lista con il numero di oggetti indicati
            provenienti dalla lista madre
    """
    chunked_list = []
    for i, ii in enumerate(range(0, len(lst), n)):
        chunked_list.append(lst[ii:ii + n])
    return chunked_list


def ratelimiter(func=None, per_minute=1000, per_hour=None, per_day=None, per_sec=None):

    if func is None:
        return lambda f: ratelimiter(func=f, per_minute=per_minute, per_hour=per_hour, per_day=per_day, per_sec=per_sec)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # recupero i parametri globali
        global ratelimiter_count_glob, ratelimiter_daytime_glob

        # imposto il limite di conteggi in base al paramtro scelto
        count_limit = per_minute
        time_limit = 60

        if per_sec is not None:
            count_limit = per_sec
            time_limit = 1
        elif per_hour is not None:
            count_limit = per_hour
            time_limit = 60*60
        elif per_day is not None:
            count_limit = per_day
            time_limit = 60*60*24

        # ottengo il risultato della funzione
        res = func(*args, **kwargs)

        # calcolo il tempo trascorso dall'avvio del programma
        delta = datetime.now() - ratelimiter_daytime_glob

        # se il tempo trascoso fin ora e' superiore al limite scelto, si azzerano i contatori
        if delta.total_seconds() > time_limit:
            ratelimiter_daytime_glob = datetime.now()
            ratelimiter_count_glob = 1

        # se il numero di run fatte e' superiore al limite scelto si mette il pausa il programma fino al raggiungimento
        # del tempo limite scelto
        elif ratelimiter_count_glob > count_limit:
            pause = time_limit - delta.total_seconds()
            warnings.warn(f'rate limit hit, request paused for: {pause} sec')
            time.sleep(pause)
            ratelimiter_daytime_glob = datetime.now()
            ratelimiter_count_glob = 1

        ratelimiter_count_glob += 1

        return res

    return wrapper


def refresh(func):
    @functools.wraps(func)
    def behaviour(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnauthorizedException:
            self = args[0]
            self.authenticate()
            return func(*args, **kwargs)

    return behaviour


def timeout_retry(func=None, max_tries: int = 2, sleep_time: int = 60):

    if func is None:
        return lambda f: timeout_retry(func=f, max_tries=max_tries, sleep_time=sleep_time)

    @functools.wraps(func)
    def behaviour(*args, **kwargs):
        count_timeout, count_json = 0, 0

        if max_tries < 2: return func(*args, **kwargs)

        for i in range(max_tries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ReadTimeout:
                print(f'WARNING: timeout reached on get_session, sleep set to {sleep_time}, on retry num {i+1}/{max_tries}')
                time.sleep(sleep_time)
                count_timeout += 1
            except requests.exceptions.JSONDecodeError:
                print(f'WARNING: JSONDecodeError, sleep set to {sleep_time}, on retry num {i+1}/{max_tries}')
                time.sleep(sleep_time)
                count_json += 1

        if max_tries > 1: print(f'WARNING: max retry excided')

        if count_timeout >= count_json:
            raise requests.exceptions.ReadTimeout
        else:
            raise requests.exceptions.JSONDecodeError

    return behaviour


def paginate(single_page: bool, page_size: int, skip: int, limit: int, bulk: bool):
    """Questa funzione è un decorator che abilita la paginazione per una funzione.

    Args:
        single_page: se True, restituisce solo una singola "pagina" di risultati.
        page_size: dimensione della pagina (numero massimo di elementi per chiamata).
        skip: numero di elementi da saltare all'inizio.
        limit: numero massimo di elementi da restituire.
        bulk: se True, gestisce il payload in modalità "bulk", suddividendolo in chunk.
    """
    def attributes(func):
        # Questo è il decorator interno che avvolge la funzione passata (`func`).
        @functools.wraps(func)
        def behaviour(mode, url, headers, payload, params, **kwargs) -> list:
            # `behaviour` è la funzione wrapper che implementa la logica di paginazione.
            # Accetta i parametri della funzione originale (`func`) e aggiunge il supporto alla paginazione.
            result = []  # Lista che conterrà i risultati aggregati.

            # se la chiamata è bulk, il payload deve essere un lista e qui viene divisa in chunk e viene chiamata un
            # chunk per volta, ogni chunk ha la dimensione del page_size
            if bulk and not single_page:  # se la bulk viene richiesta in single_page, ricade nell'uso normale
                # Divide il payload in chunk della dimensione specificata da `page_size`.
                c_payload = chunks(payload, page_size)
                # Per ogni chunk:
                for c in c_payload:
                    # Chiama la funzione originale (`func`) con il chunk corrente.
                    result_partial = func(mode, url, headers, c, params, **kwargs)
                    # Se il risultato non è una lista, lo converte in una lista.
                    if not isinstance(result_partial, list): result_partial = [result_partial]
                    # Aggiunge i risultati parziali alla lista complessiva `result`.
                    result += result_partial

            else:  # Se non è in modalità bulk o se è richiesto single_page:
                size = page_size if not single_page else limit  # Determina la dimensione della pagina.
                params['skip'] = skip  # Imposta il valore iniziale di `skip` nei parametri.
                params['limit'] = min(size, limit)  # Imposta il limite massimo per la pagina corrente.
                while True:  # Ciclo per iterare attraverso le pagine.
                    # Chiama la funzione originale (`func`) con i parametri della pagina corrente.
                    result_partial = func(mode, url, headers, payload, params, **kwargs)
                    # Se il risultato non è una lista, lo converte in una lista.
                    if not isinstance(result_partial, list): result_partial = [result_partial]
                    # Aggiunge i risultati parziali alla lista complessiva `result`.
                    result += result_partial
                    # Aggiorna il valore di `skip` per passare alla pagina successiva.
                    params['skip'] = params['skip'] + size
                    # Interrompe il ciclo se:
                    # - Non ci sono più risultati (`result_partial` è vuoto).
                    # - Il numero di risultati è inferiore alla dimensione della pagina.
                    # - Il numero totale di risultati supera il limite specificato.
                    # - È richiesto il single_page.
                    if not result_partial or len(result_partial) < size or len(result) > limit or single_page: break

            # se count è True il result è una lista con dentro una tupla, in questa maniera viene trasmessa solo la tupla
            if params.get('count', False):
                result = result[0]

            return result

        return behaviour

    return attributes


def warmstart(func=None, active: bool = True, args_ex: list = None, kwargs_ex: list = None, verbose=False):
    """
    decoratore che permette di scaricare in locale il risutato di una funzione o metodo e se ne gli argomenti
    ne il corpo della funzione cambiano vengono restituiti i risultati locali invece di calcolare la funzione.
    Se ci sono argomenti della funzione chiamata che cambiano ad ogni run ma non modificano il risultato, questi
    argomenti possono essere esclusi con i parametri args_ex e kwargs_ex.

    Args:
        func: waste key, it is not to be filled
        active (bool, optional): if False the decorator does nothing, Default to True
        args_ex (list, optional): list of indexes of the function *args to be excluded for the evaluation of the rerun.
            Default to None.
        kwargs_ex (list, optional): list of keys of the function **kwargs to be excluded for the evaluation of the
            rerun. Default to None.
        verbose (bool, optional): if True print the status of the warm_start. Default to False

    Returns: func result

    """
    if not func:
        return lambda f: warmstart(func=f, active=active, args_ex=args_ex, kwargs_ex=kwargs_ex, verbose=verbose)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if active:
            if verbose: print('warm start active')

            directory = 'warmstart'
            in_folder = True
            # si controlla se esiste la cartella warmstart
            if not os.path.isdir(directory):
                # nel caso non si riuscisse a creare una cartella viene usata la posizione dello script per creare i file di warmstart
                in_folder = False
                try:
                    # se non esiste provo a crearne una
                    os.mkdir(directory)
                    # se sono riuscito a creare una cartella da qui in poi viene usata la root della cartella
                    in_folder = True
                except:
                    pass

            # recupero il nome dei file nella cartella
            files_available = os.listdir(directory) if in_folder else os.listdir()
            # hash del corpo e del nome della funzione
            body_and_name = hashlib.md5(inspect.getsource(func).encode()).hexdigest()
            # vengono estratte dalle chiavi per l'hash gli args e kwargs che non devono essere considerati valido
            # per quelle situazioni dove un elemento cambia tra una run e la successiva ma non modifica il risultato
            args_key = list(args).copy()
            kwargs_key = kwargs.copy()

            if args_ex is not None:
                args_val = [args_key[el] for el in args_ex]
                for el in args_val:
                    args_key.remove(el)

            if kwargs_ex is not None:
                for el in kwargs_ex:
                    kwargs_key.pop(el)

            # hash delle chiavi della funzione
            arguments = hashlib.md5((str(kwargs_key) + str(args_key)).encode()).hexdigest()
            # creao un nome che contiene i due hash
            filename = 'temp_' + body_and_name + "_" + arguments + ".pkl"
            # verifico se quel nome e' presente nella cartella
            if filename in files_available:
                if in_folder: filename = './' + directory + '/' + filename
                if verbose: print('read')
                return read(filename)
            else:
                if in_folder: filename = './' + directory + '/' + filename
                if verbose: print('write')
                res = func(*args, **kwargs)
                write(res, filename)
                return res
        else:
            if verbose: print('warm start disabled')
            return func(*args, **kwargs)

    return wrapper


def write(data: Any, filename: str):
    with open(filename, 'wb') as file:
        pickle.dump(obj=data, file=file, protocol=pickle.HIGHEST_PROTOCOL)


def read(filename: str) -> Any:
    with open(filename, 'rb') as file:
        return pickle.load(file=file)
