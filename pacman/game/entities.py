import pygame
import random
from collections import deque
from .config import TILE_SIZE, YELLOW, WHITE, BLUE, RED, PINK, CYAN, ORANGE, WIDTH, HEIGHT

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
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)  
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

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

