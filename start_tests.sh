dataset_names=("simple" "ion" "credit" "ovarian")
lsvm_types=(1 2 3 4 5)

for dataset_name in ${dataset_names[@]}; do
  for lsvm_type in ${lsvm_types[@]}; do
    lsvm_type_name="none"
    if [[ lsvm_type -eq 1 ]]; then
      lsvm_type_name="pyfhel"
    elif [[ lsvm_type -eq 2 ]];then
      lsvm_type_name="palisade"
    elif  [[ lsvm_type -eq 3 ]];then
      lsvm_type_name="plain"
    elif  [[ lsvm_type -eq 4 ]];then
      lsvm_type_name="pyseal"
    elif  [[ lsvm_type -eq 5 ]];then
      lsvm_type_name="pyseal_batch"
    fi

    echo $lsvm_type $lsvm_type_name $dataset_name
    watch -n 1 "ps -aux | grep 'perf_test.py' | grep -v ps | grep -v grep | tr -s ' ' | cut -d' ' -f3-4 | tee -a ~/test_output/${lsvm_type_name}_${dataset_name}_usage.txt"&
    python3 python/perf_test.py $dataset_name $lsvm_type > ~/test_output/${lsvm_type_name}_${dataset_name}.txt
    killall watch
    sleep 1
  done
done