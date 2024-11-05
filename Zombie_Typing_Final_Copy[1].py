import pygame
import random
from pygame import mixer

pygame.init()
pygame.mixer.init()

BLACK = (0,0,0)
RED = (255, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)
BORDER = (77, 77, 77)
BUTTON_GREY = (255, 44, 53)
BUTTON_GREEN = (0, 153, 0)
ACTIVE_GREEN = (0, 53, 0)
TEXT_BOX = (255,165,53)
TEXT_COLOR = (135,18,130)
TIPS = (196, 134, 31)
game_over = False
title_screen = True
victory = False
zombie_speed = 1.05
spawning_pool = 77
boss_speed = 150
level_spawn_timer = 0
boss_spawn_timer = 12000

wave_two_started = False
wave_three_started = False
wave_three_rotating_sides = 0

total_kill_count = 0

screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Zombie Typing")
FPS = 60
number_of_zombies = 6
number_of_zombies_setting = "Many"

level_wave = 1
current_stage = 0

clock = pygame.time.Clock()
run = True
font = pygame.font.Font("Zombie.ttf", 36)
button_font = pygame.font.SysFont("comicsans", 30)
gunshot_words = ""
backspace_delay = 4
gunshot_word_display = font.render(gunshot_words, True, RED)
zombie_words = []
zombie_adjectives = []
zombie_nouns = []
zombie_tiny = []
boss_words = []

with open("boss_words.txt", "r") as f:
    boss_words = f.readlines()
boss_words = [line.strip() for line in boss_words]
f.close()

with open("zombie_normal.txt", "r") as f:
    zombie_words = f.readlines()
zombie_words = [line.strip() for line in zombie_words]
f.close()

with open("zombie_tiny.txt", "r") as f:
    zombie_tiny = f.readlines()
zombie_tiny = [line.strip() for line in zombie_tiny]
f.close()

with open("ZombieAdjectives.txt", "r") as f:
    zombie_adjectives = f.readlines()
zombie_adjectives = [line.strip() for line in zombie_adjectives]
f.close()

with open("ZombieNouns.txt", "r") as f:
    zombie_nouns = f.readlines()
zombie_nouns = [line.strip() for line in zombie_nouns]
f.close()

class Background(pygame.sprite.Sprite):
	def __init__(self, image):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
		self.rect = self.image.get_rect()
		self.rect.center = (600, 400)

class Button(pygame.sprite.Sprite):
	def __init__(self, text):
		self.text = text
		self.rect = pygame.Rect(0,0, 250, 70)
		self.color = BUTTON_GREY
		self.colinked = False
		self.active = False
		self.spawn_number = 0
		self.zombie_speed = 0
	def draw(self):
		pygame.draw.rect(screen, self.color, (self.rect))
		display_text = font.render(self.text, True, TEXT_COLOR)
		screen.blit(display_text, (self.rect.x+ 133-len(self.text)*8.5, self.rect.y+15))
	def update(self):
		if (self.rect.collidepoint(pygame.mouse.get_pos())):
			if self.active == False:
				self.color = BUTTON_GREEN
		else:
			if self.active == False:
				self.color = BUTTON_GREY

class Final_Boss(pygame.sprite.Sprite):
	def __init__ (self, image):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
		self.original_image = self.image
		self.bang = pygame.image.load("Beatrice_Bang.png")
		self.health = 100
		self.rect = self.image.get_rect()
		self.bang_timer = 0

class BossTextBox():
	def __init__ (self, text):
		self.text = text
		self.alive = True
		self.x = 300
		self.y = 680
	def display_text(self):
		zombie_word_display = font.render(self.text, True, TEXT_COLOR)
		pygame.draw.rect(screen, TEXT_BOX, pygame.Rect(self.x-5, self.y-75, 600, 60))
		pygame.draw.rect(screen, BORDER, (self.x-5, self.y-75, 600, 60), 4, border_radius=1)
		screen.blit(zombie_word_display, (self.x, self.y - 65))
	def rise(self, speed):
		self.y -= speed
	def get_y(self):
		return self.y


class Player(pygame.sprite.Sprite):
	def __init__(self, image):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
		self.original_image = self.image
		self.bang = pygame.image.load("Phoebe_Bang.png")
		self.walk_a_image = pygame.image.load("Phoebe_Walk_A.png")
		self.walk_b_image = pygame.image.load("Phoebe_Walk_B.png")
		self.new_l_original_image = self.image
		self.new_l_bang = pygame.image.load("Phoebe_Bang.png")
		self.new_l_walk_a_image = pygame.image.load("Phoebe_Walk_A.png")
		self.new_l_walk_b_image = pygame.image.load("Phoebe_Walk_B.png")
		self.rect = self.image.get_rect()
		self.health = 100
		self.health_bar_name = "HEALTH: "
		self.kill_count = 0
		self.moving = 25
		self.bang_timer = 0
		self.move_to_new_spot = 0
		self.facing_right = True
		self.move_timer = 0
		self.hitbox = pygame.Rect(self.rect.center[0], self.rect.center[1], 100, 100)
	def new_level(self):
		self.image = self.new_l_original_image
		self.original_image = self.new_l_original_image
		self.bang = self.new_l_bang
		self.walk_a_image = self.new_l_walk_a_image
		self.walk_b_image = self.new_l_walk_b_image
		self.health = 100
	def display_health(self):
		pygame.draw.rect(screen, RED, pygame.Rect(870, 725, self.health * 3, 25))
		kill_count_display = font.render(str(self.kill_count), True, RED)
		screen.blit(kill_count_display, (900, 760))
	def damage(self, damage):
		self.health -= damage
	def get_health(self):
		return self.health
	def flip_sides(self):
		self.image = pygame.transform.flip(self.image, True, False)
		self.original_image = pygame.transform.flip(self.original_image, True, False)
		self.bang = pygame.transform.flip(self.bang, True, False)
		self.walk_a_image = pygame.transform.flip(self.walk_a_image, True, False)
		self.walk_b_image = pygame.transform.flip(self.walk_a_image, True, False)

	def new_wave(self):
		if (self.move_to_new_spot > 0):
			self.move_to_new_spot -= 1
			self.rect.center = (self.rect.center[0] + 10, self.rect.center[1])
			self.move_timer += 1
			if self.move_to_new_spot == 0:
				self.flip_sides()
				self.facing_right = False
		if (self.move_to_new_spot < 0):
			self.move_to_new_spot += 1
			self.rect.center = (self.rect.center[0] - 10, self.rect.center[1])
			self.move_timer += 1
			if self.move_to_new_spot == 0:
				self.move_timer = 0
				self.image = self.original_image
				self.flip_sides()
				self.facing_right = True


Phoebe = Player("Phoebe_Right.png")
#Phoebe.image = pygame.transform.flip(Phoebe.image, True, False)

class Zombie(pygame.sprite.Sprite):
	def __init__(self, image, phrase):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image)
		self.original_image = self.image
		self.shot_image = pygame.image.load("Zombie_Shot.png")
		self.feast_image = pygame.image.load("Zombie_Feast.png")
		self.feast_head_back_image = pygame.image.load("Zombie_Feast_Head_Back.png")
		self.walk_a_image = pygame.image.load("Zombie_Walk_A.png")
		self.rect = self.image.get_rect()
		self.alive = True
		self.run_speed = 500
		self.eat_timer = 100
		self.phrase = phrase
		self.phrase_length = len(self.phrase)
		self.eating = False
		self.stacked = False
		self.stack_dy = 0
		self.stacking = 0
		self.spawn_timer = 0
		self.wave_three_status = 0
		self.remain_on_screen = 36
		self.move_timer = 0
		self.text_offset = 0
	def load_fat(self):
		self.shot_image = pygame.image.load("Fat Zombie Shot.png")
		self.feast_image = pygame.image.load("Fat Zombie Eat_A.png")
		self.feast_head_back_image = pygame.image.load("Fat Zombie Eat_B.png")
		self.walk_a_image = pygame.image.load("Fat Zombie Walk.png")
	def load_crawler(self):
		self.shot_image = pygame.image.load("crawler_die.png")
		self.feast_image = pygame.image.load("crawler_eat1.png")
		self.feast_head_back_image = pygame.image.load("crawler_eat2.png")
		self.walk_a_image = pygame.image.load("crawler_run2.png")	
		self.text_offset = 80
		self.flip_sides()
	def get_rect(self):
		return self.rect
	def display_text_bubble(self):
		zombie_word_display = font.render(self.phrase, True, TEXT_COLOR)
		pygame.draw.rect(screen, TEXT_BOX, pygame.Rect(self.rect.x-5, self.rect.y-75+self.text_offset, self.phrase_length * 20, 60))
		pygame.draw.rect(screen, BORDER, (self.rect.x-5, self.rect.y-75+self.text_offset, self.phrase_length*20, 60), 4, border_radius=1)
		screen.blit(zombie_word_display, (self.rect.x, self.rect.y - 65 + self.text_offset))
	def flip_sides(self):
		self.original_image = pygame.transform.flip(self.original_image, True, False)
		self.walk_a_image = pygame.transform.flip(self.walk_a_image, True, False)
		self.feast_image = pygame.transform.flip(self.feast_image, True, False)
		self.feast_head_back_image = pygame.transform.flip(self.feast_head_back_image, True, False)
		self.image = pygame.transform.flip(self.image, True, False)
	def animation(self):
		if (self.move_timer % 12 == 0):
			temp = self.image
			self.image = self.walk_a_image
			self.walk_a_image = temp
	def eat(self):
		global run
		global game_over
		global total_kill_count
		if self.eating == True:
			if self.eat_timer == 100:
				self.image = self.feast_image
				Phoebe.damage(10)
				if (Phoebe.get_health() == 0):
					run = False
					game_over = True
					total_kill_count = Phoebe.kill_count
					sounda1= pygame.mixer.Sound("Defeat.wav")
					sounda1.play()
				self.eat_timer = 0
			else:
				self.eat_timer += 1
				if (self.eat_timer > 35):
					self.image = self.feast_head_back_image
				if (self.eat_timer > 70):
					self.image = self.original_image
				#EAT


	def move_forward(self):
		global game_over
		global run
		global level_wave
		if (abs(Phoebe.rect.center[0] - self.rect.center[0]) > 30):
			if (level_wave == 1):
				self.rect.center = (self.rect.center[0] - (5*self.run_speed), self.rect.center[1])
			if (level_wave == 2):
				self.rect.center = (self.rect.center[0] + (5*self.run_speed), self.rect.center[1])
			if (level_wave == 3):
				if (self.wave_three_status == 1):
					self.rect.center = (self.rect.center[0] - (5*self.run_speed), self.rect.center[1])
				elif (self.wave_three_status == 2):
					self.rect.center = (self.rect.center[0] + (5*self.run_speed), self.rect.center[1])
			self.move_timer += 1
			self.animation()
		else:
			self.eating = True


Castle_Level = Background("Castle.png")
Bridge_Level = Background("Bridge_Background.png")
Forest_Level = Background("Forest.png")
Boss_Level = Background("Boss_Room.png")
Gunshots = ["gunshot1.wav", "gunshot2.wav", "gunshot3.wav", "gunshot4.wav"]
Game_Levels = [Forest_Level, Bridge_Level, Castle_Level, Boss_Level]
Phoebe_Spawns = [(300,480),(300,400),(300,480), (200, 400)]
Zombie_Spawns = [(1060, 480),(1060, 400),(1060, 480)]
Zombie_Left_Spawns = [(200, 480), (200, 400), (200, 480)]
UI = Background("zz.png")
Boss_UI = Background("yy.png")
UI.rect.center = (600, 760)
Boss_UI.rect.center = (600, 760)
Game_Title = Background("Game_Title.png")
Title_Background = Background("Title Background.png")
Title_Background.rect.center = (600, 400)
Game_Title.rect.center = (600, 200)
Play_Button = Button("START GAME")
Play_Button.rect.center = (600, 400)
Title_Sprites = pygame.sprite.Group()
Title_Sprites.add(Title_Background , Game_Title)
Title_Buttons = [Play_Button]
Few_Zombies = Button("Normal")
Some_Zombies = Button("Several")
Some_Zombies.active = True
Some_Zombies.color = ACTIVE_GREEN
Many_Zombies = Button("Nightmare")
Number_of_Zombies_Buttons = [Few_Zombies, Some_Zombies, Many_Zombies]
Slow_Speed = Button("Slow")
Medium_Speed = Button("Medium")
Medium_Speed.active = True
Medium_Speed.color = ACTIVE_GREEN
Intense_Speed = Button("Intense")
Zombie_Speed_Buttons = [Slow_Speed, Medium_Speed, Intense_Speed]
for button in Number_of_Zombies_Buttons:
	button.colinked = True
for button in Zombie_Speed_Buttons:
	button.colinked = True
Few_Zombies.rect.center = (300, 550)
Some_Zombies.rect.center = (600, 550)
Many_Zombies.rect.center = (900, 550)
Slow_Speed.rect.center = (300, 700)
Medium_Speed.rect.center = (600, 700)
Intense_Speed.rect.center = (900, 700)
Few_Zombies.spawn_number = 3
Some_Zombies.spawn_number = 6
Many_Zombies.spawn_number = 10
Slow_Speed.zombie_speed = 0.75
Medium_Speed.zombie_speed = .9
Intense_Speed.zombie_speed = 1.05
Backgrounds = pygame.sprite.Group()
Backgrounds.add(Forest_Level)
Enemy_List = []
Characters = pygame.sprite.Group()
Enemies = pygame.sprite.Group()
Beatrice = Final_Boss("Beatrice.png")
Final_Boss = pygame.sprite.Group()
Final_Boss.add(Beatrice)
Characters.add(Phoebe, UI)
Enemies.add()
Phoebe.rect.center = (300, 480)
Beatrice.rect.center = (1000, 400)
BossBoxes = []
sounda2= pygame.mixer.Sound("TitleScreen.wav")
sounda2.play(loops =-1)

while (title_screen):
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			title_screen = False
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				current_stage = 3
				sounda3= pygame.mixer.Sound("BossFight.wav")
				sounda3.play()
				title_screen = False
				Characters.empty()
				Characters.add(Phoebe, Boss_UI)
				Backgrounds.empty()
				Backgrounds.add(Game_Levels[current_stage])
				Phoebe.rect.center = (Phoebe_Spawns[current_stage])
				Phoebe.new_level()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if (Play_Button.rect.collidepoint(pygame.mouse.get_pos())):
				gunshot_sound = mixer.Sound("BeatriceShot.wav")
				gunshot_sound.play()
				title_screen = False
				sounda4= pygame.mixer.Sound("Forest.wav")
				sounda4.play()
				#TEMP CODE
				for button in Number_of_Zombies_Buttons:
					if button.active == True:
						number_of_zombies = button.spawn_number
						number_of_zombies_setting = button.text
						level_spawn_timer = number_of_zombies * spawning_pool # Desired Zombies * Spawn Rate * Level Wave??
				for button in Zombie_Speed_Buttons:
					if button.active == True:
						zombie_speed = button.zombie_speed
			for button in Number_of_Zombies_Buttons:
				if (button.rect.collidepoint(pygame.mouse.get_pos())):
					button.active = True
					button.color = ACTIVE_GREEN
					gunshot_sound = mixer.Sound(Gunshots[random.randint(0,3)])
					gunshot_sound.play()
					for other_button in Number_of_Zombies_Buttons:
						if button != other_button:
							other_button.active = False
							other_button.color = BUTTON_GREY
			for button in Zombie_Speed_Buttons:
				if (button.rect.collidepoint(pygame.mouse.get_pos())):
					button.active = True
					button.color = ACTIVE_GREEN
					gunshot_sound = mixer.Sound(Gunshots[random.randint(0,3)])
					gunshot_sound.play()
					for other_button in Zombie_Speed_Buttons:
						if button != other_button:
							other_button.active = False
							other_button.color = BUTTON_GREY
	screen.fill(BLACK)
	Title_Sprites.update()
	Title_Sprites.draw(screen)
	tips_display1 = font.render("Hit Two Spaces", True, TIPS)
	tips_display2 = font.render("or Press Enter ", True, TIPS)
	tips_display3 = font.render("to Clear Your Input", True, TIPS)
	screen.blit(tips_display1, (30, 320))
	screen.blit(tips_display2, (30, 360))
	screen.blit(tips_display3, (30, 400))
	for button in Title_Buttons:
		button.update()
		button.draw()
	number_of_zombies_option = font.render("Amount of Zombies: ", True, RED)
	screen.blit(number_of_zombies_option, (450, 450))
	zombie_speed_option = font.render("Zombie Speed: ", True, RED)
	screen.blit(zombie_speed_option, (450, 600))
	for button in Number_of_Zombies_Buttons:
		button.update()
		button.draw()
	for button in Zombie_Speed_Buttons:
		button.update()
		button.draw()
	pygame.display.flip()
	clock.tick(FPS)
while (run):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				gunshot_words = ""
				gunshot_word_display = font.render(gunshot_words, True, RED)
			if event.key == pygame.K_BACKSPACE:
				pass
			else:
				if event.unicode.islower() or event.unicode.isupper() or event.unicode.isdigit() or event.unicode == ',' or event.unicode == "?" or event.unicode == " " or event.unicode == "'" or event.unicode == "-":
					gunshot_words += event.unicode
					for box in BossBoxes:
						if gunshot_words == box.text:
							Phoebe.bang_timer = 30
							Phoebe.image = Phoebe.bang
							BossBoxes.remove(box)
							gunshot_words = ""
							Phoebe.kill_count += 1
							gunshot_sound = mixer.Sound(Gunshots[random.randint(0,3)])
							gunshot_sound.play()
					for zombie in Enemies:
						if gunshot_words == zombie.phrase:
							Phoebe.bang_timer = 30
							Phoebe.image = Phoebe.bang
							zombie.alive = False
							zombie.image = zombie.shot_image
							if (zombie.rect.center[0] < Phoebe.rect.center[0]):
								zombie.flip_sides()
								zombie.remain_on_screen = -36
							zombie.rotation_pivot = zombie.image
							Phoebe.kill_count += 1
							gunshot_sound = mixer.Sound(Gunshots[random.randint(0,3)])
							gunshot_sound.play()
							aftershock_words = gunshot_words
							gunshot_words = ""
							if (level_wave == 3 and Phoebe.rect.center[0] < zombie.rect.center[0] and Phoebe.facing_right == False):
								Phoebe.flip_sides()
								Phoebe.facing_right = True
							if (level_wave == 3 and Phoebe.rect.center[0] > zombie.rect.center[0] and Phoebe.facing_right == True):
								Phoebe.flip_sides()
								Phoebe.facing_right = False
								
				gunshot_word_display = font.render(gunshot_words, True, RED)
	pressed = pygame.key.get_pressed()
	if pressed[pygame.K_BACKSPACE]:
		if backspace_delay == 0:
			gunshot_words = gunshot_words[:-1]
			gunshot_word_display = font.render(gunshot_words, True, RED)
			backspace_delay = 2
		else:
			backspace_delay -= 1
	screen.fill(BLACK)
	Backgrounds.update()
	Backgrounds.draw(screen)
	Characters.update()
	Characters.draw(screen)

	
	
	zombie_stack = -1
	stacked_zombies = []
	level_spawn_timer -= 1
	if (number_of_zombies_setting == "Normal"):
		boss_spawn_timer -= 1
	if (number_of_zombies_setting == "Several"):
		boss_spawn_timer -= 2
	if (number_of_zombies_setting == "Nightmare"):
		boss_spawn_timer -= 2.5
	if Phoebe.bang_timer > 0:
		Phoebe.bang_timer -= 1
		if (Phoebe.bang_timer == 0):
			Phoebe.image = Phoebe.original_image
	if Beatrice.bang_timer > 0:
		Beatrice.bang_timer -= 1
		if (Beatrice.bang_timer == 0):
			Beatrice.image = Beatrice.original_image
	if (boss_spawn_timer % boss_speed == 0 and current_stage == 3):
		New_Boss_Phrase = BossTextBox(boss_words[(random.randint(0, len(boss_words)-1))])
		BossBoxes.insert(0, New_Boss_Phrase)
	if (current_stage == 3):
		if Phoebe.kill_count == 13:
			run = False
			victory = True
			total_kill_count += Phoebe.kill_count
			sounda= pygame.mixer.Sound("Victory.wav")
			sounda.play()
		for box in BossBoxes:
			box.display_text()
			box.rise(zombie_speed*1.55)
			if (box.get_y() < 90):
				BossBoxes.remove(box)
				Beatrice.bang_timer = 30
				Beatrice.image = Beatrice.bang
				gunshot_sound = mixer.Sound("BeatriceShot.wav")
				gunshot_sound.play()
				Phoebe.damage(20)
				if (Phoebe.health <= 0):
					run = False
					game_over = True
					sounda5= pygame.mixer.Sound("Defeat.wav")
					sounda5.play()
	if (level_spawn_timer % spawning_pool == 0 and level_spawn_timer > -1 and current_stage != 3):
		zombie_type = random.randint(0,15)
		if (zombie_type <= 6):
			New_Zombie = Zombie("Zombie 1.png", zombie_words[(random.randint(0, len(zombie_words)-1))])
			New_Zombie.run_speed = zombie_speed
		elif (zombie_type > 6 and zombie_type <= 8):
			New_Zombie = Zombie("Fat Zombie.png", zombie_adjectives[(random.randint(0, len(zombie_adjectives)-1))].capitalize() + " " + zombie_nouns[(random.randint(0, len(zombie_nouns)-1))].capitalize())
			New_Zombie.load_fat()
			New_Zombie.run_speed = zombie_speed*.35
		else:
			New_Zombie = Zombie("crawler_run1.png", zombie_tiny[(random.randint(0, len(zombie_tiny)-1))])
			New_Zombie.load_crawler()
			New_Zombie.run_speed = zombie_speed* 1.25
		Enemy_List.insert(0, New_Zombie)
		Enemies.add(New_Zombie)
		if current_stage != 3:
			if level_wave == 1:
				New_Zombie.rect.center = Zombie_Spawns[current_stage]
			elif level_wave == 2:
				New_Zombie.rect.center = Zombie_Left_Spawns[current_stage]
				New_Zombie.flip_sides()
			elif level_wave == 3:
				if wave_three_rotating_sides %2 == 0:
					New_Zombie.rect.center = Zombie_Spawns[current_stage]
					wave_three_rotating_sides += 1
					New_Zombie.wave_three_status = 1
				elif wave_three_rotating_sides %2 == 1:
					New_Zombie.rect.center = Zombie_Left_Spawns[current_stage]
					New_Zombie.flip_sides()
					wave_three_rotating_sides += 1
					New_Zombie.wave_three_status = 2
	for zombie in Enemy_List:
		if zombie.alive == True:
			zombie.move_forward()
			zombie.display_text_bubble()
			zombie.eat()
		elif zombie.alive == False:
			if zombie.remain_on_screen > 0:
				zombie.remain_on_screen -= 1
				zombie.image = pygame.transform.rotate(zombie.rotation_pivot, 10 * (36-zombie.remain_on_screen))
				zombie.image = pygame.transform.scale(zombie.image, (zombie.remain_on_screen*6, zombie.remain_on_screen*6))
			elif zombie.remain_on_screen < 0:
				zombie.remain_on_screen += 1
				zombie.image = pygame.transform.rotate(zombie.rotation_pivot, - 10 * (36+zombie.remain_on_screen))
				zombie.image = pygame.transform.scale(zombie.image, (-zombie.remain_on_screen*6, -zombie.remain_on_screen*6))

			if zombie.remain_on_screen == 0:
				Enemies.remove(zombie)
	if (Phoebe.kill_count == number_of_zombies * level_wave and wave_two_started == False and current_stage != 3):
		wave_two_started = True
		Phoebe.move_to_new_spot = 70
		level_wave += 1
		level_spawn_timer = number_of_zombies * spawning_pool # Desired Zombies * Spawn Rate * Level Wave??
	if (Phoebe.kill_count == number_of_zombies * level_wave and wave_three_started == False and current_stage != 3):
		wave_three_started = True
		Phoebe.move_to_new_spot = -40
		level_wave += 1
		level_spawn_timer = number_of_zombies * spawning_pool * 2# Desired Zombies * Spawn Rate * Level Wave??
	if (Phoebe.kill_count == number_of_zombies * 4 and current_stage != 3):
		wave_two_started = False
		wave_three_started = False
		total_kill_count += Phoebe.kill_count
		Phoebe.kill_count = 0
		level_wave = 1
		level_spawn_timer = number_of_zombies * spawning_pool
		current_stage += 1
		if (current_stage == 1):
			sounda6= pygame.mixer.Sound("Bridge.wav")
			sounda6.play()
		if (current_stage == 2):
			sounda7= pygame.mixer.Sound("Castle.wav")
			sounda7.play()
		if (current_stage == 3):
			sounda8= pygame.mixer.Sound("BossFight.wav")
			sounda8.play()
			Characters.empty()
			Characters.add(Phoebe, Boss_UI)
			Backgrounds.empty()
			Backgrounds.add(Game_Levels[current_stage])
			Phoebe.rect.center = (Phoebe_Spawns[current_stage])
			Phoebe.new_level()
		if (current_stage == 4):
			run = False
			game_over = False
			victory = True
			sounda9= pygame.mixer.Sound("Victory.wav")
			sounda9.play()
			#WIN SCREEN
		else:
			Backgrounds.empty()
			Backgrounds.add(Game_Levels[current_stage])
			Phoebe.rect.center = (Phoebe_Spawns[current_stage])
			Phoebe.new_level()
	Enemies.update()
	Enemies.draw(screen)
	#Characters.OrderedUpdates()
	if (current_stage != 3):
		chunks = gunshot_words.split(' ', 1)
		if len(chunks) >= 1:
			gunshot_word_display = font.render("~ " + chunks[0], True, RED)
			screen.blit(gunshot_word_display, (10, 720))
		if len(chunks) == 2:
			gunshot_word_display_two = font.render("~ " + chunks[1], True, RED)
			screen.blit(gunshot_word_display_two, (10, 760))
		spaces = 0
		for i in range (0, len(gunshot_words)):
			if gunshot_words[i] == ' ':
				spaces += 1
		if spaces >= 2:
			gunshot_words = ""
	else:
		gunshot_word_display = font.render("~ " + gunshot_words, True, RED)
		screen.blit(gunshot_word_display, (10,720))
	Phoebe.new_wave()
	Phoebe.display_health()
	if (current_stage == 3):
		Final_Boss.update()
		Final_Boss.draw(screen)
	#Line for text entry
	pygame.draw.rect(screen, BLUE, pygame.Rect(0, 690, 1200, 30))
	pygame.display.flip()
	clock.tick(FPS)
while (game_over == True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			game_over = False
	screen.fill(BLACK)
	game_over_display = font.render("GAME OVER", True, RED)
	screen.blit(game_over_display, (505, 365))
	kill_count_display = font.render("KILL COUNT: " + str(total_kill_count), True, RED)
	screen.blit(kill_count_display, (505, 425))
	pygame.display.flip()
	clock.tick(FPS)
while (victory == True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			victory = False
	screen.fill(BLACK)
	game_over_display = font.render("VICTORY!", True, RED)
	screen.blit(game_over_display, (470, 320))
	kill_count_display = font.render("KILL COUNT: " + str(total_kill_count), True, RED)
	screen.blit(kill_count_display, (470, 380))
	pygame.display.flip()
	clock.tick(FPS)


