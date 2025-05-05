from parts import part1 as b1
from parts import part2 as b2
from parts import localizer as r

def RobotGateway(ship, position: tuple, botType: int) -> r.Localizer:
    if botType == 1:
        robot = b1.Part1(ship, position)
    elif botType == 2:
        robot = b2.Part2(ship, position)
    else:
        raise ValueError(f"Invalid botType: {botType}")
    return robot