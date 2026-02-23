python3 align_schema.py
python3 match_table.py -o match_table.csv a_used_cars_data.csv a_vehicles.csv
python3 make_pairs.py -o pairs.csv match_table.csv a_used_cars_data.csv a_vehicles.csv
python3 clean_pairs.py pairs.csv pairs.csv
python3 shuffle_csv.py pairs.csv shuffled_pairs.csv
python3 train_valid_test_splitter.py shuffled_pairs.csv ./train_valid_test/
python3 clean_pairs.py -i ./train_valid_test/train.csv ./train_valid_test/train.csv
python3 clean_pairs.py ./train_valid_test/valid.csv ./train_valid_test/valid.csv
python3 clean_pairs.py ./train_valid_test/test.csv ./train_valid_test/test.csv