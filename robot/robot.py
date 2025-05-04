
class Robot:
    def __init__(self, ship, position):
        self.ship = ship  # Ship grid (30x30)
        self.position = position  # Bot's current position (set after Phase 1)