import networkx as nx
# import matplotlib.pyplot as plt
# from matplotlib.patches import Patch, Rectangle
# from scipy.interpolate import splprep, splev
from collections import deque
import itertools
import seaborn as sns
import numpy as np

def Transform_Graph_From_List(tile_kit):
    graph_kit=nx.MultiDiGraph()
    graph_kit.add_nodes_from(range(len(tile_kit)))

    ## Add edges for internal structure in clockwise orientation
    for i_edge in range(int(len(tile_kit)/4)):
        slices = deque([0,1,2,3])
        for _ in range(4):
            graph_kit.add_edge(i_edge*4+slices[0],i_edge*4+slices[1])
            slices.rotate(-1)

    ## Add edges for graph connections
    for index,face in enumerate(tile_kit):
        i=0
        if face:
            while(Interaction_Matrix(face) in tile_kit[index+i:]):
                i+=tile_kit[index+i:].index(Interaction_Matrix(face))
                graph_kit.add_edge(index,index+i)#,color='r')
                graph_kit.add_edge(index+i,index)#,color='r')
                i+=1

    return graph_kit

def PartitionPhenotype_old(genotypes):
    """
    genotypes: list of genotypes that all have the same phenotype
    returns a list of lists, where the sublists contain isomorphic genotypes
    """
    graph_clusters = [[genotypes[0]]]
    network_graphs = [Transform_Graph_From_List(genotypes[0])]

    for genotype in genotypes[1:]:
        ref_graph=Transform_Graph_From_List(genotype)
        for i,comp_graph in enumerate(network_graphs):
            if nx.is_isomorphic(ref_graph,comp_graph):
                graph_clusters[i].append(genotype)
                break
        else:
            graph_clusters.append([genotype])
            network_graphs.append(ref_graph)

    return graph_clusters

def PartitionPhenotype(genotypes):
    """
    genotypes: list of genotypes that all have the same phenotype
    returns a list of lists, where the sublists contain isomorphic genotypes
    """
    index = 0
    graph_clusters = dict()
    graph_clusters[str(genotypes[index])] = str(index)
    network_graphs = dict()
    network_graphs[str(index)] = Transform_Graph_From_List(genotypes[index])

    for genotype in genotypes[1:]:
        ref_graph = Transform_Graph_From_List(genotype)
        for key, comp_graph in network_graphs.items():
            if nx.is_isomorphic(ref_graph, comp_graph):
                graph_clusters[str(genotype)] = key
                break
        else:
            index += 1
            graph_clusters[str(genotype)] = str(index)
            network_graphs[str(index)] = ref_graph

    return graph_clusters

def Interaction_Matrix(colour):
    return colour if colour <= 0 else (1-colour%2)*(colour-1)+(colour%2)*(colour+1)
