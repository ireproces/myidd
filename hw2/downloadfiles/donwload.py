from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from lxml import html


# Imposta il driver Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Apre la pagina desiderata
url="https://arxiv.org/search/cs?query=Machine+Learning&searchtype=all&abstracts=show&order=-announced_date_first&size=50"
driver.get(url)

# Scorre fino in fondo alla pagina per caricare tutti i contenuti
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Salva l'HTML completo in un file
html_content = driver.page_source
with open("arxiv_page.html", "w", encoding="utf-8") as f:
    f.write(html_content)

driver.quit()

# Carica il file HTML
with open("arxiv_page.html", "r", encoding="utf-8") as f:
    content = f.read()

tree = html.fromstring(content)

# Imposta la cartella di destinazione nella quale salvare i file di testo
output_dir = "papers_txt"
os.makedirs(output_dir, exist_ok=True)

# Trova tutti i paper tramite XPath
papers = tree.xpath('//li[contains(@class,"arxiv-result")]')

for i, paper in enumerate(papers, 1):
    
    # Estrae il titolo
    title = paper.xpath('.//p[contains(@class,"title")]/text()')
    title = "".join([t.strip() for t in title]).strip()

    # Estrae l'abstract completo
    abstract = paper.xpath('.//span[contains(@class,"abstract-full")]/text() | .//span[contains(@class,"abstract-full")]//text()')
    abstract = "".join([a.strip() for a in abstract if a.strip()]).strip()
    
    # Crea un nome file sicuro
    safe_title = title.replace(" ", "_").replace("/", "_")[:50]
    filename = f"{i:03d}_{safe_title}.txt"
    
    # Salva su file testuale nel formato desiderato
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n\n")
        f.write(f"Abstract: {abstract}\n")

# print(f"Salvati {len(papers)} paper in '{output_dir}'")