import networkx as nx
from graph.djikstras import compatibleGraph, djikstras, getPathFromATOB
from helpers.generic import HelperService


class Localizer:
    def __init__(self, ship, position=None):
        self.ship = ship
        self.position = position
        self.actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        self.possible_locations = self.ship.currently_open.copy()

    def localize(self):
        pass

    def isLocalized(self):
        return len(self.possible_locations) == 1

    def calculatePath(self, start, target: tuple):
        ship = self.ship.Ship
        adj_list = list(ship.adjacency())
        comp_graph = compatibleGraph(ship, adj_list)

        # Validate target exists in the compatible graph
        if target not in comp_graph:
            HelperService.printDebug(f"Target cell {target} is not in the compatible graph!")
            return []

        try:
            queue = djikstras(comp_graph, startNode=start)
            path = getPathFromATOB(queue, start, target)
            return path
        except nx.NetworkXNoPath:
            HelperService.printDebug(f"No path exists from {start} to {target}!")
            return []
        except Exception as e:
            HelperService.printDebug(f"Error in path calculation: {str(e)}")
            return []
