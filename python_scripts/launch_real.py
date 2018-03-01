import os

for i in range(20):
    base_path = "stump_map_9_999999_2_7_" + str(i)
    command = "python classic_milp.py --data_path=../data/real/" + base_path + "_ " +\
              "--log_file=../logs/real/classic_milp/" + base_path + ".log --heu_sol_file=null --threads=0 --time_limit=3600"
    #print command
    os.system(command)