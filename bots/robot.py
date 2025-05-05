class Robot:
    def __init__(self, ship, position=None):
        self.ship = ship
        self.position = position
        self.actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        self.possible_locations = self.ship.currently_open.copy()

    def getNextAction(self):
        pass

    def localize(self):
        pass

    def isLocalized(self):
        return len(self.possible_locations) == 1
