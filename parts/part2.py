import random
from parts.localizer import Localizer


class Part2(Localizer):
    def __init__(self, ship, position=None):
        super().__init__(ship, position)
        self.target = self._choose_target()

    def localize(self):
        if self.isLocalized():
            self.ship.game_over = True
            print(f"Localized after {self.ship.t} moves at location {self.possible_locations}")
            self.ship.step += 1
            return

        start = random.choice(list(self.possible_locations))
        path = self.calculatePath(start, self.target)

        if len(path) > 1:
            next_step = path[1]  # index 0 = current position
            action = self._get_direction(start, next_step)
        else:
            # Already at target; fallback to greedy shrink if no path found
            action = random.choice(self.actions)

        self._update_possible_locations(action)
        self.ship.t += 1

    def _choose_target(self):
        # Pick a dead-end or corner cell from currently open
        candidates = list(self.ship.dead_ends)
        if not candidates:
            candidates = list(self.ship.currently_open)

        return random.choice(candidates)

    def _get_direction(self, from_pos, to_pos):
        fx, fy = from_pos
        tx, ty = to_pos
        if tx == fx + 1: return "DOWN"
        if tx == fx - 1: return "UP"
        if ty == fy + 1: return "RIGHT"
        if ty == fy - 1: return "LEFT"
        return random.choice(self.actions)  # fallback

    def _update_possible_locations(self, action):
        new_possible_locations = set()

        for loc in self.possible_locations:
            next_loc = self._get_next_location(loc, action)
            new_possible_locations.add(next_loc)

        self.possible_locations = new_possible_locations

    def _get_next_location(self, loc, action):
        x, y = loc
        potential_next = {
            'UP': (x - 1, y),
            'DOWN': (x + 1, y),
            'LEFT': (x, y - 1),
            'RIGHT': (x, y + 1),
        }

        next_cell = potential_next[action]
        if next_cell in self.ship.currently_open:
            return next_cell
        else:
            return loc
