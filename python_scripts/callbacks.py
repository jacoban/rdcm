from gurobipy import *

def lazy_connection(model):
    vertices = model._vertices
    Y = model._Y
    graph = model._graph
    working_graph_c = model._working_graph.copy()

    allocation_vertices = list(filter(lambda x: model.cbGetSolution(Y[x]) > 0.5, vertices))

    working_edges = []
    for i in allocation_vertices:
        for j in allocation_vertices:
            if j <= i:
                pass
            else:
                if graph.are_connected(i, j):
                    working_edges.append((i, j))

    working_graph_c.add_edges(working_edges)

    components = working_graph_c.components()
    allocation_vertices_set = set(allocation_vertices)
    components = list(filter(lambda x: len(set(x).intersection(allocation_vertices_set)) > 0, components))

    if len(components) == 1:
        return True, allocation_vertices

    for c_i in range(len(components)):
        component_i = components[c_i]
        component_A_i_raw = graph.neighborhood(vertices=component_i, order=1)

        flattened_list_A_i = [y for x in component_A_i_raw for y in x]
        component_A_i = set(list(filter(lambda x: x not in component_i, flattened_list_A_i)))

        component_and_neighs = component_A_i_raw
        component_and_neighs.append(component_i)

        flattened_list_c_n = [y for x in component_and_neighs for y in x]

        component_and_neighs = set(flattened_list_c_n)  # removes duplicates

        edges_to_remove = []
        for u in component_and_neighs:
            for v in component_and_neighs:
                if v <= u:
                    pass
                else:
                    if graph.are_connected(u, v):
                        edges_to_remove.append((u, v))

        graph_without_component_i = graph.copy()
        graph_without_component_i.delete_edges(edges_to_remove)

        for c_j in range(len(components)):
            if c_i == c_j:
                continue

            component_j = components[c_j]
            R_j = set(graph_without_component_i.subcomponent(component_j[0]))
            separator = component_A_i.intersection(R_j)

            expr = 0.0
            for n in separator:
                expr += Y[n]

            for i in component_i:
                for j in component_j:
                    model.cbLazy(expr >= Y[i] + Y[j] - 1)

    return False, allocation_vertices

