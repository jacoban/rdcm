import sys
import gflags
import os
from igraph import *
import matplotlib.pyplot as plt
import random
from copy import deepcopy
import cv2
import numpy as np

gflags.DEFINE_string('mode', 'random', 'instances to be generated (random/real)')
gflags.DEFINE_string('map_filepath', '../envs/stump_map.png', 'filepath to the image representing the map')
gflags.DEFINE_integer('size', 20, 'Random: side length of the grid. Real: grid discr. (pixels).')
gflags.DEFINE_integer('comm_range', 3, 'Comm. range. Random: manhattan distance. Map: pixels.')
gflags.DEFINE_integer('agents', 2, 'number of fixed agents')
gflags.DEFINE_integer('robots', 7, 'number of moving robots')
gflags.DEFINE_integer('experiments', 20, 'number of experiments')
gflags.DEFINE_boolean('debug', False, 'debug')
gflags.DEFINE_boolean('stump_close', True, 'generate instances that respect the closeness assumption of Stump')
gflags.DEFINE_integer('stump_dist', 3, 'maximum (manhattan) distance traveled by the agents')


def directLinePossibleBresenham(start, end, im_array):
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1

    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)

        if im_array[coord] == 0:
            return False

        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    return True


def is_grid_cell(im_array, i, j, rows, cols):
    for k in range(i, i + gflags.FLAGS.size):
        if k >= rows: return False

        for w in range(j, j + gflags.FLAGS.size):
            if w >= cols: return False

            if im_array[k][w] == 0: return False

    return True


def get_G_wp_from_graph_real(G_E, G_C):
    G = [[0 for _ in range(len(G_E.vs))] for _ in range(len(G_E.vs))]
    wp = [[0 for _ in range(len(G_E.vs))] for _ in range(len(G_E.vs))]

    sps = G_E.shortest_paths()

    # this assumes perfect symmetry
    for v1 in G_C.vs:
        for v2 in G_C.vs:
            if v1.index > v2.index:
                continue

            if v1.index == v2.index or G_C.are_connected(v1, v2):
                G[v1.index][v2.index] = 1
                G[v2.index][v1.index] = 1

            wp[v1.index][v2.index] = sps[v1.index][v2.index]
            wp[v2.index][v1.index] = sps[v1.index][v2.index]

    return G, wp, sps


def create_real_graph(map_filepath, size, comm_range, debug):
    print('Creating grid physical graph...')
    im = cv2.imread(map_filepath)
    im_array = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    rows = np.size(im_array, 0)
    cols = np.size(im_array, 1)

    G_E = Graph(directed=False)
    curr_id = 0
    bu = int(gflags.FLAGS.size / 2)
    for i in range(0, rows, gflags.FLAGS.size):
        for j in range(0, cols, gflags.FLAGS.size):
            if is_grid_cell(im_array, i, j, rows, cols):
                G_E.add_vertex()
                G_E.vs[curr_id]['y_coord'] = i + bu
                G_E.vs[curr_id]['x_coord'] = j + bu
                curr_id += 1

    neighbors = []
    for vertex_id in range(curr_id):

        curr_x = G_E.vs[vertex_id]['x_coord']
        curr_y = G_E.vs[vertex_id]['y_coord']

        up = G_E.vs.select(x_coord_eq=curr_x, y_coord_eq=(curr_y + gflags.FLAGS.size))
        if len(up):
            neighbors.append((vertex_id, up[0].index))

        right = G_E.vs.select(x_coord_eq=(curr_x + gflags.FLAGS.size), y_coord_eq=curr_y)
        if len(right):
            neighbors.append((vertex_id, right[0].index))

    G_E.add_edges(neighbors)
    print('Done. Number of vertices: ' + str(len(G_E.vs)))

    if gflags.FLAGS.debug:
        """plt.imshow(im_array)
        for edge in G_E.es:
            v1 = G_E.vs[edge.source]
            v2 = G_E.vs[edge.target]
            plt.plot([v1['x_coord'], v2['x_coord']], [v1['y_coord'], v2['y_coord']], 'b')
        pass"""

    print('Creating los communication graph...')

    G_C = Graph(directed=False)

    for vertex_id in range(len(G_E.vs)):
        G_C.add_vertex()
        G_C.vs[vertex_id]['x_coord'] = G_E.vs[vertex_id]['x_coord']
        G_C.vs[vertex_id]['y_coord'] = G_E.vs[vertex_id]['y_coord']

    neighbors = []
    range_squared = gflags.FLAGS.comm_range ** 2

    for vertex_id_1 in range(len(G_C.vs)):
        for vertex_id_2 in range(vertex_id_1 + 1, len(G_C.vs)):
            if (G_C.vs[vertex_id_1]['x_coord'] - G_C.vs[vertex_id_2]['x_coord']) ** 2 + \
                    (G_C.vs[vertex_id_1]['y_coord'] - G_C.vs[vertex_id_2]['y_coord']) ** 2 <= range_squared:

                if (directLinePossibleBresenham((G_C.vs[vertex_id_1]['y_coord'], G_C.vs[vertex_id_1]['x_coord']),
                                                (G_C.vs[vertex_id_2]['y_coord'], G_C.vs[vertex_id_2]['x_coord']),
                                                im_array)):
                    neighbors.append((vertex_id_1, vertex_id_2))

    G_C.add_edges(neighbors)

    print('Done. Number of communication edges: ' + str(len(neighbors)))

    # this is for debug plot in the main function
    for vertex_id in range(len(G_C.vs)):
        G_C.vs[vertex_id]['i'] = G_C.vs[vertex_id]['x_coord']
        G_C.vs[vertex_id]['j'] = G_C.vs[vertex_id]['y_coord']

    if gflags.FLAGS.debug:
        """plt.imshow(im_array)
        for edge in G_C.es.select(_source=0):
            v1 = G_C.vs[edge.source]
            v2 = G_C.vs[edge.target]
            plt.plot([v1['x_coord'], v2['x_coord']], [v1['y_coord'], v2['y_coord']], 'b')
        for edge in G_C.es.select(_target=0):
            v1 = G_C.vs[edge.source]
            v2 = G_C.vs[edge.target]
            plt.plot([v1['x_coord'], v2['x_coord']], [v1['y_coord'], v2['y_coord']], 'b')

        plt.show()"""
        pass

    G, wp, sps = get_G_wp_from_graph_real(G_E, G_C)

    print("Function call completed.")

    return G_C, G, wp, sps, im_array


def create_random_graph(size, comm_range, debug):
    graph = Graph(directed=False)
    curr_id = 0

    for i in range(size):
        for j in range(size):
            graph.add_vertex()
            graph.vs[curr_id]['i'] = i
            graph.vs[curr_id]['j'] = j
            curr_id += 1

    edges = []
    for v1 in graph.vs:
        for v2 in graph.vs:
            if v2.index <= v1.index:
                continue

            i_1 = v1['i']
            j_1 = v1['j']

            i_2 = v2['i']
            j_2 = v2['j']

            if abs(i_1 - i_2) <= comm_range and abs(j_1 - j_2) <= comm_range:
                edges.append((v1.index, v2.index))

    graph.add_edges(edges)

    if debug:
        """for v1 in graph.vs:
            plt.plot([v1['i']], [v1['j']], 'bo')

        for v1 in graph.vs:
            if graph.are_connected(graph.vs[25].index, v1.index):
                plt.plot([graph.vs[25]['i'], v1['i']], [graph.vs[25]['j'], v1['j']], 'r')

        plt.show()"""
        pass

    return graph


def get_G_wp_from_graph_random(graph, size):
    G = [[0 for _ in range(size*size)] for _ in range(size*size)]
    wp = [[0 for _ in range(size*size)] for _ in range(size*size)]

    # this assumes perfect symmetry
    for v1 in graph.vs:
        for v2 in graph.vs:
            if v1.index > v2.index:
                continue

            if v1.index == v2.index or graph.are_connected(v1, v2):
                G[v1.index][v2.index] = 1
                G[v2.index][v1.index] = 1

            wp[v1.index][v2.index] = int(abs(v1['i'] - v2['i']) + abs(v1['j'] - v2['j']))
            wp[v2.index][v1.index] = wp[v1.index][v2.index]

    return G, wp


def write_matrix_to_file(matrix, size, path):
    s = ""

    for i in range(size):
        for j in range(size):
            s += str(matrix[i][j]) + '\t'

        s += '\n'

    f = open(path, 'w')
    f.write(s)
    f.close()


def write_list_to_file(l, path):
    s = ""

    for el in l:
        s += str(el) + '\t'

    f = open(path, 'w')
    f.write(s)
    f.close()


def get_deployment_close(graph, start_agents, moving_robots, start_v_rob, sps=None):
    while True:
        pos_agents = {}
        vertices_agents = []

        for a in start_agents.keys():
            v_a = start_agents[a]

            i_a = graph.vs[v_a]['i']
            j_a = graph.vs[v_a]['j']

            if sps is None:
                candidates = list(filter(lambda x: abs(graph.vs[x]['i'] - i_a) <= gflags.FLAGS.stump_dist and abs(graph.vs[x]['j'] - j_a) <=
                                              gflags.FLAGS.stump_dist and x not in start_v_rob, range(len(graph.vs))))

            else:
                candidates = list(filter(lambda x: sps[v_a][x] <= gflags.FLAGS.stump_dist and x not in start_v_rob, range(len(graph.vs))))

            new_v = random.choice(candidates)
            pos_agents[a] = new_v
            vertices_agents.append(new_v)

        if graph.subgraph(vertices_agents).is_connected():
            continue
        else:
            break

    return pos_agents, vertices_agents


def get_deployment(graph, fixed_agents, moving_robots, mode='random', start_v_rob=[]):

    pos_agents = {}
    pos_robots = {}
    entities = fixed_agents + moving_robots
    pos_entities = {}

    if mode == 'random':

        while True:
            vertices_agents = random.sample(list(filter(lambda x: x not in start_v_rob, range(len(graph.vs)))), len(fixed_agents))

            if graph.subgraph(vertices_agents).is_connected():
                continue

            vertices_robots = random.sample(list(filter(lambda x: x not in vertices_agents, range(len(graph.vs)))),
                                        len(moving_robots))

            all_vertices = vertices_agents + vertices_robots

            if graph.subgraph(all_vertices).is_connected():
                break

    elif mode == 'lined':
        vertices_agents = deepcopy(fixed_agents)
        vertices_robots = deepcopy(moving_robots)

    else:
        print("Mode not recognized!")
        exit(1)

    for i in range(len(fixed_agents)):
        pos_agents[fixed_agents[i]] = vertices_agents[i]
        pos_entities[fixed_agents[i]] = vertices_agents[i]

    for i in range(len(moving_robots)):
        pos_robots[moving_robots[i]] = vertices_robots[i]
        pos_entities[moving_robots[i]] = vertices_robots[i]

    graphD = Graph(directed=False)
    matrixD = [[0 for _ in entities] for _ in entities]

    for i in range(len(entities)):
        graphD.add_vertex()

    edgesD = []

    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            if graph.are_connected(pos_entities[i], pos_entities[j]):
                edgesD.append((i, j))

    graphD.add_edges(edgesD)

    spanning_tree = graphD.spanning_tree()

    for v1 in spanning_tree.vs:
        for v2 in spanning_tree.vs:
            if spanning_tree.are_connected(v1.index, v2.index):
                matrixD[v1.index][v2.index] = 1

    assert(len(spanning_tree.vs) - 1 == len(spanning_tree.es))

    return matrixD, pos_agents, pos_robots, vertices_agents, vertices_robots


def run_main():
    random.seed(1)

    argv = gflags.FLAGS(sys.argv)

    if gflags.FLAGS.mode == 'random':

        if not os.path.exists('../data/random_grids'):
            os.makedirs('../data/random_grids')

        graph = create_random_graph(gflags.FLAGS.size, gflags.FLAGS.comm_range, gflags.FLAGS.debug)

        base_path = '../data/random_grids/' + str(gflags.FLAGS.size) + '_' + str(gflags.FLAGS.comm_range) + \
                    '_' + str(gflags.FLAGS.agents) + '_' + str(gflags.FLAGS.robots)

        if gflags.FLAGS.stump_close:
            base_path += '_es_' + str(gflags.FLAGS.stump_dist)

        G, wp = get_G_wp_from_graph_random(graph, gflags.FLAGS.size)

    elif gflags.FLAGS.mode == 'real':

        gflags.FLAGS.stump_close = True

        if gflags.FLAGS.map_filepath.endswith('.png'):
            map_name = gflags.FLAGS.map_filepath.split('/')[-1]
            map_name = map_name[:-4]

        else:
            print("Only png files are supported. Exiting.")
            exit(1)

        if not os.path.exists('../data/random_grids'):
            os.makedirs('../data/random_grids')

        base_path = '../data/real/' + map_name + '_' + str(gflags.FLAGS.size) + '_' + str(gflags.FLAGS.comm_range) + \
                    '_' + str(gflags.FLAGS.agents) + '_' + str(gflags.FLAGS.robots)

        graph, G, wp, sps, im_array = create_real_graph(gflags.FLAGS.map_filepath, gflags.FLAGS.size, gflags.FLAGS.comm_range,
                                                   gflags.FLAGS.debug)

        print("Ready for generating experiments.")

    else:
        print("Mode not recognized. Exiting.")
        exit(1)

    graph.write(base_path + '.graphml', format='graphml')

    fixed_agents = list(range(0, gflags.FLAGS.agents))
    moving_robots = list(range(gflags.FLAGS.agents, gflags.FLAGS.agents + gflags.FLAGS.robots))

    for n in range(gflags.FLAGS.experiments):
        print("Experiment " + str(n))
        write_matrix_to_file(G, len(graph.vs), base_path + '_' + str(n) + '_G.txt')
        write_matrix_to_file(wp, len(graph.vs), base_path + '_' + str(n) + '_w_p.txt')

        write_list_to_file(list(map(lambda x: x + 1, fixed_agents)), base_path + '_' + str(n) + '_V_beta.txt')

        if not gflags.FLAGS.stump_close:
            D, start_agents, start_robots, start_v_ag, start_v_rob = get_deployment(graph, fixed_agents, moving_robots,
                                                                                    'lined')
        else:
            D, start_agents, start_robots, start_v_ag, start_v_rob = get_deployment(graph, fixed_agents, moving_robots,
                                                                                    'random')

        write_matrix_to_file(D, len(fixed_agents + moving_robots), base_path + '_' + str(n) + '_D.txt')

        success = False
        while not success:
            if not gflags.FLAGS.stump_close:
                Ddummy, final_agents, dummy_robots, final_v_a, dummy_v_rob = get_deployment(graph, fixed_agents,
                                                                                            moving_robots, mode='random',
                                                                                            start_v_rob=start_v_rob)
            else:
                if gflags.FLAGS.mode == 'random':
                    final_agents, final_v_a = get_deployment_close(graph, start_agents, moving_robots, start_v_rob)

                else:
                    final_agents, final_v_a = get_deployment_close(graph, start_agents, moving_robots, start_v_rob, sps)

            if not graph.subgraph(final_v_a + start_v_rob).is_connected():
                success = True

        m1_list = []
        for a in fixed_agents:
            m1_list.append(final_agents[a] + 1)

        for r in moving_robots:
            m1_list.append(start_robots[r] + 1)

        write_list_to_file(m1_list, base_path + '_' + str(n) + '_m_1.txt')

        if gflags.FLAGS.mode == 'real':
            start_agents_list = []
            for a in fixed_agents:
                start_agents_list.append(start_agents[a] + 1)
                write_list_to_file(start_agents_list, base_path + '_' + str(n) + '_start_agents.txt')

        if gflags.FLAGS.debug:

            if gflags.FLAGS.mode == 'real':
                plt.imshow(im_array)
            
            for v1 in graph.vs:
                plt.plot([v1['i']], [v1['j']], 'wo')

            for i in start_v_ag:
                plt.plot([graph.vs[i]['i']], [graph.vs[i]['j']], 'bo')

            for i in final_v_a:
                plt.plot([graph.vs[i]['i']], [graph.vs[i]['j']], 'ro')

            for i in start_v_rob:
                plt.plot([graph.vs[i]['i']], [graph.vs[i]['j']], 'go')

            for i in range(len(D)):
                if i in fixed_agents:
                    v_i = start_agents[i]
                else:
                    v_i = start_robots[i]

                # for j in range(i + 1, len(D)):
                #    if j in fixed_agents:
                #        v_j = start_agents[j]
                #    else:
                #        v_j = start_robots[j]

                #    if D[i][j] == 1:
                #        plt.plot([graph.vs[v_i]['i'], graph.vs[v_j]['i']],
                #                 [graph.vs[v_i]['j'], graph.vs[v_j]['j']], 'm')

            # for v1 in graph.vs:
            #    if graph.are_connected(graph.vs[711].index, v1.index):
            #        plt.plot([graph.vs[711]['i'], v1['i']], [graph.vs[711]['j'], v1['j']], 'k')


            plt.axis('off')
            if gflags.FLAGS.mode != 'real': 
                plt.xlim(-1, gflags.FLAGS.size + 1)
                plt.ylim(-1, gflags.FLAGS.size + 1)
            plt.tight_layout(pad=0.0, w_pad=0.0, h_pad=0.0)
            plt.show()

            pass


if __name__ == "__main__":
    run_main()