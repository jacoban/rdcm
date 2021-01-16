import sys
import gflags
import time

from utils import load_data, load_heuristic_sol, write_log, write_log_with_dash, optimal_alloc_util, is_solution_connected


gflags.DEFINE_string('data_path', '../data/example_simple/', 'data path')
gflags.DEFINE_string('log_file', '../logs/example/hungarian_allocation_log.log', 'log file')
gflags.DEFINE_string('heu_sol_file', '../logs/example/classic_milp_log.log', 'heuristic solution file')


if __name__ == "__main__":
    argv = gflags.FLAGS(sys.argv)

    graph, edges, distances, starting_pos, fixed_agents,\
    starting_pos_fixed, vertices_not_fixed, moving_robots = load_data(gflags.FLAGS.data_path)

    heuristic_obj, heuristic_alloc = load_heuristic_sol(gflags.FLAGS.heu_sol_file)

    print("Heu allocation:" + str(heuristic_alloc))
    print("Moving robots:" + str(moving_robots))
    print("Heu obj:" + str(heuristic_obj))
    print("Sum:" + str(sum(map(lambda x: distances[starting_pos[x], heuristic_alloc[x]], moving_robots))))

    if is_solution_connected(graph, map(lambda x: x+1, heuristic_alloc)):
        print("Solution is connected")
    else:
        print("Solution is not connected")

    if not(heuristic_obj < 1e+100):
        print('Algorithm cannot run since no feasible solution was provided. Exiting.')
        exit(1)

    assert(abs(heuristic_obj -
               sum(map(lambda x: distances[starting_pos[x], heuristic_alloc[x]], moving_robots))) < 1e-3)

    start = time.time()

    moving_robots_new_locs = []
    for i in range(len(heuristic_alloc)):
        if i in fixed_agents:
            pass
        else:
            moving_robots_new_locs.append(heuristic_alloc[i])

    assert(len(moving_robots) == len(moving_robots_new_locs))

    new_allocation, total_cost = optimal_alloc_util(moving_robots, moving_robots_new_locs, distances, starting_pos, fixed_agents)

    assert(total_cost <= heuristic_obj)

    if total_cost < heuristic_obj:
        print('Total cost has changed from'  + str(heuristic_obj) + ' to ' + str(total_cost))

    else:
        print('Total cost has remained unchanged at' + str(total_cost))

    print("Allocation is: " + str(new_allocation))
    write_log_with_dash(gflags.FLAGS.log_file, time.time() - start, total_cost, new_allocation, False)
