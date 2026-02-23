# Lucene

Libreria scritta in Java, utilizzata di diversi sistemi che diventano prodotti.
E' un core-component per i motori di ricerca dei vari sistemi.

Viene usato anche in ricerca, infatti si usa come baseline per poi fare confronti con nuovi sistemi di information retrieval

## Prospettiva Utente
Faccio una ricerca, e mi ritorna risultati -> 1 caso d'uso

## Prospettiva architetturale
Una query (di solito testuale) viene processata e spezzata in token o termini e vengono confrontati all'interno dell'indice (tipo l'indice invertito). Quando c'è un match, si ritorna il documento della posting list. Si effettua anche un ranking dei risultati.

Queste posting list vanno popolate in qualche modo.

Cioè la posting list va popolata a partire dai dati e documenti su cui il motore di ricerca può afferire.

## Indicizzazione
Lucene lavora su disco, e la prima cosa che si fa è definire una directory dove l'indice esisterà.

Lucene quindi ha come indice una intera directory.

In Lucene un'altra astrazione è quella del Documento.
Il documento è l'entità che può essere restituita a partire da una query.

```Document doc1 = new Document();```

Ci sono diversi attributi su cui fare appiglio, come la data, oppure su base testuale del contenuto del documento. Su base testuale, si può fare ricerca per titolo, oppure sul corpo.

Quindi esistono Campi (un'altra astrazione) che definiamo noi e che si possono usare per effettuare query. Ogni campo ha una posting list.

```doc1.add(new Field("titolo", "Come diventare un ingegnere dei dati, Data engineer?", ..., ...)...);```

Si possono utilizzare i contenuti del documento per creare posting list. Esistono diventono 2 modi, String Fields oppure Text Field. Quando è Text allora il testo è spezzettato e il matching avviene sulle parole singole. Invece uno string field renderà possibile ricerche su stringhe as-is.

In fase di indicizzazione dobbiamo scegliere a priori quali sono i campi da mostrare all'utente in fase di ricerca.

``` Field.Store.YES``` Cioè un campo che è ricercabile e anche mostrato all'utente finale. Invece con ```No``` non si mostra tutto. Ci sono


Si possono specificare nell'indice cosa ignorare e cosa no per ogni campo. Tipo il titolo è case-sensitive ma ignora le Stop Words. Invece nel testo ignoriamo maiuscolo e minoscolo ma includiamo le stopwords.

