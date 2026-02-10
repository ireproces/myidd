# Homework 2 – Indicizzazione e Ricerca con Apache Lucene

## 🧠 Descrizione del progetto
Questo progetto implementa un **motore di indicizzazione e ricerca** basato su [Apache Lucene](https://lucene.apache.org/).\
Il programma è in grado di:
- indicizzare una collezione di file di testo (`.txt`);
- eseguire interrogazioni, sui campi `title` ed `abstract` dei file, tramite query testuali.

---

## 📁 Struttura del progetto
```
hw2-idd
├── downloadfiles/
│   └── download.py
├── txt-indexer-searcher/
│   └── src/main/java/com/idd/util/
│       ├── TxtIndexer.java
│       └── TxtSearcher.java
│   └── pom.xml
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🚀 Run del progetto
1. Clonare il repository in locale
2. All'interno della directory `downloadfiles`, eseguire lo script python `download.py`
3. Al termine dell'esecuzione dello script, all'interno della directory corrente, verranno creati:
    - una directory `papers_txt` (contenente i 50 papers estratti)
    - un file `arxiv_page.html` (pagina di archivio in html)
4. All'interno della directory `txt-indexer-searcher`, eseguire la classe `TxtIndexer.java`. Questo creerà la directory `indexes_lucene` contenente i file di indicizzazione
5. Sempre nella directory `txt-indexer-searcher`, eseguire la classe `TxtSearcher.java`
6. Ora è possibile eseguire query sul motore di ricerca Lucene, per terminare digitare la keyword `exit`

---

## ⚙️ Funzionalità principali

### 🧾 Processo di estrazione e creazione dei file `.txt`
La **creazione dei file** di testo utilizzati per l’indicizzazione è **automatizzata** tramite lo script `download.py`, che utilizza **Selenium** e **lxml** per scaricare e processare i risultati della ricerca su [arXiv.org](https://arxiv.org).

Lo script avvia un browser Chrome in cui viene aperta la pagina di ricerca di arXiv, configurata per mostrare i primi 50 articoli di Machine Learning.
Una volta caricata interamente la pagina, il contenuto HTML viene salvato in un file `arxiv_page.html`.

Utilizzando lxml, viene effettuato il parsing della pagina salvata.
Ogni elemento `li` contenente la classe `arxiv-result` rappresenta un paper.\
Per ciascun paper vengono estratti i campi richiesti tramite XPath:
- Titolo $\to$ `XPath: .//p[contains(@class,"title")]/text()`
- Abstract $\to$ `XPath: .//span[contains(@class,"abstract-full")]//text()`

Ogni paper viene salvato nella cartella `papers_txt/` con un nome normalizzato nel formato desiderato ed una struttura standard.

### 🏗️ Processo di indicizzazione
La classe `TxtIndexer.java` scansiona tutti i file `.txt` contenuti nella directory locale `papers_txt`.\
Da ognuno estrae:
- **Titolo** $\to$ linea che segue la parola chiave `Title:`
- **Abstract** $\to$ linee che seguono la parola chiave `Abstract:`

Successivamente, crea un indice Lucene contenente i campi:\
`title`, `abstract`, `filename`, `path`

Infine, stampa **statistiche sui tempi di indicizzazione**:
- il numero totale di file indicizzati
- il tempo totale e medio per file
- il numero totale di documenti presenti nell'indice

### 🔎 Processo di ricerca
La classe `TxtSearcher.java` supporta sia **term query** che **phrase query**. In particolare, legge query da console sui campi `title` e `abstract` (4 forme sintattiche supportate):
- title:term
- abstract:term
- abstract:"phrase"
- title:x,abstract:y

Per ogni query mostra:
- titolo, abstract e punteggio di rilevanza dei documenti trovati
- i campi interrogati
- alcune statistiche di ricerca (come il numero di documenti trovati e il tempo totale di ricerca)

Il programma continua a ricevere query finché l’utente non digita la keyword `exit`.

---

## 👨‍💻 Autore ed Info sul corso
**Nome**: Irene Proietti Cesarini\
**Corso**: Ingegneria dei Dati\
**Anno accademico**: 2025/2026