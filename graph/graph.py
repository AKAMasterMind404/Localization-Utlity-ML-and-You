import networkx as nx
import random
import constants as cnt
import helpers.draw_grid as dg
from bots.robot import Robot
from gateways.robotgateway import RobotGateway
from helpers.draw_grid import draw_grid_internal
from helpers.generic import HelperService


class ManhattanGraph:
    def __init__(self, screen, n, alpha, bot_type, is_rat_moving, isUseIpCells: bool = False,
                 isUsePresetPos: bool = False):
        self.n = n  # Dimension of rhe 2d graph
        self.alpha = alpha  # Detection sensitivity
        self.bot_type = bot_type  # bot type
        self.is_rat_moving: bool = is_rat_moving
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
        self.isUsePresetPos = isUsePresetPos  # A boolean flag indicating fire, bot and button positions are already defined
        self.bot_candidate_nodes = set()  # A set of nodes that are currently open and could be the bots position
        self.currBot: Robot = None
        self.t = 0  # Time step, calculates how many times proceed() ahs been called. Also, a measure for no of steps taken by bot

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

    def proceed(self):
        if self.step == 1 and self.one_neighbour_set:
            # Chose one cell to expand
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
            draw_grid_internal(self)
        elif self.step == 4:
            if self.currBot is None:
                self.currBot: Robot = RobotGateway(self, None, cnt.CURRENT_BOT)

            action = self.currBot.getNextAction()
            self.currBot.update_possible_locations(action)
            self.t += 1

            if self.currBot.is_localized():
                self.game_over = True
                print(f"Localized after {self.t} moves at location {self.currBot.possible_locations}")
                self.step = 5  # End the localization step

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


def getGraph(screen, bot_type, alpha, is_rat_moving, isUseIpCells: bool = False, isUsePresetPos: bool = False):
    graph = ManhattanGraph(screen=screen, n=cnt.GRID_SIZE, alpha=alpha, bot_type=bot_type, is_rat_moving=is_rat_moving,
                           isUseIpCells=isUseIpCells,
                           isUsePresetPos=isUsePresetPos)
    graph.create_manhattan_graph()

    return graph
