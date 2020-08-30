import torch
import numpy as np

def valence_compute():
    pass

ATOM_VARIABLE = 1
EDGE_VARIABLE = 2
MSP_VARIABLE = 3
EDGE_FACTOR = 4
MSP_FACTOR = 5

def get_edgeatomfactorsntypes(adj, nodes, edge_index_2, edge_attr_2):

    fact = [] # (number of factors , 3) 3 here are [edge_index, atom_1_index, atom_2_index]
    fact_type = []

    # edge_variable_idxes = (nodes[:, 0] == EDGE_VARIABLE).nonzero()
    # atom_variable_idxes = (nodes[:, 0] == ATOM_VARIABLE).nonzero()
    # a = edge_index_2[0, torch.flatten(edge_variable_idxes)].cpu()
    # b = edge_index_2[1, torch.flatten(atom_variable_idxes)].cpu()
    # res_np = np.intersect1d(a, b)
    # res = torch.from_numpy(res_np)

    edge_variable_idxes = torch.flatten((edge_attr_2[:, 0] == 1).nonzero())

    edge_index_short = edge_index_2[:, edge_variable_idxes]

    # Todo: Factoring this
    for i in range(edge_index_short.shape[1] - 1):
        fact.append([
            edge_index_short[0][i],
            edge_index_short[1][i],
            edge_index_short[1][i+1]
        ])
        fact_type.append([
            1,
            1,
            1
        ])

    # edge_factor_index = torch.flatten((nodes[:, 0] == EDGE_FACTOR).nonzero())
    #
    # fact = nodes[edge_factor_index][:, 1:4]
    # fact = nodes[edge_factor_index][:, 1:4]

    return fact, fact_type

