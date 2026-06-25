import math
import sys

import pygame


# Window and gameplay constants.
WIDTH, HEIGHT = 960, 640
FPS = 60
STARTING_LIVES = 20
STARTING_CASH = 100
ENEMY_RADIUS = 14
ENEMY_SPEED = 100.0  # pixels per second
SPAWN_INTERVAL = 1.0  # seconds
PROJECTILE_SPEED = 380.0
TOWER_RANGE = 150
TOWER_FIRE_RATE = 0.75
TOWER_COST = 50
ENEMY_REWARD = 20

# Colors (R, G, B).
BG_COLOR = (28, 32, 40)
PATH_COLOR = (125, 133, 150)
ENEMY_COLOR = (220, 85, 85)
TEXT_COLOR = (245, 245, 245)
TOWER_COLOR = (86, 181, 130)
SPOT_COLOR = (80, 95, 110)
PROJECTILE_COLOR = (255, 220, 120)


class Enemy:
	def __init__(self, path_points, speed=ENEMY_SPEED, hp=5):
		self.path_points = path_points
		self.x, self.y = path_points[0]
		self.speed = speed
		self.hp = hp
		self.target_index = 1
		self.alive = True
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


class Tower:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.range = TOWER_RANGE
		self.fire_rate = TOWER_FIRE_RATE
		self.cooldown = 0.0

	def update(self, dt, enemies, projectiles):
		if self.cooldown > 0:
			self.cooldown -= dt

		if self.cooldown > 0:
			return

		target = self.find_target(enemies)
		if target is None:
			return

		projectiles.append(Projectile(self.x, self.y, target))
		self.cooldown = self.fire_rate

	def find_target(self, enemies):
		for enemy in enemies:
			if not enemy.alive or enemy.reached_goal:
				continue

			distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
			if distance <= self.range:
				return enemy

		return None

	def draw(self, surface):
		pygame.draw.circle(surface, TOWER_COLOR, (self.x, self.y), 18)
		pygame.draw.circle(surface, TEXT_COLOR, (self.x, self.y), self.range, 1)


class Projectile:
	def __init__(self, x, y, target, speed=PROJECTILE_SPEED):
		self.x = x
		self.y = y
		self.target = target
		self.speed = speed
		self.active = True

	def update(self, dt):
		if not self.active:
			return

		if self.target is None or not self.target.alive or self.target.reached_goal:
			self.active = False
			return

		dx = self.target.x - self.x
		dy = self.target.y - self.y
		distance = math.hypot(dx, dy)

		if distance <= self.speed * dt:
			self.target.hp -= 1
			if self.target.hp <= 0:
				self.target.alive = False
			self.active = False
			return

		self.x += (dx / distance) * self.speed * dt
		self.y += (dy / distance) * self.speed * dt

	def draw(self, surface):
		pygame.draw.circle(surface, PROJECTILE_COLOR, (int(self.x), int(self.y)), 5)


def draw_path(surface, path_points):
	pygame.draw.lines(surface, PATH_COLOR, False, path_points, 34)


def draw_build_spots(surface, build_spots, occupied_spots):
	for spot in build_spots:
		color = TOWER_COLOR if spot in occupied_spots else SPOT_COLOR
		pygame.draw.circle(surface, color, spot, 22, 2)


def draw_ui(surface, font, lives, cash, enemies_on_screen):
	lives_text = font.render(f"Lives: {lives}", True, TEXT_COLOR)
	cash_text = font.render(f"Cash: {cash}", True, TEXT_COLOR)
	enemy_text = font.render(f"Enemies: {enemies_on_screen}", True, TEXT_COLOR)
	surface.blit(lives_text, (20, 16))
	surface.blit(cash_text, (20, 48))
	surface.blit(enemy_text, (20, 80))


def get_clicked_spot(mouse_pos, build_spots, occupied_spots):
	for spot in build_spots:
		if spot in occupied_spots:
			continue

		if math.hypot(mouse_pos[0] - spot[0], mouse_pos[1] - spot[1]) <= 22:
			return spot

	return None


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
	build_spots = [
		(120, 220),
		(120, 420),
		(315, 230),
		(330, 560),
		(560, 400),
		(640, 555),
		(830, 400),
		(840, 170),
	]

	enemies = []
	towers = []
	projectiles = []
	occupied_spots = set()
	spawn_timer = 0.0
	lives = STARTING_LIVES
	cash = STARTING_CASH
	running = True

	while running:
		dt = clock.tick(FPS) / 1000.0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and lives > 0:
				clicked_spot = get_clicked_spot(event.pos, build_spots, occupied_spots)
				if clicked_spot is not None and cash >= TOWER_COST:
					towers.append(Tower(*clicked_spot))
					occupied_spots.add(clicked_spot)
					cash -= TOWER_COST

		if lives > 0:
			spawn_timer += dt
			if spawn_timer >= SPAWN_INTERVAL:
				spawn_timer = 0.0
				enemies.append(Enemy(path_points))

			for enemy in enemies:
				enemy.update(dt)

			for tower in towers:
				tower.update(dt, enemies, projectiles)

			for projectile in projectiles:
				projectile.update(dt)

		leaked = [enemy for enemy in enemies if enemy.reached_goal]
		if leaked:
			lives -= len(leaked)

		defeated = [enemy for enemy in enemies if enemy.alive is False]
		if defeated:
			cash += len(defeated) * ENEMY_REWARD

		enemies = [enemy for enemy in enemies if enemy.alive and not enemy.reached_goal]
		projectiles = [projectile for projectile in projectiles if projectile.active]

		screen.fill(BG_COLOR)
		draw_path(screen, path_points)
		draw_build_spots(screen, build_spots, occupied_spots)

		for enemy in enemies:
			enemy.draw(screen)

		for tower in towers:
			tower.draw(screen)

		for projectile in projectiles:
			projectile.draw(screen)

		draw_ui(screen, font, lives, cash, len(enemies))

		if lives <= 0:
			game_over = font.render("Game Over - Close window to exit", True, TEXT_COLOR)
			screen.blit(game_over, (250, 16))

		pygame.display.flip()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
