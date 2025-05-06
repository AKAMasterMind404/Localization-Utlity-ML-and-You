from graph.graph import getGraph
from graph.sample.sample1 import currently_open_1, dead_ends_1

# A function that runs a simulation without screen / ui elements
def auto_game(bot_type, isUseIpCells: bool = True, open_cells = []):
    print(f"Autogame started part type: {bot_type}")
    graph = getGraph(None, isUseIpCells)
    if isUseIpCells:
        graph.currently_open = open_cells if open_cells else currently_open_1
        graph.dead_ends_1 = dead_ends_1

    while not graph.game_over:
        graph.proceed(is_use_ip_cells=isUseIpCells)
    return graph
