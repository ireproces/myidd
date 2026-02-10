package com.idd.util;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.standard.StandardTokenizerFactory;
import org.apache.lucene.analysis.custom.CustomAnalyzer;
import org.apache.lucene.analysis.core.LowerCaseFilterFactory;
import org.apache.lucene.analysis.miscellaneous.WordDelimiterGraphFilterFactory;
import org.apache.lucene.document.Document;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.store.FSDirectory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Paths;

public class TxtSearcher {

    private IndexSearcher searcher;
    private QueryParser titleParser;
    private QueryParser abstractParser;

    // Costruttore
    public TxtSearcher(String indexPath) throws IOException {
        Directory dir = FSDirectory.open(Paths.get(indexPath));
        IndexReader reader = DirectoryReader.open(dir);
        this.searcher = new IndexSearcher(reader);

        // Analyzer personalizzato per il titolo
        Analyzer titleAnalyzer = CustomAnalyzer.builder()
                .withTokenizer(StandardTokenizerFactory.class)
                .addTokenFilter(LowerCaseFilterFactory.class)
                .addTokenFilter(WordDelimiterGraphFilterFactory.class)
                .build();

        // Analyzer standard per l'abstract
        Analyzer abstractAnalyzer = new StandardAnalyzer();

        this.titleParser = new QueryParser("title", titleAnalyzer);
        this.abstractParser = new QueryParser("abstract", abstractAnalyzer);
    }

    // Metodo che esegue la ricerca data una query in input
    public void search(String queryStr) throws Exception {

        // Inizializzazione della varibile per le statistiche
        long startTime = System.currentTimeMillis(); // Timer di inizio

        BooleanQuery.Builder booleanQueryBuilder = new BooleanQuery.Builder();
        // Suddivide la query in termini separati dalla virgola e li salva in un array
        String[] terms = queryStr.split(",");
        // Controlla che la query non contenga più di due termini
        if (terms.length > 2) {
            System.out.println("\nALERT: Invalid query format.\n");
            return;
        }

        boolean titleSearched = false, abstractSearched = false;

        // Cicla sui termini per costruire la query effettiva
        for (String term : terms) {
            // Suddivide il termine in campo da interrogare e termine di ricerca
            String[] parts = term.split(":", 2);
            // Controlla che il termine sia nel formato corretto
            if (parts.length == 2) {
                String field = parts[0].trim(); // Campo da interrogare
                String fieldQuery = parts[1].trim(); // Termine di ricerca

                Query query = null;
                // L'istruzione switch indirizza il controllo ad uno dei vari rami a seconda
                // del valore della variabile 'field'
                switch (field) {
                    // Ramo di ricerca sul campo 'title'
                    case "title":
                        query = this.titleParser.parse(fieldQuery);
                        titleSearched = true;
                        break;
                    // Ramo di ricerca sul campo 'abstract'
                    case "abstract":
                        query = this.abstractParser.parse(fieldQuery);
                        abstractSearched = true;
                        break;
                    default:
                        // Se il campo non è valido, stampa un messaggio di errore e termina la ricerca
                        System.out.println("\nALERT: Invalid field. Valid fields are title and abstract.\n");
                        return;
                }

                booleanQueryBuilder.add(query, BooleanClause.Occur.MUST);
            } else {
                // Altrimenti, stampa un messaggio di errore e termina la ricerca
                System.out.println("\nALERT: Invalid query format.\n");
                return;
            }
        }

        BooleanQuery finalQuery = booleanQueryBuilder.build();

        // Esegue una ricerca sincrona sull'indice Lucene e restituisce i primi
        // 10 risultati con punteggio maggiore
        TopDocs results = this.searcher.search(finalQuery, 10);

        long endTime = System.currentTimeMillis(); // Timer di fine
        long totalDocumentsReturned = results.totalHits.value(); // Numero totale di documenti restituiti

        // Controlla che la ricerca abbia prodotto dei risultati
        if (results.totalHits.value() > 0) {
            System.out.println("\n-----" + results.totalHits.value() + " Documents retrieved-----");

            // Cicla sui risultati ottenuti
            for (ScoreDoc hit : results.scoreDocs) {
                // Recupera il documento corrispondente al risultato
                Document doc = this.searcher.getIndexReader().storedFields().document(hit.doc);

                // Stampa solo i campi richiesti
                System.out.println("Title: " + (doc.get("title") != null ? doc.get("title") : "N/A"));
                System.out.println("Abstract: " + (doc.get("abstract") != null ? doc.get("abstract") : "N/A"));
                System.out.println("Score: " + hit.score);
                System.out.println("\n");
            }
        } else {
            // Altrimenti, stampa un messaggio di avviso
            System.out.println("\nNo documents found for the query.\n");
        }

        // Copertura dei campi interrogati
        System.out.println("-----Fields queried-----");
        System.out.printf("• Title queried: %b\n", titleSearched);
        System.out.printf("• Abstract queried: %b\n", abstractSearched);

        // Statistiche di ricerca
        System.out.println("\n-----Search Statistics-----");
        System.out.printf("• Total documents returned: %d\n", totalDocumentsReturned);

        double totalSeconds = (endTime - startTime) / 1000.0;
        System.out.printf("• Total time: %.2f seconds\n", totalSeconds);
        System.out.println("\n");
    }

    public void close() throws IOException {
        this.searcher.getIndexReader().close();
    }

    public static void main(String[] args) {

        // Lettura dell'input da console
        try (BufferedReader br = new BufferedReader(new InputStreamReader(System.in))) {
            String indexPath = "indexes_lucene"; // directory degli indici Lucene
            TxtSearcher searcher = new TxtSearcher(indexPath);

            System.out.println("\nStarting the research program...");
            System.out.println("Enter your query ('title:term', 'abstract:term', 'abstract:\"phrase\"', 'title:x,abstract:y').");
            System.out.println("Or type 'exit' to stop the search.\n");

            String line;
            // Ciclo infinito di lettura delle query
            while (true) {
                System.out.print("Query > ");

                line = br.readLine(); // Legge la riga di input
                // Controlla se la riga è valida o se l'utente ha digitato la keyword di uscita
                if (line == null || line.equalsIgnoreCase("exit")) {
                    System.out.println("Exiting...\n");
                    break;
                }

                // Se la riga è valida, esegue la ricerca
                if (!line.trim().isEmpty()) searcher.search(line);
            }
            searcher.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
