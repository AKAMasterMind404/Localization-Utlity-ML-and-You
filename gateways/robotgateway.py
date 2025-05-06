from parts import localizer1 as b1
from parts import localizer2 as b2
from parts import localizer3 as b3
from parts import localizer as r

def LocalizerGateway(ship, position: tuple, botType: int) -> r.Localizer:
    if botType == 1:
        robot = b1.Localizer1(ship, position)
    elif botType == 2:
        robot = b2.Localizer2(ship, position)
    elif botType == 3:
        robot = b3.Localizer3(ship, position)
    else:
        raise ValueError(f"Invalid botType: {botType}")
    return robot