import pygame
import time
import json
import pandas as pd
import random
import numpy as np

class App:

	def __init__(self, specs=(1280,720), population_size=100, apple_population=25, apple_time=0.5, apple_max=100, kids_amount=3):

		pygame.init()
		self.font = pygame.font.Font(None, 30)
		self.creature_font = pygame.font.Font(None, 60)
		self.specs = specs
		self.colors = Colors
		self.population_size = population_size
		self.kids_amount = kids_amount
		self.apple_population = apple_population
		self.screen = pygame.display.set_mode(self.specs)
		self.running = True
		self.clock = pygame.time.Clock()
		self.all_players = np.zeros(self.population_size, dtype=object)
		self.all_apples = np.zeros(self.apple_population, dtype=object)

		self.apple_time = apple_time
		self.apple_now = 75
		self.apple_max = apple_max
		self.apple_image = pygame.image.load('apple.png').convert_alpha()
		self.start_game_time = time.time()
		for idx, x in enumerate(self.all_players):

			#eerste is de goede tweede was eentje waar de populatie makkelijker overleeft
			#self.all_players[idx] = Player(random.randint(2,10), random.randint(2,6), random.randint(5, 20), idx, self.screen)
			size = random.randint(5,20)
			speed = random.randint(2,4)
			expiration = random.randint(10, 25)
			self.all_players[idx] = Player(size, speed, expiration, idx, self.screen, self.specs, True, size, expiration, speed)

		for idx, x in enumerate(self.all_apples):

			self.all_apples[idx] = Apple(20, self.specs)

	def slidebar(self, size, pos):

		
		slide_fill_size = (self.apple_time-0.5) * 48
		self.screen.fill(Colors.red, (pos, (slide_fill_size, size[1])))
		pygame.draw.rect(self.screen, self.colors.black, (pos, size), 4)


	def game_running(self):

		apple_new_time = time.time()
		selectedplayer = 0
		no_select = True
		previous_time = time.time()
		while self.running:

			for event in pygame.event.get():

				if event.type == pygame.QUIT:

					self.running = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_LEFT:
						if self.apple_time > 0.2: 
							self.apple_time -= 0.1
					if event.key == pygame.K_RIGHT:
						if self.apple_time < 3:
							self.apple_time += 0.1
					if event.key == pygame.K_DOWN:
						if self.apple_now > 5: 
							self.apple_now -= 1
					if event.key == pygame.K_UP:
						if self.apple_now < self.apple_max:
							self.apple_now += 1


			self.deltatime = time.time() - previous_time
			previous_time = time.time()
				
			self.screen.fill(self.colors.white)
			self.new_players = self.all_players[:]
			gensize = 0
			one_gen = True

			
			rem_index_player = []
		    
			
			for idx,player in enumerate(self.all_players):

					if idx == 0:

						first_id = player.id

					if player.id != first_id:

						one_gen = False

					gensize +=1
					self.new_apples = self.all_apples[:]
					r_player = player.movement(self.deltatime)
					if r_player.collidepoint(pygame.mouse.get_pos()):
						if selectedplayer != player:
							selectedplayer = player
							no_select = False

						
					if time.time() - player.start_time > player.expiration:
						#print(self.new_players)
						if player == selectedplayer:
							no_select = True
						rem_index_player.append(idx)
						

					rem_index_apple = []
					for a_idx,apple in enumerate(self.all_apples):

						

							#apple_fill = self.screen.fill(Colors.lime, apple.apple_rect)
							#apple_outline = pygame.draw.rect(self.screen, Colors.black, apple.apple_rect, 1)
							apple_im = self.screen.blit(self.apple_image, (apple.x, apple.y))
							collision = apple.collision(r_player)

							if collision == True:

								rem_index_apple.append(a_idx)

								if player.fertile == True:

									fertile_kid = GeneticAlgorithm(self.new_players[idx].size, self.new_players[idx].speed, self.new_players[idx].expiration, self.new_players[idx].id, True, self.new_players[idx].sec_size, self.new_players[idx].sec_speed, self.new_players[idx].sec_expiration, self.screen, self.specs)
									not_fertile_kid = GeneticAlgorithm(self.new_players[idx].sec_size, self.new_players[idx].sec_speed, self.new_players[idx].sec_expiration, self.new_players[idx].id, False, self.new_players[idx].sec_size, self.new_players[idx].sec_speed, self.new_players[idx].sec_expiration, self.screen, self.specs)

									for x in range(self.kids_amount):
										
										new_figure = fertile_kid.mutation()
										new_figure.x = self.new_players[idx].x
										new_figure.y = self.new_players[idx].y
										new_figure.color = self.new_players[idx].color
										self.new_players = np.append(self.new_players, [new_figure]) # I have to apply here the genetic algorithm here where they get 2 kids
									
									for x in range(self.kids_amount):
										
										new_figure = not_fertile_kid.mutation()
										new_figure.x = self.new_players[idx].x
										new_figure.y = self.new_players[idx].y
										new_figure.color = self.new_players[idx].color
										self.new_players = np.append(self.new_players, [new_figure])

									rem_index_player.append(idx)
									if player == selectedplayer:
										selectedplayer = self.new_players[-1]
									break

					

					self.new_apples = np.delete(self.new_apples, rem_index_apple)
					self.all_apples = self.new_apples[:]
			
			self.new_players = np.delete(self.new_players, rem_index_player)
			self.all_players = self.new_players[:]
			#print(len(self.all_players), ' is after the slicing')
			slidesize = (120,20)
			slidepos = (670,40)

			self.slidebar(slidesize,slidepos)

			
			if len(self.all_players) == 0:

				text = self.creature_font.render((f"All the creatures are dead"), True, Colors.blue)
				self.screen.blit(text, (160, 280))

			if time.time()-apple_new_time > self.apple_time:

				if len(self.all_apples) < self.apple_now:

					self.all_apples = np.append(self.all_apples, np.array([Apple(20, self.specs)]))
					
					apple_new_time = time.time()

			self.clock.tick(60)
			if no_select == False:
				try:
					pygame.draw.rect(self.screen, self.colors.red, (selectedplayer.x, selectedplayer.y, selectedplayer.size, selectedplayer.size), 3)
					text = self.font.render((f"Id: {selectedplayer.id}, size: {round(selectedplayer.size, 1)}"), True, Colors.red)
					self.screen.blit(text, (530, 66))
					text2 = self.font.render((f"Speed:{round(selectedplayer.speed, 1)}, expiration:{round(selectedplayer.expiration,1)}"), True, Colors.red)
					self.screen.blit(text2, (530, 92))
					text2 = self.font.render((f"Fertility: {selectedplayer.fertile}"), True, Colors.red)
					self.screen.blit(text2, (530, 118))
				except:
					pass
			
			text = self.font.render((f"Only 1 generation left: {one_gen}"), True, Colors.red)
			self.screen.blit(text, (980, 16))
			text = self.font.render((f"SpawnMax: {round(self.apple_now, 1)} apples"), True, Colors.red)
			self.screen.blit(text, (530, 16))
			text = self.font.render((f"Spawn: {round(self.apple_time, 1)} s"), True, Colors.red)
			self.screen.blit(text, (530, 42))
			text = self.font.render((f"Apple amount: {len(self.all_apples)} apples"), True, Colors.red)
			self.screen.blit(text, (980, 42))
			fps = str(int(self.clock.get_fps()))
			text = self.font.render((f"Gensize: {gensize}"), True, Colors.red)
			self.screen.blit(text, (20, 40))
			text = self.font.render((f"FPS: {fps}"), True, Colors.red)
			self.screen.blit(text, (20, 20))
			text = self.font.render((f"Time passed: {round(time.time() - self.start_game_time, 1)} s"), True, Colors.red)
			self.screen.blit(text, (20, 60))
			pygame.display.flip()

class Player:

	def __init__(self, size, speed, expiration, pl_id, screen, specs, fertile, sec_size, sec_expiration, sec_speed):

		self.start_time = time.time()

		self.speed = speed
		self.expiration = expiration
		self.size = size
		self.fertile = fertile

		self.color = Colors().random_color()
		self.id = pl_id

		self.sec_size = sec_size
		self.sec_expiration = sec_expiration
		self.sec_speed = sec_speed
		
		self.specs = specs
		self.screen = screen

		self.x = random.randint(0, self.specs[0]-int(self.size))
		self.y = random.randint(0, self.specs[1]-int(self.size))

	def movement(self, deltatime):


		n_loop = deltatime / 0.01

		n_loop = int(n_loop)


		for x in range(n_loop):

			directionx = random.randint(-1,1)
			directiony = random.randint(-1,1)

			if directionx > 0:
	 
				self.x +=  (self.speed)
				if self.x> self.specs[0]-self.size:
					self.x = self.specs[0]-self.size
				

			elif directionx < 0:

				self.x-= (self.speed )
				if self.x< 0:
					self.x= 0
				

			if directiony > 0:

				self.y += (self.speed)
				if self.y > self.specs[1]-self.size:
					self.y = self.specs[1]-self.size
				
			elif directiony < 0:

				self.y -= (self.speed )
				if self.y < 0:
					self.y = 0
				

		self.player_rect = pygame.Rect(self.x, self.y, self.size, self.size)

		return pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.size, self.size)) 

class Apple:

	def __init__(self, size, specs):

		self.specs = specs
		self.size = size
		self.x = (random.randint(0,self.specs[0]-self.size))
		self.y = (random.randint(0, self.specs[1]-self.size))
		self.apple_rect = pygame.Rect((self.x, self.y), (self.size, self.size))

	def collision(self, player_rect):

		

		if self.apple_rect.colliderect(player_rect):

				return True

class GeneticAlgorithm:

	def __init__(self, size, speed, expiration, pl_id, fertile, sec_size, sec_speed, sec_expiration, screen, specs):

		self.size = size
		self.speed = speed
		self.id = pl_id
		self.expiration = expiration
		self.screen = screen
		self.specs = specs
		self.fertile = fertile
		self.sec_size = sec_size
		self.sec_speed = sec_speed
		self.sec_expiration = sec_expiration

	def mutation(self):

		if random.randint(1,3) == 2:
			self.size += random.randint(-(int(self.size)), int(self.size))/10

		if random.randint(1,3) == 2:
			self.speed += random.randint(-(int(self.speed)), int(self.speed))/10

		if random.randint(1,3) == 2:
			self.expiration += random.randint(-(int(self.expiration)), int(self.expiration))/10

		return Player(self.size, self.speed, self.expiration, self.id, self.screen, self.specs, self.fertile, self.sec_size, self.expiration, self.sec_speed)





class Colors:
    
	white = (255, 255, 255)
	blue  = (0,0,255)
	red = (255,0,0)
	lime = (0,255,0)
	yellow = (255,215,0)
	orange = (255,165,0)
	turquasie = (0, 255,255)
	purple = (255,0,255)
	black = (0,0,0)
	magenta = (255,0,255)
	maroon = (128,0,0)
	olive = (128,128,0)
	green = (0,128,0)
	navy = (0,0,128)
	teal = (0,128,128)
	purple = (128,0,128)
	silver = (192,192,192)

	def random_color(self):

		return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

if __name__ == '__main__':

	print('you have to create another file that calls all these objects')