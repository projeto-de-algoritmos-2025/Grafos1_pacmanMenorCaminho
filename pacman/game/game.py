import pygame
from .config import *
from .map import create_map

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        self.font = pygame.font.SysFont(None, 36)
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.LayeredUpdates()
        self.dots = pygame.sprite.LayeredUpdates()
        self.ghosts = pygame.sprite.LayeredUpdates()
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.level = 1
        self.create_menu()

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
        self.all_sprites.empty()
        self.walls.empty()
        self.dots.empty()
        self.ghosts.empty()
        create_map(self)
        self.playing = True

    def level_complete(self):
        self.level += 1
        self.dots.empty()
        self.ghosts.empty()
        create_map(self)
        self.player.reset_position()

    def game_over(self):
        self.playing = False
        self.high_score = max(self.score, self.high_score)
        self.show_start_screen()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and self.playing:
                if hasattr(self, "player"):
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
            self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (10, 10))
            self.screen.blit(self.font.render(f"Lives: {self.lives}", True, WHITE), (WIDTH - 150, 10))
            self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE), (WIDTH//2 - 50, 10))
        pygame.display.flip()

    def run(self):
        self.show_start_screen()
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.quit()

