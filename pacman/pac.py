import pygame
import sys
import random
from collections import deque

WIDTH, HEIGHT = 608, 672
TILE_SIZE = 32
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

tilemap = [
    "BBBBBBBBBBBBBBBBBBBB",
    "B........BB.......BB",
    "B.BBBB.BB.BB.BBBB.BB",
    "B.B....B...B....B.BB",
    "B.B.BBBBB BBBBB.B.BB",
    "B...B.........B...GB",
    "BBB.B.BBBBBBB.B.BBBB",
    "B.....B     B.....PB",
    "B.BBBBB     BBBBB.BB",
    "B.B.............B.BB",
    "B.BBBBB     BBBBB.BB",
    "B.....B     B.....BB",
    "BBB.B.BBB.BBB.B.BBBB",
    "B...B.........B...BB",
    "B.B.BBBBB BBBBB.B.BB",
    "B.B....B...B....B.BB",
    "B.BBBB.BB.BB.BBBB.BB",
    "B........BB.......BB",
    "BBBBBBBBBBBBBBBBBBBB"
]


class PacMan(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 4
        self.groups = self.game.all_sprites
        super().__init__(self.groups)
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.direction = "right"
        self.next_direction = "right"
        self.speed = 2
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.animation_frames = 0
        self.mouth_angle = 45

    def update(self):
        self.move()
        self.collide_with_dots()
        self.collide_with_ghosts()
        self.animation_frames += 1
        if self.animation_frames % 5 == 0:
            self.mouth_angle = 45 if self.mouth_angle == 0 else 0

    def move(self):
        if self.direction != self.next_direction and self.can_move(self.next_direction):
            self.direction = self.next_direction
        if self.can_move(self.direction):
            if self.direction == "right":
                self.rect.x += self.speed
            elif self.direction == "left":
                self.rect.x -= self.speed
            elif self.direction == "up":
                self.rect.y -= self.speed
            elif self.direction == "down":
                self.rect.y += self.speed
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0

    def can_move(self, direction):
        test_rect = self.rect.copy()
        if direction == "right":
            test_rect.x += self.speed
        elif direction == "left":
            test_rect.x -= self.speed
        elif direction == "up":
            test_rect.y -= self.speed
        elif direction == "down":
            test_rect.y += self.speed
        return not any(test_rect.colliderect(wall.rect) for wall in self.game.walls)

    def collide_with_dots(self):
        hits = pygame.sprite.spritecollide(self, self.game.dots, True)
        for _ in hits:
            self.game.score += 10
            if len(self.game.dots) == 0:
                self.game.level_complete()

    def collide_with_ghosts(self):
        hits = pygame.sprite.spritecollide(self, self.game.ghosts, False)
        if hits:
            self.game.lives -= 1
            if self.game.lives <= 0:
                self.game.game_over()
            else:
                self.reset_position()

    def reset_position(self):
        self.rect.x = self.x
        self.rect.y = self.y
        self.direction = "right"
        self.next_direction = "right"

class Ghost(pygame.sprite.Sprite):
    def __init__(self, game, x, y, color, behavior):
        self.game = game
        self._layer = 3
        self.groups = self.game.all_sprites, self.game.ghosts
        super().__init__(self.groups)
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.color = color
        self.behavior = behavior
        self.direction = random.choice(["up", "down", "left", "right"])
        self.speed = 1.5
        self.target = None
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.move()
        self.check_collision_with_pacman()

    def bfs(self, start, goal):
        queue = deque()
        queue.append(start)
        visited = {start}
        came_from = {}
        while queue:
            current = queue.popleft()
            if current == goal:
                break
            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    came_from[neighbor] = current
        path = []
        current = goal
        while current != start:
            if current in came_from:
                path.append(current)
                current = came_from[current]
            else:
                return []
        path.reverse()
        return path

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        directions = [(0, -TILE_SIZE), (0, TILE_SIZE), (-TILE_SIZE, 0), (TILE_SIZE, 0)]
        for dx, dy in directions:
            neighbor_rect = pygame.Rect(x + dx, y + dy, TILE_SIZE, TILE_SIZE)
            if not any(neighbor_rect.colliderect(w.rect) for w in self.game.walls):
                neighbors.append((x + dx, y + dy))
        return neighbors

    def move(self):
        if self.color == RED:
            start = (self.rect.x // TILE_SIZE * TILE_SIZE, self.rect.y // TILE_SIZE * TILE_SIZE)
            goal = (self.game.player.rect.x // TILE_SIZE * TILE_SIZE, self.game.player.rect.y // TILE_SIZE * TILE_SIZE)
            path = self.bfs(start, goal)
            if path:
                next_pos = path[0]
                dx = next_pos[0] - self.rect.x
                dy = next_pos[1] - self.rect.y
                if dx > 0:
                    self.rect.x += self.speed
                elif dx < 0:
                    self.rect.x -= self.speed
                elif dy > 0:
                    self.rect.y += self.speed
                elif dy < 0:
                    self.rect.y -= self.speed
            return
        if random.random() < 0.1 or not self.can_move(self.direction):
            options = [d for d in ["up", "down", "left", "right"] if d != self.get_opposite_direction() and self.can_move(d)]
            if self.target and options:
                self.direction = min(options, key=lambda d: self.distance_to_target(d))
        if self.can_move(self.direction):
            if self.direction == "right":
                self.rect.x += self.speed
            elif self.direction == "left":
                self.rect.x -= self.speed
            elif self.direction == "up":
                self.rect.y -= self.speed
            elif self.direction == "down":
                self.rect.y += self.speed
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0

    def can_move(self, direction):
        test_rect = self.rect.copy()
        if direction == "right":
            test_rect.x += self.speed
        elif direction == "left":
            test_rect.x -= self.speed
        elif direction == "up":
            test_rect.y -= self.speed
        elif direction == "down":
            test_rect.y += self.speed
        return not any(test_rect.colliderect(wall.rect) for wall in self.game.walls)

    def distance_to_target(self, direction):
        test_rect = self.rect.copy()
        if direction == "up":
            test_rect.y -= self.speed
        elif direction == "down":
            test_rect.y += self.speed
        elif direction == "left":
            test_rect.x -= self.speed
        elif direction == "right":
            test_rect.x += self.speed
        return ((test_rect.x - self.target[0]) ** 2 + (test_rect.y - self.target[1]) ** 2) ** 0.5

    def get_opposite_direction(self):
        return {"up": "down", "down": "up", "left": "right", "right": "left"}.get(self.direction)

    def check_collision_with_pacman(self):
        if pygame.sprite.collide_rect(self, self.game.player):
            if self.behavior == "frightened":
                self.kill()
                self.game.score += 200
            else:
                self.game.lives -= 1
                if self.game.lives <= 0:
                    self.game.game_over()
                else:
                    self.game.player.reset_position()
                    for ghost in self.game.ghosts:
                        ghost.rect.x = ghost.x
                        ghost.rect.y = ghost.y

class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 2
        self.groups = self.game.all_sprites, self.game.walls
        super().__init__(self.groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

class Dot(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = 1
        self.groups = self.game.all_sprites, self.game.dots
        super().__init__(self.groups)
        self.radius = 3
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), self.radius)
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

class PowerPellet(Dot):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.radius = 8
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), self.radius)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        self.font = pygame.font.SysFont(None, 36)
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.level = 1
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.LayeredUpdates()
        self.dots = pygame.sprite.LayeredUpdates()
        self.ghosts = pygame.sprite.LayeredUpdates()
        self.create_map()
        self.create_menu()

    def create_map(self):
        for i, row in enumerate(tilemap):
            for j, col in enumerate(row):
                if col == "B":
                    Wall(self, j, i)
                elif col == ".":
                    Dot(self, j, i)
                elif col == "P":
                    self.player = PacMan(self, j, i)
                elif col == "G":
                    if len(self.ghosts) == 0:
                        Ghost(self, j, i, RED, "chase")
                    elif len(self.ghosts) == 1:
                        Ghost(self, j, i, PINK, "scatter")
                    elif len(self.ghosts) == 2:
                        Ghost(self, j, i, CYAN, "chase")
                    elif len(self.ghosts) == 3:
                        Ghost(self, j, i, ORANGE, "scatter")

    def create_menu(self):
        self.title_font = pygame.font.SysFont(None, 72)
        self.menu_font = pygame.font.SysFont(None, 48)
        self.title_text = self.title_font.render("PAC-MAN", True, YELLOW)
        self.start_text = self.menu_font.render("Press SPACE to Start", True, WHITE)
        self.quit_text = self.menu_font.render("Press Q to Quit", True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.start_rect = self.start_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.quit_rect = self.quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.title_text, self.title_rect)
        self.screen.blit(self.start_text, self.start_rect)
        self.screen.blit(self.quit_text, self.quit_rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                        self.new_game()
                    elif event.key == pygame.K_q:
                        waiting = False
                        self.running = False

    def new_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        for sprite in self.all_sprites:
            sprite.kill()
        self.create_map()
        self.playing = True

    def level_complete(self):
        self.level += 1
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.kill()
        self.create_map()
        self.player.reset_position()

    def game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.playing = False
        self.show_game_over()

    def show_game_over(self):
        game_over_text = self.title_font.render("GAME OVER", True, RED)
        score_text = self.menu_font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = self.menu_font.render(f"High Score: {self.high_score}", True, WHITE)
        restart_text = self.menu_font.render("Press SPACE to Restart", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))
        self.screen.fill(BLACK)
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_score_text, high_score_rect)
        self.screen.blit(restart_text, restart_rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                        self.new_game()
                    elif event.key == pygame.K_q:
                        waiting = False
                        self.running = False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN and self.playing:
                if self.playing and hasattr(self, "player"):
                    if event.key == pygame.K_RIGHT:
                        self.player.next_direction = "right"
                    elif event.key == pygame.K_LEFT:
                        self.player.next_direction = "left"
                    elif event.key == pygame.K_UP:
                        self.player.next_direction = "up"
                    elif event.key == pygame.K_DOWN:
                        self.player.next_direction = "down"

    def update(self):
        if self.playing:
            self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        if self.playing:
            self.all_sprites.draw(self.screen)
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            level_text = self.font.render(f"Level: {self.level}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (WIDTH - 150, 10))
            self.screen.blit(level_text, (WIDTH//2 - 50, 10))
        pygame.display.flip()

    def run(self):
        self.show_start_screen()
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

