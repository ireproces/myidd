#load the CSV and graph the distribution of publication years using matplotlib
import csv
import matplotlib.pyplot as plt



if __name__ == "__main__":
    file1 = "arxiv_all_year2amount.csv"
    file2 = "arxiv_html_year2amount.csv"
    year_to_count1 = {}
    year_to_count2 = {}
    with open(file1, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            year = int(row[0])
            count = int(row[1])
            year_to_count1[year] = count
    with open(file2, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            year = int(row[0])
            count = int(row[1])
            year_to_count2[year] = count
    
    plot = plt.figure(figsize=(10, 5))
    plt.plot(list(year_to_count1.keys()), list(year_to_count1.values()), label="All Papers", marker='o')
    plt.plot(list(year_to_count2.keys()), list(year_to_count2.values()), label="Papers with HTML content", marker='o')
    plt.xlabel("Year")
    plt.ylabel("Number of Papers")
    plt.title("Distribution of Publication Years for ArXiv Papers")
    plt.legend()
    plt.grid()
    plt.savefig("arxiv_publication_year_distribution.png")
    plt.show()
   


    