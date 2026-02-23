OUTPUT_PATH="data/used_cars_vehicles/log"
date
python3.9 matcher.py \
  --task used_cars_vehicles \
  --input_path input/input.jsonl \
  --output_path output/output.jsonl \
  --lm roberta \
  --max_len 64 \
  --use_gpu \
  --checkpoint_path ${OUTPUT_PATH}
date