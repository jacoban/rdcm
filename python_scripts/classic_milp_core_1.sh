#!/bin/bash
clear

ROOT_FOLDER=../data/random_grids/
LOGS_FOLDER=../logs/random_grids/classic_milp/new/
HEUSOL_FOLDER=../logs/random_grids/hungarian/
sz_start=10
sz_step=10
sz_end=40
instance_id_start=0
instance_id_end=19
robots=7
agents=2

for sz in $(seq $sz_start 10 $sz_end)
do
	# size -> comm_range mapping
	if [ $sz = 10 ]; then
		comm_range=2
		max_dist=2
	elif [ $sz = 20 ]; then
		comm_range=3
		max_dist=3
	elif [ $sz = 30 ]; then
		comm_range=5
		max_dist=5
	elif [ $sz = 40 ]; then
		comm_range=7
		max_dist=7
	else
		echo "Cannot determine comm range for size $sz"
		comm_range=0
	fi

	if [[ $comm_range > 0 ]]; then
		for instance_id in $(seq $instance_id_start $instance_id_end)
		do
			instance_name=$sz"_"$comm_range"_"$agents"_"$robots"_"$instance_id
			#instance_name=$sz"_"$comm_range"_"$agents"_"$robots"_es_"$max_dist"_"$instance_id
			python classic_milp.py --data_path=$ROOT_FOLDER$instance_name"_" --log_file=$LOGS_FOLDER$instance_name.log --heu_sol_file=$HEUSOL_FOLDER$instance_name.log --threads=0 --time_limit=3600
		done
	fi
done
