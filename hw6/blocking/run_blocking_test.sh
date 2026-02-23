python3 blocking1.py ../dataset/train_valid_test/test.csv -o ../dataset/train_valid_test/blocked1_test.csv -e ../dataset/train_valid_test/excluded1_test.csv
python3 blocking2.py ../dataset/train_valid_test/test.csv -o ../dataset/train_valid_test/blocked2_test.csv -e ../dataset/train_valid_test/excluded2_test.csv
python3 ../dataset/clean_pairs.py -i ../dataset/train_valid_test/blocked1_test.csv -o ../dataset/train_valid_test/blocked1_test.csv
python3 ../dataset/clean_pairs.py -i ../dataset/train_valid_test/blocked2_test.csv -o ../dataset/train_valid_test/blocked2_test.csv