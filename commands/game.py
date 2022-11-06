games = {}

class Game:
    def __init__(self):
        self.players = []
        self.player_data = {}
        self.started = False
        self.lava_level = 0.2
        self.eliminated = []
        self.penalty_modifier = 1

