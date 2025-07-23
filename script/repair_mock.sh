date "+%Y-%m-%d %H:%M:%S"

for i in 1 2; do
  echo "Running repair sample $i in MOCK mode..."
  python agentless/repair/repair.py \
    --output_folder results/$FOLDER_NAME/repair_sample_$i \
    --num_threads $NJ \
    --dataset $DATASET \
    --split $SPLIT \
    ${TARGET_ID:+--target_id $TARGET_ID} \
    --skip_existing \
    --mock
done 