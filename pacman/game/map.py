from .entities import Wall, Dot, PacMan, Ghost
from .config import tilemap, RED, PINK, CYAN, ORANGE

def create_map(game):
    for y, row in enumerate(tilemap):
        for x, col in enumerate(row):
            if col == "B":
                Wall(game, x, y)
            elif col == ".":
                Dot(game, x, y)
            elif col == "P":
                game.player = PacMan(game, x, y)
            elif col == "G":
                ghosts = [RED, PINK, CYAN, ORANGE]
                color = ghosts[len(game.ghosts)]
                behavior = "chase" if color in [RED, CYAN] else "scatter"
                Ghost(game, x, y, color, behavior)

