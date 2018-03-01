#!/bin/bash

#source ../../../config_global.cfg
#source ./config_local.cfg

#################### START EDIT HERE #####################################################
# core where this is meant to run
#CORE=1
# instances root directory
#INSTANCES_DIR=instances_selected
# instances sub directory (where the mat file are)
#GROUP_NAME=instances_edge_density_25_ntargets_10
#################### STOP EDIT HERE #####################################################

OVERALL_DEADLINE=10
ROOT_FOLDER=../data/random_grids/
INSTANCE=5_2_0

./timeout3 -t $OVERALL_DEADLINE matlab -nodesktop -nosplash -r "solveInstance('$ROOT_FOLDER','$INSTANCE'); exit"

#./timeout3 -t $OVERALL_DEADLINE matlab -nodesktop -nosplash -r "disp('Hello'); exit;"

# the dir name where the results will be stored
#RESULT_DIR_TAG=${GROUP_NAME}"_"${RESULTS_DIR_POSTFIX}

#for f in "$BASE_DIR/$INSTANCES_DIR/$GROUP_NAME"/*.mat
#do
#	../../../timeout3 -t $OVERALL_DEADLINE matlab -nodesktop -nosplash -r "addpath('$BASE_DIR/git/secgames/missed_detections/'); addpath('$BASE_DIR/git/secgames/missed_detections/bgl_graph_functions/'); runInstance('$BASE_DIR', '${INSTANCES_DIR}', '${GROUP_NAME}', '${f##*/}', '${RESULT_DIR_TAG}', ${ALPHA_VAL}, ${ORACLE_DEADLINE}, ${SRO_APX}, ${USE_CCO}, ${USE_RO}); exit;"

#done

#matlab -nodesktop -nosplash -r "addpath('$BASE_DIR/git/secgames/missed_detections/'); sendTextByMail('Tests $RESULT_DIR_TAG on core  $CORE  completed'); exit;"

echo "Status: $?" > last_status

reset


#reset


