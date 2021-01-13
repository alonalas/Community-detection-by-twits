def main():
    # question 1 tests
    #print("louvain: " , community_detector('louvain',nx.les_miserables_graph()))
    #print("girvin: " , community_detector('girvin_newman',nx.les_miserables_graph(), edge_selector_optimizer))
    #print("clique_percolation:" , community_detector('clique_percolation', nx.les_miserables_graph(),edge_selector_optimizer))

    #question 2 tests

    final_dict_1 = construct_heb_edges('C:\\Users\\alona\\PycharmProjects\\aluv\\hebrow_twitter_data',
                                      non_parliamentarians_nodes=0)
    network1 = construct_heb_network(final_dict_1)
    central_players_df = pd.read_csv(
        f'C:\\Users\\alona\\PycharmProjects\\aluv\\hebrow_twitter_data\\central_political_players.csv')
    inversed = central_players_df.set_index('id').to_dict()['name']
    dictush = dict(inversed)
    network_with_names = nx.relabel_nodes(network1, inversed)

    partition = community_detector('girvin_newman', network1, edge_selector_optimizer)
    for community in partition['partition']:
        print ("community:")
        community_list = []
        for node in community:
            community_list.append(dictush[node])
        print(community_list)
        print("------------------")
    print(partition)


    nx.draw_networkx(network_with_names,with_labels=True,node_size=100, font_size=6)
    plt.show()
    # final_dict_2 = construct_heb_edges('C:\\Users\\alona\\PycharmProjects\\aluv\\hebrow_twitter_data',non_parliamentarians_nodes=20)
    # network2 = construct_heb_network(final_dict_2)
    # print("finished building graph2")
    # print(community_detector('girvin_newman', network2 ,edge_selector_optimizer))
    # nx.draw(network2, with_labels=True)
    # plt.show()