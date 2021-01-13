import os
import networkx as nx
import pandas as pd
import community as community_louvain
import re
from datetime import datetime as dt
import json
import math

def get_name():
    return "Alona Lasry"


def get_id():
    return "205567944"

#------------------------------------ 1 ------------------------------------
#------------- i ---------------
def community_detector(algorithm_name, network, most_valualble_edge= None):

    dict = {}
    if algorithm_name == 'girvin_newman':
        result = nx.algorithms.community.girvan_newman(network,most_valualble_edge)
        modularities = []
        max_modularity = 0
        for partition_tuple_of_sets in result:
            modularity = nx.algorithms.community.modularity(network,partition_tuple_of_sets)
            modularities.append((partition_tuple_of_sets,modularity))
            if modularity > max_modularity:
                max_modularity = modularity
        partition = []
        for tup in modularities:
            if tup[1] == max_modularity:
                dict['num_partitions'] = len(tup[0])
                dict['modularity'] = max_modularity
                for community_set in tup[0]:
                    partition.append(list(community_set))
                dict['partition'] = partition

    elif algorithm_name == 'clique_percolation':

        partitions = []
        largest_community = nx.graph_clique_number(network)
        if largest_community > 3:
            for k in range(3, largest_community):
                partitions.append(nx.algorithms.community.k_clique_communities(network,k))

        modularities = []
        for part in partitions:
            partition = []
            for community in part:
                list_of_nodes = list(community)
                partition.append(list_of_nodes)
            modularities.append((partition,compute_modularity(network,partition)))

        list_of_modularities = []
        for tup in modularities:
            list_of_modularities.append(tup[1])

        maximal_modularity = max(list_of_modularities)
        for tuptup in modularities:
            if tuptup[1] == maximal_modularity:
                dict['num_partitions'] = len(tuptup[0])
                dict['modularity'] = maximal_modularity
                dict['partition'] = tuptup[0]

    else:#algorithm_name == 'louvain'

        result = community_louvain.best_partition(network)
        community_set = set(list(result.values()))

        partition = []
        for community_index in community_set:
            community_nodes = []
            for node, node_community in result.items():
                if node_community == community_index:
                    community_nodes.append(node)
            partition.append(community_nodes)

        dict['num_partitions'] = len(community_set)
        dict['modularity'] = community_louvain.modularity(result,network)
        dict['partition'] = partition

    return dict

def edge_selector_optimizer(graph):
    btw_dictionary = nx.edge_betweenness_centrality(graph)
    maximal_betweenness = max(btw_dictionary.values())
    for edge,betweenness in btw_dictionary.items():
        if betweenness == maximal_betweenness:
            return edge

def construct_heb_edges(files_path, start_date = '2019-03-15', end_date = '2019-04-15', non_parliamentarians_nodes = 0):

    central_players_df = pd.read_csv(f'{files_path}\central_political_players.csv')
    central_players = central_players_df['id'].tolist()

    format_start_date = dt.strptime(start_date, '%Y-%m-%d').date()
    format_end_date = dt.strptime(end_date, '%Y-%m-%d').date()
    files_in_range = []

    for file_name in os.listdir(files_path):
        if file_name.endswith('.txt'):
            date = re.search(r'\d{4}-\d{2}-\d{2}', file_name)
            if format_start_date <= dt.strptime(date.group(), '%Y-%m-%d').date():
                if format_end_date >= dt.strptime(date.group(), '%Y-%m-%d').date():
                    files_in_range.append(file_name)

    edge_dictionary = {}

    additional_nodes = 0
    for file_name in files_in_range:
        file = open(files_path + '\\' + file_name)
        for tweet in file:
            tweet_json = json.loads(tweet)
            if 'retweeted_status' in tweet_json:
                tup = (tweet_json['user']['id'], tweet_json['retweeted_status']['user']['id'])
                if tup[0] in central_players and tup[1] in central_players:
                        if tup in edge_dictionary:
                            edge_dictionary[tup] +=1
                        else:
                            edge_dictionary[tup] = 1
                else:
                    if (tup[0] in central_players and tup[1] not in central_players) or (tup[1] in central_players and tup[0] not in central_players):
                        if tup in edge_dictionary:
                            edge_dictionary[tup] +=1
                        else:
                            if additional_nodes < non_parliamentarians_nodes:
                                additional_nodes += 1
                                edge_dictionary[tup] = 1

    return edge_dictionary

#returns a networkX object (consisting of the input nodes and edges).
def construct_heb_network(edge_dictionary):
    graph = nx.DiGraph()
    for tup in edge_dictionary.keys():
        for node in tup:
            if not graph.has_node(node):
                graph.add_node(tup[0])
    for tup, weight in edge_dictionary.items():
        graph.add_edge(tup[0], tup[1], weight=weight)

    return graph

def compute_modularity(network, partition):
    L = network.number_of_edges()
    Modularity = 0
    for community in partition:
        Lc = 0
        Kc = 0
        for node in network.nodes():
            if node in community:
                Kc += network.degree(node)
        for edge in network.edges():
            if edge[0] in community and edge[1] in community:
                Lc += 1
        Mc = (Lc / L - math.pow((Kc / (2 * L)), 2))
        Modularity += Mc
    return Modularity
