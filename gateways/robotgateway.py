from bots import bot1 as b1
from bots import robot as r

def RobotGateway(ship, position: tuple, botType: int) -> r.Robot:
    if botType == 1:
        robot = b1.Bot1(ship, position)
    else:
        raise ValueError(f"Invalid botType: {botType}")
    return robot