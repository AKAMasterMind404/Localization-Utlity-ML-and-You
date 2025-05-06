import networkx as nx
import random
import constants as cnt
import helpers.draw_grid as dg
from graph.sample.sample1 import currently_open_1, dead_ends_1
from parts.localizer import Localizer
from gateways.robotgateway import LocalizerGateway
from helpers.draw_grid import draw_grid_internal
from helpers.generic import HelperService


class ManhattanGraph:
    def __init__(self, screen, n, isUseIpCells: bool = False):
        self.n = n  # Dimension of rhe 2d graph
        self.game_over = False  # Indicates whether game may or may not be proceeded
        self.Ship = nx.Graph()  # Graph nodes represented using networkx.Graph object
        self.path = None  # Path outlined by the bot
        self.canProceed = True  # Indicates whether simulation is already under progress
        self.screen = screen  # pygame.screen - May or may not be None
        self.current_step = "Ship Expansion"  # Display Label
        self.open_ship_initialized = False

        self.step = 1  # Track algorithm step
        self.one_neighbour_set = set()  # Set of nodes with one 'open' cell, # Zero indicates 'open' and One indicates 'close'
        self.currently_open = set()  # Nodes that are 'open', # Zero indicates 'open' and One indicates 'close'
        self.multi_neighbour_set = set()  # Converse of one_neighbour_set
        self.dead_ends = list()  # cells that have 3 closed cells around them
        self.curr_bot_pos = None  # Current position of bot
        self.isUseIpCells = isUseIpCells  # A boolean flag indicating opened cells are already defined
        self.currLocalizer: Localizer = None
        self.t = 0  # Time step, calculates how many times proceed() ahs been called. Also, a measure for no of steps taken by bot
        self.L_size = None

    def create_manhattan_graph(self):
        for i in range(self.n):
            for j in range(self.n):
                node = (i, j)
                self.Ship.add_node(node, weight=cnt.CELL_CLOSED)
                if i > 0:
                    self.Ship.add_edge(node, (i - 1, j), weight=cnt.CELL_CLOSED)
                if j > 0:
                    self.Ship.add_edge(node, (i, j - 1), weight=cnt.CELL_CLOSED)

    def initialize_ship_opening(self):
        if self.open_ship_initialized:
            return

        xCord = random.randint(1, self.n - 2)
        yCord = random.randint(1, self.n - 2)

        self.one_neighbour_set = set(HelperService.getEligibleNeighbours(self, (xCord, yCord)))
        self.currently_open.add((xCord, yCord))
        self.Ship.nodes[(xCord, yCord)]['weight'] = 0
        self.open_ship_initialized = True
        draw_grid_internal(self)

    def proceed(self, is_use_ip_cells:bool):
        if self.step == 1:
            if is_use_ip_cells:
                self.currently_open = currently_open_1
                self.dead_ends = dead_ends_1
                for i, j in self.dead_ends:
                    self.Ship.nodes[(i, j)]['weight'] = cnt.CELL_CLOSED
                for i, j in self.currently_open:
                    self.Ship.nodes[(i, j)]['weight'] = cnt.CELL_OPENED
                self.step = 4
                return
            else:
                # Chose one cell to expand
                self.initialize_ship_opening()
                cell_to_expand = random.choice(list(self.one_neighbour_set))
                self.Ship.nodes[cell_to_expand]['weight'] = 0  # Zero indicates 'open' and One indicates 'close'
                self.currently_open.add(cell_to_expand)
                self.one_neighbour_set.remove(cell_to_expand)
                # one_neighbour_set is a set of nodes that are surrounded by just one open cell

                new_candidates = HelperService.getEligibleNeighbours(self, cell_to_expand)
                for candidate in new_candidates:
                    if candidate not in self.multi_neighbour_set:
                        if candidate in self.one_neighbour_set:
                            self.one_neighbour_set.remove(candidate)
                            self.multi_neighbour_set.add(candidate)
                        else:
                            self.one_neighbour_set.add(candidate)
                if not self.one_neighbour_set:
                    # We ran out of cells that we can expand into
                    self.step = 2  # Move to dead-end detection
                    self.current_step = "Identifying Dead Ends"
                draw_grid_internal(self)
        elif self.step == 2:
            HelperService.printDebug(f"Step {self.step} has begun!!")
            self.dead_ends = [node for node in self.currently_open if self.isNodeIsolated(node)]
            self.step = 3  # Move to dead-end expansion
            self.current_step = "Expanding Dead Ends"
            draw_grid_internal(self)

        elif self.step == 3:
            # We randomly open one closed neighbour of half of the dead end cells
            if self.dead_ends:
                HelperService.printDebug(f"Step {self.step} has begun!!")
                num_to_expand = len(self.dead_ends) // 2
                random.shuffle(self.dead_ends)
                for i in range(num_to_expand):
                    dead_end = self.dead_ends[i]
                    closed_neighbors = [neighbor for neighbor in HelperService.getEligibleNeighbours(self, dead_end) if
                                        self.Ship.nodes[neighbor]['weight'] == 1]
                    if closed_neighbors:
                        to_open = random.choice(closed_neighbors)
                        self.Ship.nodes[to_open]['weight'] = 0
                        self.currently_open.add(to_open)
            else:
                HelperService.printDebug("Dead ends not found!!")
            # Ship Generation is Complete!
            self.step = 4
            self.curr_bot_pos = random.choice(list(self.currently_open))
            self.current_step = "Ship Generation Complete"
            self.L_size = len(self.currently_open)
            draw_grid_internal(self)
        elif self.step == 4:
            if self.currLocalizer is None:
                self.currLocalizer: Localizer = LocalizerGateway(self, None, cnt.CURRENT_PART)
            self.currLocalizer.localize()
        elif self.step == 5:
            self.game_over = True
            dg.draw_grid_internal(self)

    def isNodeIsolated(self, node: tuple):
        x, y = node
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]

        isOpenCount = 0
        for nX, nY in neighbors:
            node = self.Ship.nodes[(nX, nY)]
            if node['weight'] == 0:
                isOpenCount += 1

        if isOpenCount == 1:
            return True


def getGraph(screen, isUseIpCells: bool = False):
    graph = ManhattanGraph(screen=screen, n=cnt.GRID_SIZE, isUseIpCells=isUseIpCells)
    graph.create_manhattan_graph()

    return graph
