from igraph import *
import numpy as np
import os.path
from munkres import Munkres
import random


def is_solution_connected(graph, allocation):
    subgraph = graph.subgraph(list(map(lambda x: x - 1, allocation)))
    return subgraph.is_connected()


def write_log(log_file, runtime, obj, allocation, fractional, gap=None):
    log_file = open(log_file, 'w')
    log_file.write('Runtime=' + str(runtime) + '\n')
    log_file.write('Objval=' + str(obj) + '\n')
    log_file.write('Allocation=' + str(allocation) + '\n')
    log_file.write('Fractional=' + str(fractional) + '\n')
    if gap is not None:
        log_file.write('Gap=' + str(gap) + '\n')
    log_file.close()


def write_log_with_dash(log_file, runtime, obj, allocation, fractional, gap=None):
    log_file = open(log_file, 'w')
    log_file.write('---\n')
    log_file.write('Runtime=' + str(runtime) + '\n')
    log_file.write('Objval=' + str(obj) + '\n')
    log_file.write('Allocation=' + str(allocation) + '\n')
    log_file.write('Fractional=' + str(fractional) + '\n')
    if gap is not None:
        log_file.write('Gap=' + str(gap) + '\n')
    log_file.write('---\n')
    log_file.close()


def load_data(data_path):
    random.seed(0)
    file_g = open(data_path + 'G.txt', 'r')
    lines = file_g.readlines()
    s = ""
    for line in lines:
        linet = line.replace("\t", " ").replace("\n", "").replace("\r", "")
        linet = linet[:len(linet) - 1]
        s += linet + ";"
    s = s[:len(s) - 1]
    file_g.close()

    graph_matrix = np.matrix(s)
    graph = Graph(directed=False)
    edges = []
    for i in range(graph_matrix.shape[0]):
        graph.add_vertex()
        for j in range(i+1, graph_matrix.shape[0]):
            if graph_matrix[i, j] == 1:
                edges.append((i, j))

    graph.add_edges(edges)

    file_distances = open(data_path + 'w_p.txt', 'r')
    lines = file_distances.readlines()
    s = ""
    for line in lines:
        linet = line.replace("\t", " ").replace("\n", "").replace("\r", "")
        linet = linet[:len(linet) - 1]
        s += linet + ";"
    s = s[:len(s) - 1]
    file_distances.close()

    distances = np.matrix(s)
    # np.ones((graph_matrix.shape[0], graph_matrix.shape[0]))
    # print distances
    # for i in xrange(graph_matrix.shape[0]):
    #    distances[i, i] = 0

    file_starting = open(data_path + 'm_1.txt', 'r')
    line = file_starting.readlines()[0]
    starting_pos = list(map(lambda x: int(x) - 1, line.split()))

    file_fixed = open(data_path + 'V_beta.txt', 'r')
    line = file_fixed.readlines()[0]
    fixed_agents = list(map(lambda x: int(x) - 1, line.split()))

    starting_pos_fixed = list(map(lambda x: starting_pos[x], fixed_agents))
    vertices_not_fixed = list(filter(lambda x: x not in starting_pos_fixed, range(len(graph.vs))))
    moving_robots = list(filter(lambda x: x not in fixed_agents, range(len(starting_pos))))

    return graph, edges, distances, starting_pos, fixed_agents,\
           starting_pos_fixed, vertices_not_fixed, moving_robots


def load_heuristic_sol(file_path):
    heuristic_obj = float('inf')
    allocation = []

    if not(os.path.exists(file_path)) or file_path == 'null':
        return heuristic_obj, allocation

    f = open(file_path, 'r')
    lines = f.readlines()
    for line in lines:
        if 'Objval' in line:
            s = line.split('=')
            heuristic_obj = int(float(s[1]))

        elif 'Allocation' in line:
            s = line.split('=')
            allocation = eval(s[1])
            allocation = list(map(lambda x: x - 1, allocation))

    return heuristic_obj, allocation


def optimal_alloc_util(moving_robots, moving_robots_new_locs, distances, starting_pos, fixed_agents):
    cost_matrix = []

    for r_index in range(len(moving_robots)):
        cost_matrix.append([])
        for l_index in range(len(moving_robots_new_locs)):
            cost_matrix[-1].append(distances[starting_pos[moving_robots[r_index]], moving_robots_new_locs[l_index]])

    m = Munkres()
    indexes = m.compute(cost_matrix)

    total_cost = 0

    new_allocation = [None for _ in range(len(starting_pos))]
    for a in fixed_agents:
        new_allocation[a] = starting_pos[a] + 1

    for r_index, l_index in indexes:
        total_cost += cost_matrix[r_index][l_index]
        new_allocation[moving_robots[r_index]] = moving_robots_new_locs[l_index] + 1

    return new_allocation, total_cost
