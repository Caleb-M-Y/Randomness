import math
import sys

import pygame


# Window and gameplay constants.
WIDTH, HEIGHT = 960, 640
FPS = 60
STARTING_LIVES = 20
ENEMY_RADIUS = 14
ENEMY_SPEED = 100.0  # pixels per second
SPAWN_INTERVAL = 1.0  # seconds

# Colors (R, G, B).
BG_COLOR = (28, 32, 40)
PATH_COLOR = (125, 133, 150)
ENEMY_COLOR = (220, 85, 85)
TEXT_COLOR = (245, 245, 245)


class Enemy:
	def __init__(self, path_points, speed=ENEMY_SPEED, hp=1):
		self.path_points = path_points
		self.x, self.y = path_points[0]
		self.speed = speed
		self.hp = hp
		self.target_index = 1
		self.reached_goal = False

	def update(self, dt):
		if self.reached_goal:
			return

		if self.target_index >= len(self.path_points):
			self.reached_goal = True
			return

		target_x, target_y = self.path_points[self.target_index]
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.hypot(dx, dy)

		if distance == 0:
			self.target_index += 1
			return

		step = self.speed * dt

		if step >= distance:
			self.x = target_x
			self.y = target_y
			self.target_index += 1
			if self.target_index >= len(self.path_points):
				self.reached_goal = True
		else:
			self.x += (dx / distance) * step
			self.y += (dy / distance) * step

	def draw(self, surface):
		pygame.draw.circle(surface, ENEMY_COLOR, (int(self.x), int(self.y)), ENEMY_RADIUS)


def draw_path(surface, path_points):
	pygame.draw.lines(surface, PATH_COLOR, False, path_points, 34)


def draw_ui(surface, font, lives, enemies_on_screen):
	lives_text = font.render(f"Lives: {lives}", True, TEXT_COLOR)
	enemy_text = font.render(f"Enemies: {enemies_on_screen}", True, TEXT_COLOR)
	surface.blit(lives_text, (20, 16))
	surface.blit(enemy_text, (20, 48))


def main():
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Tower Defense - Milestone 1")
	clock = pygame.time.Clock()
	font = pygame.font.SysFont("consolas", 24)

	# Fixed path enemies will follow from start to finish.
	path_points = [
		(40, 320),
		(200, 320),
		(200, 140),
		(430, 140),
		(430, 500),
		(760, 500),
		(760, 250),
		(920, 250),
	]

	enemies = []
	spawn_timer = 0.0
	lives = STARTING_LIVES
	running = True

	while running:
		dt = clock.tick(FPS) / 1000.0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		spawn_timer += dt
		if spawn_timer >= SPAWN_INTERVAL:
			spawn_timer = 0.0
			enemies.append(Enemy(path_points))

		for enemy in enemies:
			enemy.update(dt)

		leaked = [enemy for enemy in enemies if enemy.reached_goal]
		if leaked:
			lives -= len(leaked)

		enemies = [enemy for enemy in enemies if not enemy.reached_goal]

		screen.fill(BG_COLOR)
		draw_path(screen, path_points)

		for enemy in enemies:
			enemy.draw(screen)

		draw_ui(screen, font, lives, len(enemies))

		if lives <= 0:
			game_over = font.render("Game Over - Close window to exit", True, TEXT_COLOR)
			screen.blit(game_over, (250, 16))

		pygame.display.flip()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
