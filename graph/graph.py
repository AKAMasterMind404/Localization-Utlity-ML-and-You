import networkx as nx
import random
import constants as cnt
import helpers.draw_grid as dg
from graph.sample.sample1 import currently_open_1, dead_ends_1
from helpers.draw_grid import draw_grid_internal
from helpers.generic import HelperService
from robot.robot import Robot


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
        self.curr_rat_pos = None  # Current and final button position
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

        if self.isUseIpCells:
            xCord, yCord = random.choice(list(currently_open_1))
        else:
            xCord = random.randint(1, self.n - 2)
            yCord = random.randint(1, self.n - 2)
            self.one_neighbour_set = set(HelperService.getEligibleNeighbours(self, (xCord, yCord)))
        self.currently_open.add((xCord, yCord))
        self.Ship.nodes[(xCord, yCord)]['weight'] = 0
        self.open_ship_initialized = True
        draw_grid_internal(self)

    def proceed(self):
        # Everytime proceed is called, one timestep is increased.
        # Timestep counting begins when grid is set, and bot-button-fire is initialized
        # if self.step == 1 and self.isUseIpCells:
        #     # Handles pre-defined graph values
        #     self.step = 4
        #     self.currently_open = currently_open_1
        #     self.dead_ends = dead_ends_1
        #     for i, j in self.dead_ends:
        #         self.Ship.nodes[(i, j)]['weight'] = 0
        #     return
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
            self.current_step = "Ship Generation Complete"
            draw_grid_internal(self)
        elif self.step == 4:
            # PHASE 2
            return
            self.curr_bot_pos = None
            if self.currBot.rat_probability[self.curr_rat_pos] == 0:
                raise ValueError("Rat probability zero error")

            if self.currBot.position == self.curr_rat_pos or self.t > cnt.MAX_MOVES_CAP:
                # Code halt condition if too many time steps are received or if rat is found
                self.step = 5
                return

            if self.currBot.isMove:
                isReached = self.currBot.moveBot()
                # Checks if bot is found whilst reaching the final target
                if isReached:
                    self.step = 5
                    return
            else:
                # Updates ping knowledge base
                self.currBot.updatePingLikelihoodProbabilities()

            if self.is_rat_moving:
                neighbors = HelperService.getOpenNeighbourListForNode(self, self.curr_rat_pos, isIgnoreDiagonals=True)
                cell_to_go_rat = random.choice(neighbors)
                self.curr_rat_pos = cell_to_go_rat
                self.currBot.updateRatProbabilities()
            # Increase the timestep
            self.t += 1
        elif self.step == 5:
            self.game_over = True
            return self
        dg.draw_grid_internal(self)
        return

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

    def placeSpaceRat(self):
        rat_candidates = self.currently_open.copy()
        rat_candidates.remove(self.curr_bot_pos)
        self.curr_rat_pos = random.choice(list(rat_candidates))


def getGraph(screen, bot_type, alpha, is_rat_moving, isUseIpCells: bool = False, isUsePresetPos: bool = False):
    graph = ManhattanGraph(screen=screen, n=cnt.GRID_SIZE, alpha=alpha, bot_type=bot_type, is_rat_moving=is_rat_moving,
                           isUseIpCells=isUseIpCells,
                           isUsePresetPos=isUsePresetPos)
    graph.create_manhattan_graph()

    return graph
