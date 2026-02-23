python3 blocking1.py ../dataset/shuffled_pairs.csv -o ../dataset/blocked1_shuffled_pairs.csv -e ../dataset/excluded1_shuffled_pairs.csv
python3 blocking2.py ../dataset/shuffled_pairs.csv -o ../dataset/blocked2_shuffled_pairs.csv -e ../dataset/excluded2_shuffled_pairs.csv
python3 ../dataset/clean_pairs.py -i ../dataset/blocked1_shuffled_pairs.csv -o ../dataset/blocked1_shuffled_pairs.csv
python3 ../dataset/clean_pairs.py -i ../dataset/blocked2_shuffled_pairs.csv -o ../dataset/blocked2_shuffled_pairs.csv