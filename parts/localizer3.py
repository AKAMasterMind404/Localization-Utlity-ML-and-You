import random
import joblib
from parts.localizer import Localizer
from parts.localizer1 import Localizer1  # π₀ strategy

class Localizer3(Localizer):
    def __init__(self, ship, position=None, model_path="../models/model_p0.joblib"):
        super().__init__(ship, position)
        self.possible_locations = self.ship.currently_open.copy()
        self.visited = set()
        self.model = joblib.load(model_path)  # Load trained π₀ estimator
        self.fallback = Localizer1(ship, position)  # Fallback to π₀ after first move
        self.has_looked_ahead = False  # Track if π₁ logic has been used

    def localize(self):
        if self.isLocalized():
            self.ship.game_over = True
            print(f"Localized after {self.ship.t} moves at location {self.possible_locations}")
            self.ship.step += 1
            return

        if not self.has_looked_ahead:
            self._one_step_lookahead()
            self.has_looked_ahead = True
        else:
            self.fallback.possible_locations = self.possible_locations
            self.fallback.localize()
            self.possible_locations = self.fallback.possible_locations

        self.ship.t += 1

    def _one_step_lookahead(self):
        best_action = None
        best_predicted_cost = float('inf')
        best_new_L = None
        current_state_str = self._location_set_to_str(self.possible_locations)
        self.visited.add(current_state_str)

        for action in self.actions:
            new_L = {self._getNextLocation(loc, action) for loc in self.possible_locations}
            new_state_str = self._location_set_to_str(new_L)

            if new_state_str in self.visited:
                continue

            predicted_cost = self.model.predict([[len(new_L)]])[0]

            if predicted_cost < best_predicted_cost:
                best_predicted_cost = predicted_cost
                best_action = action
                best_new_L = new_L

        if best_action:
            self.possible_locations = best_new_L
        else:
            # Fallback to random if all actions lead to visited or stagnant sets
            fallback_action = random.choice(self.actions)
            self.possible_locations = {
                self._getNextLocation(loc, fallback_action) for loc in self.possible_locations
            }

    def _getNextLocation(self, loc, action):
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
