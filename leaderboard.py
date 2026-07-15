# leaderboard.py
import json
import os


class Leaderboard:
    def __init__(self, filename="highscores.json"):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            return []

    def save_score(self, score):
        if score <= 0:
            return

        self.scores.append(score)
        self.scores.sort(reverse=True)
        self.scores = self.scores[:5]

        try:
            with open(self.filename, 'w') as file:
                json.dump(self.scores, file, indent=4)
        except IOError as e:
            print(f"Error saving leaderboard: {e}")

    def get_top_scores(self):
        return self.scores