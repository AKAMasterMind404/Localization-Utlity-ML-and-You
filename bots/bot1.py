import random
from bots.robot import Robot


class Bot1(Robot):
    def __init__(self, ship, position):
        super().__init__(ship, position)

    def getNextAction(self):
        return random.choice(self.actions)
