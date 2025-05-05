import random
from parts.localizer import Localizer


class Part1(Localizer):
    def __init__(self, ship, position):
        super().__init__(ship, position)
        self.visited = set()
        self.possible_locations = self.ship.currently_open.copy()

    def localize(self):
        action = self._getNextAction()
        self._updatePossibleLocations(action)
        self.ship.t += 1

        if self.isLocalized():
            self.ship.game_over = True
            print(f"Localized after {self.ship.t} moves at location {self.possible_locations}")
            self.ship.step += 1

    def _updatePossibleLocations(self, action):
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

        # If next cell is open, move there. Otherwise, stay put.
        if next_cell in self.ship.currently_open:
            return next_cell
        else:
            return loc

    def _getNextAction(self):
        action_candidates = []
        min_len = float('inf')

        curr = self._location_set_to_str(self.possible_locations)

        for action in self.actions:
            new_locations = set()
            for loc in self.possible_locations:
                next_loc = self._get_next_location(loc, action)
                new_locations.add(next_loc)

            newLocation = self._location_set_to_str(new_locations)

            # Ignore actions that don't change L or already seen
            if newLocation == curr or newLocation in self.visited:
                continue

            if len(new_locations) < min_len:
                min_len = len(new_locations)
                action_candidates = [action]
            elif len(new_locations) == min_len:
                action_candidates.append(action)

        # Save current L
        self.visited.add(curr)

        if action_candidates:
            return random.choice(action_candidates)
        else:
            # All actions stall — fallback to a random move to break symmetry
            return random.choice(self.actions)

    def _location_set_to_str(self, location_set):
        return ",".join(sorted(f"{x}-{y}" for x, y in location_set))
