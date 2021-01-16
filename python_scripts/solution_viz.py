import sys
import gflags
from igraph import *
import matplotlib.pyplot as plt
import cv2

from utils import load_heuristic_sol

gflags.DEFINE_string('map_filepath', '../envs/stump_map.png', 'image representing the map')
gflags.DEFINE_string('graphml_file', '../data/real/stump_map_9_1000000_2_7.graphml', 'graphml file')
gflags.DEFINE_string('m_1', '../data/real/stump_map_9_1000000_2_7_0_m_1.txt', 'm_1 file')
gflags.DEFINE_string('V_beta', '../data/real/stump_map_9_1000000_2_7_0_V_beta.txt', 'm_1 file')
gflags.DEFINE_string('start_agents', '../data/real/stump_map_9_1000000_2_7_0_start_agents.txt', 'start_agents file')
gflags.DEFINE_string('log_file', '../logs/real/classic_milp/stump_map_9_1000000_2_7_0.log', 'log file')

if __name__ == "__main__":
    argv = gflags.FLAGS(sys.argv)

    graph = read(gflags.FLAGS.graphml_file, format='graphml')

    file_m1 = open(gflags.FLAGS.m_1, 'r')
    line = file_m1.readlines()[0]
    m_1 = list(map(lambda x: int(x) - 1, line.split()))

    file_fixed = open(gflags.FLAGS.V_beta, 'r')
    line = file_fixed.readlines()[0]
    fixed_agents = list(map(lambda x: int(x) - 1, line.split()))
    moving_robots = list(filter(lambda x: x not in fixed_agents, range(len(m_1))))

    target_agents = list(map(lambda x: m_1[x], fixed_agents))

    file_start_agents = open(gflags.FLAGS.start_agents, 'r')
    line = file_start_agents.readlines()[0]
    start_agents = list(map(lambda x: int(x) - 1, line.split()))

    obj, alloc = load_heuristic_sol(gflags.FLAGS.log_file)

    start_robots = []
    goal_robots = []
    for r in moving_robots:
        start_robots.append(m_1[r])
        goal_robots.append(alloc[r])

    im = cv2.imread(gflags.FLAGS.map_filepath)

    fig, ax = plt.subplots()

    plt.imshow(im, cmap='Greys')

    for i in start_agents:
        plt.plot([graph.vs[i]['i']], [graph.vs[i]['j']], 'bo', markersize=16)

    for i in start_robots:
        plt.plot([graph.vs[i]['i']], [graph.vs[i]['j']], 'ro', markersize=16)

    for i in target_agents:
        plt.plot([graph.vs[i]['i']], [graph.vs[i]['j']], 'b*', markersize=16)

    for i in goal_robots:
        plt.plot([graph.vs[i]['i']], [graph.vs[i]['j']], 'r*', markersize=16)

    plt.tight_layout(pad=0.0, w_pad=0.0, h_pad=0.0)

    plt.axis('off')

    fig.savefig("../envs/sol_real.png", bbox_inches='tight')
