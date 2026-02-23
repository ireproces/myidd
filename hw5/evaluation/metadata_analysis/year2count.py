import argparse
import os
import json
import csv

def published_date_to_year(published_date: str) -> str:
    if published_date:
        return published_date[:4]  # Extract year from published date
    return "Unknown"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A metadata collector for research papers that counts the number of papers published each year based on the metadata JSON files.")
    parser.add_argument("--metadata_path", type=str, required=True, help="Path to the folder containing the metadata JSON files for the research papers")
    parser.add_argument("--output", type=str, default="metadata_analysis_results.csv", help="Path to the output CSV file for the analysis results")
    args = parser.parse_args()

    year_to_count = {}

    # Load and analyze metadata
    metadata_files = [f for f in os.listdir(args.metadata_path) if f.endswith(".json") and not f.endswith("_figures.json") and not f.endswith("_paragraphs.json") and not f.endswith("_links.json") and not f.endswith("_tables.json")]
    print(f"Found {len(metadata_files)} metadata files in directory: {args.metadata_path}")
    for metadata_file in metadata_files:
        metadata_file_path = os.path.join(args.metadata_path, metadata_file)
        with open(metadata_file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            #print(f"{metadata}")
            published_date = metadata.get("published", "")
            year = published_date_to_year(published_date)
            if year not in year_to_count:
                year_to_count[year] = 0
            year_to_count[year] += 1

    # Order by year
    year_to_count = dict(sorted(year_to_count.items(), key=lambda item: item[0]))

    # Save results to CSV
    output_csv_path = args.output
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Year", "Number of Papers"])
        for year, count in sorted(year_to_count.items()):
            writer.writerow([year, count])
