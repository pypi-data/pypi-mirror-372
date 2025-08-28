# Xautomata API
Pacchetto che fornisca una interfaccia semplice per usare le API di Xautomata in python

The full documentation can be fount at https://sherlogic.github.io/xautomata-hive/

# Installazione

Il pacchetto si installa come un qualsiasi pacchetto python
```bash
pip install xautomata-hive
```

L'uso interno poi deve essere fatto con il solo nome **hive**
```python
import hive
```


# Manuale d'uso

La libreria *hive* è stata pensata per facilitare l'interazione con le API di XAutomata.
Di seguito si trova un esempio dove viene chiesta la lista dei customers con codice DEMO, e si chiede di ottere il 
risultato paginato di 50 elementi per volta. Il risultato ottenuto (ricompattato in un unica lista) vine poi
usato per estrarre lo uuid del primo customer per chiedere tutti i siti attivi di quel customer scelto.

L'uso di questa libreria garantisce una serie di feature aggiuntive automatiche, gestite dietro le quinte, di cui l'operatore non deve preoccuparsi:
- warmstart: gestione di una cache locale per non rifare piu volte la stessa chiamata se non serve.
- ratelimiter: vengono limitate le chiamate massime al minuto che si possono fare, garantendo l'impossibilita di dare fastidio al server inavvertitamente.
- riautenticazione: se l'autenticazione usata scade per il troppo tempo passato, viene gestita in automatico la riatuenticazione.
- paginazione: le chiamate troppo grandi vengono suddivise in automatico in sottochiamate per non chiedere tutto assieme.
- richiamate: se una chiamata fallisce vengono fatti una serie di tentativi prima di restituire un errore.

**Ogni metodo usato restituisce sempre una lista di elementi.**

Le API trovate sullo swagger del proprio ambiente XAUTOMATA sono chiamabili in maniera semplificata come metodi della
libreria *XautomataAPI*. In alternativa si puo usare una metodologia piu simile alla libreria *request* che richiede l'url
dell'API. Di seguito i due tipi di approccio.

## API come metodi

```python
from hive.api import XautomataApi

root = ''
passw = ''
user = ''

xa = XautomataApi(root=root, user=user, password=passw)

customers = xa.customers(code='DEMO', like=True, page_size=50)

uuid_c = customers[0]['uuid']

sites = xa.sites(uuid_customer=uuid_c, status='A')
```

Si puo vedere come le chiamate alle API hanno la stessa terminologie trovata sullo swagger
cosi come tutti i parametri di filtro evidenziati dentro lo swagger.
Suddetti filtri vengono selezionati semplicemente aggiungendo la chiave:valore nel metodo scelto.
In aggiunta ai filtri degli specifici endpoint sono presenti in aggiunta:
- single_page: XautomataApi pagina sempre la chiamata, ma se impostato a single_page=True, la paginazione viene inibita
- page_size: paginando in automatico, è sempre presente un valore di elementi per pagina. Importante ricordare che il risultato non viene restituito paginato ma sempre ricompattato in una unica risposta.
- warm_start: per le chiamate in lettura è sempre possibile attivare la modalita warmstart che crea una hard cache locale, salvado la risposta in un file. Ogni volta che viene rifatta la stessa chiamata con gli stessi parametri (se in modalita warm_start), il risultato viene preso dal file locale invece che fare la chiamata al server.
- kwargs: questa chiave prevede di ricevere un dizionario e sono valori vengono passati direttamente a *request*. Utile sono a chi sa cosa sta facendo e vuole un comportamento di request diverso dal default.

L'uso di ogni API è specializzato ai parametri specifici di quel API, per avere un dettaglio dei parametri usabili si puo consultare sia il docstring di ogni metodo,
che contiene il dettaglio dei parametri usabili, cosi come lo swagger stesso. Ogni parametro presente nello swagger è riportato un modo speculare nei parametri di XautomataApi.

Nelle situazioni in cui viene richiesto un corpo delle API sotto forma di una lista di oggetti, la lista deve essere fornita per intero, come nell'esempio che segue:

```python
from hive.api import XautomataApi
xa = XautomataApi(root='root', user='user', password='passw')

lista_uuid = ['uuid1', 'uuid2', 'uuid3']

customers = xa.sites_bulk(payload=lista_uuid)
```

## API come url

In alternativa e' possibile usare XautomataApi tramite l'url dell'endpoint. La differenza chiave sul passare tramite
questo approccio e' che si possono chiamare anche API non ancora implemetate in modalita metodi, o manipolare in modo piu
diretto cosa viene passato alla chiamata. Resta ugualmente preferibile usare XautomataApi rispetto a *request*
perche anche tramite la chiamta url vengono mantenute le proprieta di paginazione, cache, riautenticazione etc.

Qui di seguito si puo vedere la chiamata fatta per ottenere i clienti con codice 'DEMO' in modalita url.

```python
from hive.api import XautomataApi
xa = XautomataApi(root='root', user='user', password='passw')

params = {'code': 'DEMO',
          'like': True}

customers = xa.execute(mode='GET', path='/customers/', params=params, page_size=50)
```

a differenza della modalita per metodi, in questo caso i parametri devono essere inseriti all'interno di un dizionario
che viene passato a **params** se si sta fornendo un parametri, e a **payload** se si sta fornendo un *corpo* (tipicamente
usato per le post)

## tips and tricks

esiste un parametri privato *_get_only* che se forzato a True impedisce di usare API di POST/PUT/DELETE. Fatta eccezione
delle bulk e query dove vengono inibite solo le chiamtate che andrebbero ad apportare modifiche al db

```python
from hive.api import XautomataApi
xa = XautomataApi(root='root', user='user', password='passw')
xa._get_only = True
```

# Come e' organizzato XA

La struttura di XA e' complessa e mescola assieme elementi di una gerarchia ad albero con elenedi da grafo, ma se ci si limita
all'interazione con gli elementi dell'asset di un cliente la complessita si riduce un minimo.

Possiamo immaginare di avere l'asset di un cliente e una serie di servizzi che puntano all'asset, andando ad arricchire
l'informazione li presente, oppure aggiungendo funzionalita.

## L'asset

Come **asset** definiamo tutto cio' che costituisce il perimetro fisico del cliente. L'asset e' definito in modo
gerarchico dalle seguenti componenti (in ordine gerarchica decrescente:
- Customer
- Site
- Group
- Object
- Metric_type
- Metric
- Service

Ogniuno di questi livelli contiene informazione, il customer definisce il cliente, i siti definiscono le filiali del cliente, etc.
Ogni livelli e' connesso con un legame uno a molti con il livello sottostante, quindi un sito ha dei gruppi al suo interno, ma un gruppo non puo essere in piu siti.
Esiste un eccezione che sono i gruppi, per la maggior parte del loro uso mantengono una relazione uno a molti con i metric_type, ma un oogetto puo essere contenuto in piu gruppi.
Quindi diciamo che tra i gruppi e gli oggetti c'e' una relazione molti a molti.

Ogni elemento puo essere identificato da una serie di chiavi primarie che comprendono anche lo uuid del suo livello superiore.
Questo ovviamente non e' vero per gli oggetti per via della natura molti a molti con i gruppi.

I servizzi che chiudono la fila, sono una seconda eccezione: hanno una importanza gerarchica simile alle metriche, possono essere legate alle metriche con legame molti a molti ma possono anche non essere legate alle metriche
e vivere completamente slegate dall'asset.
I servizzi rappresentano informazione aggiuntiva calcolata partendo da valori del cliente o altri dati, non necessariamente sono legate all'asset.
Se sono legate all'asset lo sono tramite le metriche, in questi casi esiste un puntamento verso tutte le metriche che hanno contribuito a formare il servizio.

La struttura dal customer al servizio rappresenta l'asset e viene chiamato **albero**.

Per navigare l'albero esistono API che permettono di ottenere le informazioni di legame di un layer con gli altri.
Per fare un esempio, se conosco una **metric** e voglio sapere in quale **object** questa e' contenuta, nei dati della **metric** stessa e' presente lo *uuid* del **metric_type** che la contiene.
Con quel *uuid*, posso ricavare i dettagli del **metric_type** in cui e' presente lo *uuid* del **object** che lo contiene. Con quel *uuid* posso andare a chiedere i dettagli dell'**object** che mi interessava conoscere.

E' altrettando vero nell'altra direzione, noto un **objetc** posso sapere tutti gli **metric_type** che lo compongono, sceltone uno posso chiedere tutte le **metrics** che lo compongono.

Questo modo di navigare l'albero trova alcune variazioni quando si cerca di superare i layer con relazioni molti a molti. Per conoscere quali **groups** contengono un **object** e viceversa, ci sono API apposta che dato
uno dei due layer, ti restituisce il secondo. Questo vale anche per i **services** avengo la stessa natura molti a molti.

Esistono scorciatoie per navigare l'albero, queste scorciatorie vanno sotto forma del set di API **tree_hierarchy**. Questa API sono disegnate per recuperare un elemento nell'albero con tutti i suoi legami con i layer superiori.

## Time series

L'asset rapresenta gli oggetti che producono dati, ma i dati stessi vengono raccolti in un posto diverso. Nello specifico nelle tabelle delle serie temporali.
Tali serie si dividono in due tipologie, serie di **stato** e serie di **valore**.

Le serie di stato sono una successione di informazioni raccolte in dizionari, possono contenere ogni tipo di informazione e portano con se un indice di *gravita*.
Le serie di valore sono successioni di numeri, ideali per raccogliere dati numerici come temperatura, velocita etc.

Le **metrics** sono il layer in cui vengono salvate queste serie. Ogni **metric** e' legata direttamente ad una e una sola serie temporale, sia essa di stato o di valore.

I **services** possono essere legati a serie temporali a loro volta, e , a differenza delle **metrics** possono puntare conemporaneamente sia a serie di valore che di stato.

## Informazioni aggiuntive

Le ralazioni non finiscono con l'asset, esistono una miriade di informazioni aggiuntive esplorabili, come gli **user**, le **dashboard** e cosi via.
Il modo di navigare questi legami e' pero lo stesso con cui si naviga l'albero.

La completa connessione tra tutti gli elementi richiamabili con API e' presentata nello schema qui di seguito

<img src="docs/schema.png"  width="80%" height="80%">


