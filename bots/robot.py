class Robot:
    def __init__(self, ship, position=None):
        self.ship = ship
        self.position = position
        self.actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        self.possible_locations = self.ship.currently_open.copy()

    def getNextAction(self):
        pass

    def update_possible_locations(self, action):
        new_possible_locations = set()

        for loc in self.possible_locations:
            next_loc = self.get_next_location(loc, action)
            new_possible_locations.add(next_loc)

        self.possible_locations = new_possible_locations

    def get_next_location(self, loc, action):
        x, y = loc
        potential_next = {
            'UP': (x - 1, y),
            'DOWN': (x + 1, y),
            'LEFT': (x, y - 1),
            'RIGHT': (x, y + 1),
        }

        next_cell = potential_next[action]

        # If next cell is open, move there. Otherwise, stay put.
        if next_cell in self.ship.currently_open:
            return next_cell
        else:
            return loc

    def is_localized(self):
        return len(self.possible_locations) == 1
