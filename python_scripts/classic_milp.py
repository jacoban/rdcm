import sys
import gflags
from igraph import *
from gurobipy import *

from utils import load_data, load_heuristic_sol, write_log, is_solution_connected
from callbacks import lazy_connection

gflags.DEFINE_string('data_path', '../data/example_simple/', 'data path')
gflags.DEFINE_string('log_file', '../logs/example/classic_milp_log.log', 'log file')
gflags.DEFINE_string('heu_sol_file', '../logs/example/hungarian_allocation_log.log', 'heuristic solution file')
gflags.DEFINE_integer('time_limit', 1800, 'milp deadline')
gflags.DEFINE_integer('threads', 0, 'number of threads used by GUROBI')


def callback(model, where):
    if where == GRB.callback.MIPSOL:
        lazy_connection(model)


def add_variables(m, Y, Z, graph, vertices_not_fixed, moving_robots, distances, starting_pos, heuristic_obj=float('inf')):
    n_vertices = len(graph.vs)

    for v in range(n_vertices):
        Y[v] = m.addVar(vtype=GRB.BINARY, name="y[%d]" % v)

    for v in vertices_not_fixed:
        for r in moving_robots:
            if distances[starting_pos[r], v] <= heuristic_obj:
                Z[r, v] = m.addVar(vtype=GRB.CONTINUOUS, lb=0.0, obj=distances[starting_pos[r], v])


def set_initial_solution(Y, Z, heuristic_alloc, moving_robots):
    for v in Y.keys():
        Y[v].start = 0.0

    for (r, v) in Z.keys():
        Z[r, v].start = 0.0

    for v in heuristic_alloc:
        Y[v].start = 1.0

    for r in moving_robots:
        Z[r, heuristic_alloc[r]].start = 1.0


def add_constraints(m, Y, Z, graph, moving_robots, vertices_not_fixed, starting_pos_fixed, distances, starting_pos,
                    heuristic_obj=float('inf')):

    # each robot in 1 vertex
    for r in moving_robots:
        m.addConstr(quicksum(Z[r, v] for v in filter(lambda x: distances[starting_pos[r], x] <= heuristic_obj,
                                                     vertices_not_fixed)) == 1)

    # if non-occupied vertex in solution, a single robot must occupy it
    for v in vertices_not_fixed:
        m.addConstr(quicksum(Z[r, v] for r in filter(lambda x: distances[starting_pos[x], v] <= heuristic_obj,
                                                     moving_robots)) == Y[v])

    # set to 1 all vertices occupied by fixed agents
    for v in starting_pos_fixed:
        m.addConstr(Y[v] == 1)

    # helpful inequalities
    for v in range(len(graph.vs)):
        m.addConstr(quicksum(Y[u] for u in graph.neighbors(v)) >= Y[v])


def run_main():
    argv = gflags.FLAGS(sys.argv)

    graph, edges, distances, starting_pos, fixed_agents,\
    starting_pos_fixed, vertices_not_fixed, moving_robots = load_data(gflags.FLAGS.data_path)

    heuristic_obj, heuristic_alloc = load_heuristic_sol(gflags.FLAGS.heu_sol_file)

    m = Model('rdcm')
    m.setParam('OutputFlag', True)
    m.setParam('TimeLimit', gflags.FLAGS.time_limit)
    m.setParam('Threads', gflags.FLAGS.threads)
    m.params.LazyConstraints = 1

    Y = {}
    Z = {}

    add_variables(m, Y, Z, graph, vertices_not_fixed, moving_robots, distances, starting_pos, heuristic_obj)

    m.update()

    if heuristic_obj < float('inf'):
        heuristic_alloc_set = set(heuristic_alloc)
        if len(heuristic_alloc_set) == len(heuristic_alloc):
            # means that all the vertices are different
            set_initial_solution(Y, Z, heuristic_alloc, moving_robots)

    m._Y = Y
    m._graph = graph
    m._vertices = range(len(graph.vs))

    # avoids to always rebuild the vertices set
    working_graph = Graph(directed=False)
    for i in range(len(graph.vs)):
        working_graph.add_vertex()
    m._working_graph = working_graph

    m.update()

    add_constraints(m, Y, Z, graph, moving_robots, vertices_not_fixed, starting_pos_fixed, distances, starting_pos,
                    heuristic_obj)

    m.modelSense = GRB.MINIMIZE
    m.update()

    m.optimize(callback)

    runtime = m.getAttr('Runtime')
    print("Runtime is: ", runtime)

    if m.status == GRB.status.INF_OR_UNBD:
        print('Error during optimization (model inf or unbd).')

    elif m.status == GRB.status.INFEASIBLE:
        print('Error during optimization (model infeasible).')

    elif m.status == GRB.status.INTERRUPTED:
        print('Interrupted.')

    elif m.status == GRB.status.OPTIMAL or m.status == GRB.TIME_LIMIT:
        obj = m.getAttr("ObjVal")
        print("Obj is: ", obj)

        gap = m.getAttr("MIPGap")
        print("MIP gap is: ", gap)

        allocation = []

        fractional = False

        if gap < 1e+100:

            z = m.getAttr('x', Z)

            allocation = [None for _ in range(len(starting_pos))]
            for a in fixed_agents:
                allocation[a] = starting_pos[a] + 1

            for v in vertices_not_fixed:
                for r in filter(lambda x: distances[starting_pos[x], v] <= heuristic_obj, moving_robots):
                    if z[r, v] > 0.0001 and z[r, v] < 0.9999:
                        fractional = True
                        break

                    if z[r, v] > 0.5:
                        allocation[r] = v + 1

                if fractional:
                    break

            if not fractional:
                print("Allocation is: ", allocation)
                assert(is_solution_connected(graph, allocation))

        write_log(gflags.FLAGS.log_file, runtime, obj, allocation, fractional, gap)


if __name__ == "__main__":
    run_main()
