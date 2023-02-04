echo "starting jupyter processing."
/opt/conda/bin/jupyter nbconvert --no-input --execute --to pdf "$1" --output-dir="$2" --output="$3" 2>&1
echo "finished jupyter processing."