# Homework 5
Estrazione ed indicizzazione di paper provenienti da Arxiv e PubMed

## Argomenti
- Arxiv: "text-to-sql" or "Natural language to sql"
- PubMed: "glyphosate AND cancer risk"

## Step
- Indicizzazione dei documenti. Scrivere il codice per indicizzare gli articoli utilizzando Elasticsearch (o Lucene), includendo i seguenti campi: titolo, autori, data, abstract, testo completo. 
- Funzionalità di ricerca base. Il sistema deve permettere interrogazioni su uno o più campi, ricerca per parole chiave, combinazioni di query (es. ricerca booleana, full-text). Le funzionalità di ricerca devono essere disponibili tramite una semplice shell su riga di comando e tramite una semplice interfaccia web. 
- Estrazione delle tabelle. Scrivere il codice per estrarre dagli articoli del corpus tutte le tabelle con associati dati di contesto. In particolare, per ogni tabella, estrare il corpo, la caption, i paragrafi che la citano, i paragrafi che contengono termini presenti nella tabella o nella caption (evitando di considerare termini non informativi).
- Estrazione delle figure. Scrivere il codice per estrarre dagli articoli del corpus tutte le figure con associati dati di contesto. In particolare, per ogni figura, estrare l'url, la caption, i paragrafi che la citano, i paragrafi che citano termini presenti nella caption (evitando di considerare termini non informativi).
- Indicizzazione delle tabelle. Scrivere il codice per indicizzare le tabelle utilizzando Elasticsearch (o Lucene). Ogni tabella viene indicizzata come un documento, con i seguenti campi: paper_id (ID dell'articolo), table_id (ID della tabella all’interno dell’articolo),  caption (testo della caption della tabella), body (contenuto della tabella come testo), mentions (lista dei paragrafi del paper che citano la tabella), context_paragraphs (lista dei paragrafi del paper che contengono termini presenti nella tabella o nella caption).
- Indicizzazione delle figure. Scrivere il codice per indicizzare le figure utilizzando Elasticsearch (o Lucene). Ogni figura viene indicizzata come un documento, con i seguenti campi: url (url della figura), paper_id (ID dell'articolo), table_id (ID della figura all’interno dell’articolo),  caption (testo della caption della figura), mentions (lista dei paragrafi del paper che citano la figura).
- Funzionalità di ricerca avanzate. Il sistema deve permettere interrogazioni per tabelle, figure, documenti su uno o più campi, ricerca per parole chiave, combinazioni di query (es. ricerca booleana, full-text). Le funzionalità di ricerca devono essere disponibili tramite una semplice shell su riga di comando e tramite una semplice interfaccia web. 

# Documentazione API Esterne
## Arxiv
Per arxiv [qui](https://info.arxiv.org/help/api/user-manual.html#31-calling-the-api) dovrebbe esserci la maggiorparte della roba

In particolare, bisogna usare usare i parametri nell'URL per far scorrere la finestra dell'indice.

## PubMed
Per PubMed, si accede all'indice con 
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer+immunotherapy&retmode=json&retstart=20&retmax=20
```
Da notare come **retstart** e **retmax** ci consentono di fare sliding window sull'indice

Per scaricare i metadati di un certo paper, bisogna utilizzare
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=41391682&retmode=xml
```

Specificando l'id del paper
# Client & Indexer

Sono disponibili due sistemi principale, il primo è un client che permette di interagire con elastic search tramite una GUI, mentre il secondo sistema è quello che si occupa di scaricare i dati, elaborarli secondo le specifiche e indicizzarli all'interno di elastic search.

# Estrazione Tabelle, Paragrafi e Figure
Dobbiamo non solo estrarre le tabelle, ma anche i paragrafi che le citano direttamente per nome oppure che citano termini contenuti all'interno della tabella.
Questa vuol dire che esiste una relazione one-to-many tra tabella-paragrafo

Il problema diventa quindi l'individuazione della tabella, l'estrazione dati dall'interno della tabella da poter usare per l'indicizzazione e da poter usare per rilevare i paragrafi.

Inoltre bisogna poter rilevare i paragrafi, estrarli e vedere se all'interno viene citato la tabella i-esima

Si potrebbe anche invertire, cioè, prima rileviamo all'interno del paper tutti i paragrafi e tutti le tabelle che citano per singolo paragrafo, e alla fine estraiamo anche le tabelle e le colleghiamo alle informazioni relative dei paragrafi.

## arXiv
### Tabelle
Una tabella è incluse sempre nei TAG ```<figure> ... </figure>``` con class="ltx_table". Questo ci fa subito trovare le tabelle.
Inoltre, gli HTML delle tabelle hanno anche un ID univoco che specificano in quale capitolo si trovano e il loro id della tabella ad esempio id="S1.T1" che vuol dire "figura 1 in sezione 1"

Inoltre all'interno c'è il tag ```<figcaption>...</figcaption>``` che delinea la caption della tabella in questo caso.
### Paragrafi
Per i paragrafi esistono tag html ```<p>``` oppure ```<div>``` con class="ltx_p" oppure class="ltx_para" oppure class="ltx_paragraph".

La classe ```ltx_p``` è quella che appare più spesso e probabilmente quella su cui fare più affidamento.
### Figure
Una figura, è sempre inclusa nei tag ```<figure> ... </figure>``` con class="ltx_figure". Questo ci fa subito trovare le tabelle.
Inoltre, gli HTML delle figure hanno anche un ID univoco che specificano in quale capitolo si trovano e il loro id della tabella ad esempio id="S1.F1" che vuol dire "figura 1 in sezione 1"

Inoltre all'interno c'è il tag ```<figcaption>...</figcaption>``` che delinea la caption della tabella in questo caso.
### Rilevazione di citazioni relative a tabelle e figure dentro ai paragrafi
Si utilizza ```<a class="ltx_ref" ...``` per citare cose all'interno dei paragrafi. Quindi estratte le figure, si capisce 

## PubMed
### Tabelle
per le tabelle si può fare utilizzo di ```<table-wrap>``` con relativo id.

All'interno troveremo ```<label>, <caption>, <table>``` che contiene i dati effettivi
### Paragrafi
Per i paragrafi abbiamo ```<p>```

All'interno del paragrafo la citazione avviene 
### Figure
Per le figure si sfrutta il tag in xml ```<fig>``` con relativo id.

Nel fig abbiamo anche ```<caption>``` che contiene ciò che ci interessa
### Rilevazione di citazioni relative a tabelle e figure dentro ai paragrafi

# Requisiti
- Python 3.14
- Dipendenze in requirements.txt