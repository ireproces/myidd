package com.idd.util;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.Locale;


public class TxtIndexer {

    private final IndexWriter writer;

    // Costruttore
    public TxtIndexer(String indexPath) throws IOException {
        Directory dir = FSDirectory.open(Paths.get(indexPath)); // Crea un oggetto Directory per l'indice
        
        Analyzer analyzer = new StandardAnalyzer(); // Crea un analizzatore per l'indice
        
        // Assegna l'analizzatore alla configurazione dell'IndexWriter
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        
        // Imposta l'IndexWriter in modalità CREATE per sovrascrivere l'indice esistente
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE);

        // Crea un oggetto IndexWriter che si occupa di aggiungere, aggiornare
        // e cancellare documenti da un indice Lucene
        this.writer = new IndexWriter(dir, config);
    }

    // Metodo per ottenere un array di oggetti File estratti dalla
    // directory passata in input (tramite path)
    public File[] getFiles(String txtFolderPath) {

        // Crea un oggetto File che rappresenta la cartella contenente i papers .txt
        File txtFolder = new File(txtFolderPath);
        // Controllo se la directory esiste e se è leggibile
        if (!txtFolder.exists() || !txtFolder.isDirectory()) {
            System.out.println("ALERT: La directory " + txtFolderPath + " non esiste");
            return new File[0];
        } else if (!txtFolder.canRead()) {
            System.out.println("ALERT: La directory " + txtFolderPath + " non è leggibile");
            return new File[0];
        }

        // Filtra solo i file .txt (o .TXT) contenuti nella directory e li resituisce
        // sottoforma di array di oggetti File
        File[] txtFiles = txtFolder.listFiles((dir, name) -> {
            File f = new File(dir, name);
            return f.isFile() && name.toLowerCase(Locale.ROOT).endsWith(".txt");
        });

        System.out.println("Found " + txtFiles.length + " .txt files in directory " + txtFolderPath + "\n");

        return txtFiles;
    }

    public void indexTxtFiles(String txtFolderPath) throws IOException {
        System.out.println("Starting indexing...");

        // Ottiene l'array di file .txt da indicizzare
        File[] txtFiles = getFiles(txtFolderPath);
        if (txtFiles == null || txtFiles.length == 0) {
            System.out.println("ALERT: No files to index.");
            return;
        }
        
        // Inizializzazione delle variabili per le statistiche
        long startTime = System.currentTimeMillis(); // Timer di inizio
        int count = 0; // Contatore per i file indicizzati

        // Cicla su tutti i file dell'array
        for (File file : txtFiles) {
            // Controlla se il file è leggibile
            if (file.canRead()) {
                // In caso affermativo, indicizza il file tramite funzione apposita
                System.out.println("Indexing file: " + file.getName());
                indexSingleFile(file); // Indicizza singolo file tramite funzione apposita

                count++; // Incrementa il contatore se l'indicizzazione ha avuto successo
            } else {
                // Altrimenti, stampa un messaggio di alert
                System.out.println("ALERT: Cannot read file " + file.getName());
            }
        }
        long endTime = System.currentTimeMillis(); // Timer di fine
        System.out.printf("Indexing completed.\n");
        
        // Calcolo delle statistiche temporali
        double totalSeconds = (endTime - startTime) / 1000.0;
        double avgSeconds = totalSeconds / Math.max(count, 1);

        // Stampa delle statistiche
        System.out.printf("\nStatistics:\n");
        System.out.printf("• Total files indexed: %d\n", count);
        System.out.printf("• Total time: %.2f seconds\n", totalSeconds);
        System.out.printf("• Average time per file: %.2f seconds\n", avgSeconds);
    }

    // Metodo per estrarre il titolo dal File passato in input
    private String extractTitle(File file) throws IOException {

        // Carica il file in un BufferedReader per leggerlo riga per riga
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            String line;
            // Cicla su tutte le righe del file non nulle
            while ((line = br.readLine()) != null) {
                line = line.trim(); // Rimuove spazi bianchi iniziali e finali
                if (line.isEmpty()) continue; // Salta righe vuote

                // Se la riga inizia con "title:" (o "Title:"), estrae e restituisce il titolo
                if (line.toLowerCase(Locale.ROOT).startsWith("title:")) {
                    // Restituisce il titolo rimuovendo tag iniziale e spazi bianchi
                    return line.substring(6).trim();
                }   
            }
        }
        // br ed fr vengono chiusi automaticamente qui grazie al try-with-resources

        // Se non viene trovato alcun titolo, restituisce "Unknown title"
        return "Unknown title";
    }

    // Metodo per estrarre l'abstract dal File passato in input
    private String extractAbstract(File file) throws IOException {
        StringBuilder sb = new StringBuilder();
        boolean abstractFound = false; // Flag per indicare se l'abstract è stato trovato

        // Carica il file in un BufferedReader per leggerlo riga per riga
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            String line;
            // Cicla su tutte le righe del file non nulle
            while ((line = br.readLine()) != null) {
                line = line.trim(); // Rimuove spazi bianchi iniziali e finali
                if (line.isEmpty()) continue; // Salta righe vuote

                if (!abstractFound) {
                    // Se l'abstract non è stato ancora trovato

                    // Verifica se la riga inizia con "abstract:" (o "Abstract:")
                    if (line.toLowerCase(Locale.ROOT).startsWith("abstract:")){
                        abstractFound = true;
                        if (line.length() > 9) { // evita StringIndexOutOfBounds
                            // Estrae il testo dopo "abstract:" e lo aggiunge al StringBuilder
                            sb.append(line.substring(9).trim()).append(" ");
                        }
                    }
                } else {
                    // Se l'abstract è stato trovato, continua ad aggiungere righe
                    // fino a quando non si incontra una riga vuota o una nuova sezione
                    if (line.matches("(?i)^(introduction|1\\.|i\\.|references|keywords|acknowledgments|conclusion|conclusions)[:\\s].*")) {
                        break; // Termina l'estrazione dell'abstract
                    }
                    sb.append(line.trim()).append(" ");
                }
            }
        }
        // br ed fr vengono chiusi automaticamente qui grazie al try-with-resources

        // Restituisce l'abstract estratto o un messaggio di default se non viene trovato nulla
        return sb.length() > 0 ? sb.toString().trim() : "No abstract available";
    }

    // Metodo per indicizzare un singolo file passato in input
    private void indexSingleFile(File file) throws IOException {
        try {
            String title = extractTitle(file); // Estrae il titolo dal file
            String abstractText = extractAbstract(file); // Estrae l'abstract dal file

            Document doc = new Document(); // Crea un documento Lucene per l'indice
            // Aggiunge i campi del paper all'indice Lucene tramite analizzatori appropriati
            doc.add(new StringField("path", file.getAbsolutePath(), Field.Store.YES));
            doc.add(new StringField("filename", file.getName(), Field.Store.YES));
            doc.add(new TextField("title", title, Field.Store.YES));
            doc.add(new TextField("abstract", abstractText, Field.Store.YES));

            // Aggiunge il documento all'indice tramite l'IndexWriter
            this.writer.addDocument(doc);

            System.out.println("Indexed file: " + file.getName());
        } catch (IOException e){
            System.err.println("ALERT: Error indexing file " + file.getName() + "--> " + e.getMessage());
        }
    }

    public void closeWriter() throws IOException {
        this.writer.close();
    }

    public static void main(String[] args) {
        try {
            // path della directory dove salvare gli indici, se non esiste viene creata
            String indexPath = "indexes_lucene";

            // path della directory contenente i file .txt da indicizzare
            String txtFolderPath = "downloadfiles/papers_txt";
            TxtIndexer indexer = new TxtIndexer(indexPath);
            indexer.indexTxtFiles(txtFolderPath); // indicizza i file tramite la funzione apposita

            // Chiude l'IndexWriter, assicura che tutti i documenti siano stati
            // processati e scritti sull'indice
            indexer.closeWriter();

            try (DirectoryReader reader = DirectoryReader.open(FSDirectory.open(Paths.get(indexPath)))) {
                System.out.println("Total documents in index: " + reader.numDocs());
            }
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
