import random
from parts.localizer import Localizer


class Localizer2(Localizer):
    def __init__(self, ship, position=None):
        super().__init__(ship, position)
        self.target = self._choose_target()
        self.visited = set()
        self.possible_locations = self.ship.currently_open.copy()

    def localize(self):
        if self.isLocalized():
            self.ship.game_over = True
            print(f"Localized after {self.ship.t} moves at location {self.possible_locations}")
            self.ship.step += 1
            return

        current_state_str = self._location_set_to_str(self.possible_locations)
        self.visited.add(current_state_str)

        best_action = None
        best_new_state = None
        min_len = float('inf')

        for action in self.actions:
            new_L = self._simulate_action(self.possible_locations, action)
            new_state_str = self._location_set_to_str(new_L)

            if new_state_str in self.visited:
                continue  # Already seen, skip

            if len(new_L) < min_len:
                min_len = len(new_L)
                best_action = action
                best_new_state = new_L

        if best_action:
            self.possible_locations = best_new_state
        else:
            # All actions lead to seen or same states — fallback to random
            action = random.choice(self.actions)
            self.possible_locations = self._simulate_action(self.possible_locations, action)

        self.ship.t += 1

    def _simulate_action(self, locs, action):
        return {self._get_next_location(loc, action) for loc in locs}

    def _choose_target(self):
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

    def _get_next_location(self, loc, action):
        x, y = loc
        potential_next = {
            'UP': (x - 1, y),
            'DOWN': (x + 1, y),
            'LEFT': (x, y - 1),
            'RIGHT': (x, y + 1),
        }
        next_cell = potential_next[action]
        return next_cell if next_cell in self.ship.currently_open else loc

    def _location_set_to_str(self, location_set):
        return ",".join(sorted(f"{x}-{y}" for x, y in location_set))
