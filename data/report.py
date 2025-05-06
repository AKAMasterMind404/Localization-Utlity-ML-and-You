import multiprocessing
from tqdm import tqdm
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import constants as cnt
from game.auto_game import auto_game


def worker(args):
    """Standalone worker function for parallel processing"""
    try:
        g = auto_game(bot_type=cnt.CURRENT_PART, isUseIpCells=True)
        return f"{g.t},"
    except Exception as e:
        print(f"Error : {str(e)}")
        return ""


class DataService:
    def __init__(self, isGenerateData: bool, points: int):
        """
        Initialize data service
        :param isGenerateData: True to generate data, False to plot
        :param points: Number of runs per parameter combination
        """
        self.points = points
        self.isGenerateData = isGenerateData

        # Initialize empty dataframe
        self.df = pd.DataFrame(columns=['timesteps', 'alpha', 'bot_number', 'is_rat_moving'])

    def generateDataParalelly(self):
        """Generate data in parallel and save to file"""
        params = [() for _ in range(self.points)]  # Number of runs

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "data.txt")

        # Run simulations in parallel
        with multiprocessing.Pool() as pool, \
                open(file_path, "a+") as f:

            # Process results as they complete
            for result in tqdm(pool.imap(worker, params),
                               total=len(params),
                               desc="Running simulations"):
                if result:  # Only write successful results
                    f.write(result)
                    f.flush()

    def plotData(self):
        with open("data/data.txt", "r") as f:
            raw_data = f.read()

        step_counts = [int(x.strip()) for x in raw_data.strip().split(",") if x.strip().isdigit()]

        group_size = 100
        num_groups = len(step_counts) // group_size

        L_sizes = []
        avg_steps = []

        for i in range(num_groups):
            group = step_counts[i * group_size:(i + 1) * group_size]
            L_sizes.append(i + 1)
            avg_steps.append(np.mean(group))

        plt.figure(figsize=(10, 6))
        plt.plot(L_sizes, avg_steps, marker='o')
        plt.xlabel('|L| (Initial Uncertainty Size)')
        plt.ylabel('Average Steps to Localize')
        plt.title('Average Localization Steps vs |L|')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
