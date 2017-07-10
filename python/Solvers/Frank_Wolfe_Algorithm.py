import igraph
import numpy as np
from All_or_Nothing_Function import all_or_nothing, all_or_nothing_beats

def Frank_Wolfe_Solver(traffic_scenario, cost_function,past=10, max_iter=1000, eps=1e-8, \
    q=50, display=1, stop=1e-2):
    '''
    This is an adaptation of Fukushima's modification of the Frank_Wolfe algorithm
    :param traffic_scenario: traffic model object with all info regarding the traffic scenario to be solved
    :param F_function: Function_F object with evaluate cost function method for traffic model
    past:     search direction is the mean over the last 'past' directions
    max_iter: maximum number of iterations
    esp:      used as a stopping criterium if some quantities are too close to 0
    q:        first 'q' iterations uses open loop step sizes 2/(i+2)
    display:  controls the display of information in the terminal
    :return: Flow on links in Equilibrium state
    '''
    assert past <= q, "'q' must be bigger or equal to 'past'"

    #Construct igraph object
    graph_object = construct_igraph(traffic_scenario, cost_function)
    #Constructing a dictionary for demand: origin: ([destination],[demand])
    #od = construct_od(traffic_scenario.beats_api.get_od_info())
    od = traffic_scenario.beats_api.get_od_info()

    f = np.zeros(traffic_scenario.beats_api.get_num_links(), dtype="float64")  # initial flow assignment is null
    fs = np.zeros((traffic_scenario.beats_api.get_num_links(), past), dtype="float64")  # to keep track of the past q
                                                                                        # assignments
    K = total_free_flow_cost(graph_object, od)

    # why this?
    if K < eps:
        K = np.sum(traffic_scenario.get_demand_values())
    elif display >= 1:
        print 'average free-flow travel time', K / traffic_scenario.get_total_demand()

    #import pdb; pdb.set_trace()
    for i in range(max_iter):

        if display >= 1:
            if i <= 1:
                print 'iteration: {}'.format(i+1)
            else:
                print 'iteration: {}, error: {}'.format(i+1, error)

        # construct weighted graph with latest flow assignment
        L, grad = search_direction(f, cost_function, graph_object, od)

        fs[:,i%past] = L
        w = L - f
        if i >= 1:
            error = -grad.dot(w) / K
            # if error < stop and error > 0.0:
            if error < stop:
                if display >= 1: print 'stop with error: {}'.format(error)
                return f
        if i > q:
            # step 3 of Fukushima
            v = np.sum(fs,axis=1) / min(past,i+1) - f
            norm_v = np.linalg.norm(v,1)
            if norm_v < eps:
                if display >= 1: print 'stop with norm_v: {}'.format(norm_v)
                return f
            norm_w = np.linalg.norm(w,1)
            if norm_w < eps:
                if display >= 1: print 'stop with norm_w: {}'.format(norm_w)
                return f
            # step 4 of Fukushima
            gamma_1 = grad.dot(v) / norm_v
            gamma_2 = grad.dot(w) / norm_w
            if gamma_2 > -eps:
                if display >= 1: print 'stop with gamma_2: {}'.format(gamma_2)
                return f
            d = v if gamma_1 < gamma_2 else w
            # step 5 of Fukushima
            s = line_search(lambda a: cost_function.evaluate_BPR_Potential(f+a*d))
            lineSearchResult = s
            if s < eps:
                if display >= 1: print 'stop with step_size: {}'.format(s)
                return f
            f = f + s*d
        else:
            f = f + 2. * w/(i+2.)

    return f

def search_direction(flow, Cost_Function, graph_object, od):
    # computes the Frank-Wolfe step
    # g is just a canvas containing the link information and to be updated with
    # the most recent edge costs
    grad =  Cost_Function.evaluate_Cost_Function(flow)
    graph_object.es["weight"] = grad.tolist()
    L = all_or_nothing(graph_object, od)
    return L, grad

def line_search(f, res=10):
    # on a grid of 2^res points bw 0 and 1, find global minimum
    # of continuous convex function
    d = 1./(2**res-1)
    l, r = 0, 2**res-1
    while r-l > 1:
        if f(l*d) <= f(l*d+d): return l*d
        if f(r*d-d) >= f(r*d): return r*d
        # otherwise f(l) > f(l+d) and f(r-d) < f(r)
        m1, m2 = (l+r)/2, 1+(l+r)/2
        if f(m1*d) < f(m2*d): r = m1
        if f(m1*d) > f(m2*d): l = m2
        if f(m1*d) == f(m2*d): return m1*d
    return l*d

#Constructs the igraph object used in shortest path calculation
def construct_igraph(traffic_scenario, Cost_Function):
    # 'vertices' contains the range of the vertices' indices in the graph
    vertices = traffic_scenario.beats_api.get_node_ids()

    #Create edges:a list of [[source_node_id, sink_node_id], ...] for each edge
    edges_list = list(traffic_scenario.beats_api.get_link_connectivity()) #convert java list to python list
    edges_array = np.array(edges_list)
    # 'edges' is a list of the edges (to_id, from_id) in the graph
    edges = list(edges_array[:,1:])

    graph_object = igraph.Graph(vertex_attrs={"label":vertices}, edges=edges, directed=True)
    coeff_array = np.array(Cost_Function.Coefficients.values())

    graph_object.es["weight"] =coeff_array[0,:].tolist() # feel with free-flow travel times
    return graph_object

def total_free_flow_cost(graph_object, od):
    return np.array(graph_object.es["weight"]).dot(all_or_nothing(graph_object, od))
