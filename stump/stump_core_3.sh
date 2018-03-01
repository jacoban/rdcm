#!/bin/bash
clear

OVERALL_DEADLINE=3600 # must be in seconds
ROOT_FOLDER=../data/random_grids/
LOGS_FOLDER=../logs/random_grids/stump/new
sz_start=10
sz_step=10
sz_end=40
instance_id_start=10
instance_id_end=14
robots=7
agents=2

for sz in $(seq $sz_start 10 $sz_end)
do
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

			#instance_name=$sz"_"$comm_range"_"$agents"_"$robots"_es_"$max_dist"_"$instance_id
            instance_name=$sz"_"$comm_range"_"$agents"_"$robots"_"$instance_id
			echo $(date) "::: starting resolution of instance " $instance_name > $LOGS_FOLDER"/"$instance_name".diary"
			./timeout3 -t $OVERALL_DEADLINE matlab -nodesktop -nosplash -r "solveInstance('$ROOT_FOLDER','$LOGS_FOLDER','$instance_name'); exit"
			exit_status=$?
			if [ $exit_status = 0 ]; then
				exit_msg="(solved)"
			else
				exit_msg="(timeout)"
			fi

			echo $(date) "::: ended with status: $exit_status $exit_msg" >> $LOGS_FOLDER"/"$instance_name".diary"
			reset
		done
	fi
done