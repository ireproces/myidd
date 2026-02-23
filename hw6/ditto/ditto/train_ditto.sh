OUTPUT_PATH="data/used_cars_vehicles/"
date
python3.9 train_ditto.py \
  --task used_cars_vehicles \
  --batch_size 32 \
  --run_id 1 \
  --max_len 64 \
  --logdir ${OUTPUT_PATH}log \
  --save_model \
  --lm roberta \
  --lr 1.5e-5 \
  --n_epochs 5 \
  --device cuda \

date