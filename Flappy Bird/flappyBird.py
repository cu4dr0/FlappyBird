import pygame
import neat
import time
import os
import random

WIN_WIDTH = 570
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),\
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),\
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bgshorter.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "floor.png")))

GEN = 0

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROTATION_VELO = 20
	ANIMATION_TIME = 5

	def __init__(self, xPos, yPos):
		self.x = xPos
		self.y = yPos
		self.tilt = 0
		self.tickCount = 0
		self.velo = 0
		self.height = self.y
		self.imgCount = 0
		self.img = self.IMGS[0]

	def jump(self):
		self.velo = -10.5
		self.tickCount = 0 
		self.height = self.y 

	def move(self):
		self.tickCount += 1
		d = self.velo + self.tickCount + 1.5*self.tickCount**2 #physics opperation
		if d >= 16: #if reached the top down velocity, keep that way
			d = 16
		if d < 0:
			d -=2
		self.y += d
		if d <0 or self.y < self.height +50: #upwards animation (play with the numbers)
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt > -90:
				self.tilt -= self.ROTATION_VELO 

	def draw(self, win):
		self.imgCount +=1	
		#animation of bird flapping it's wings (play with the numbers)
		if self.imgCount < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.imgCount < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.imgCount < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.imgCount < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.imgCount < self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.imgCount = 0
		if self.tilt <= -80: #if going downwards then stay in one image
			self.img = self.IMGS[1]
			self.imgCount = self.ANIMATION_TIME * 2 #when it's back up it will start with it's actual animation
		#rotates the image around the center
		rotatedImage = pygame.transform.rotate(self.img, self.tilt)
		newRectangule = rotatedImage.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotatedImage, newRectangule.topleft)

	def getMask(self):
		return pygame.mask.from_surface(self.img)

class Pipe:
	GAP = 200
	VELO = 5
	def __init__(self, x):
		self.x = x
		self.height = 0
		self.top = 0
		self.bot = 0
		#images
		self.PIPE_BOTTOM = PIPE_IMG 
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #or get an image upside down and just create it as PIPE_BOTTOM
		self.passed = False
		self.setHeight()

	def setHeight(self):
		self.height = random.randrange(50,450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bot = self.height + self.GAP
	def move(self):
		self.x -= self.VELO

	def draw(self, win):
		win.blit(self.PIPE_TOP,(self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bot))

	def collide(self, bird):
		birdMask = bird.getMask()
		topMask = pygame.mask.from_surface(self.PIPE_TOP)
		botMask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		topOffset = (self.x - bird.x, self.top - round(bird.y))
		botOffset = (self.x - bird.x, self.bot - round(bird.y))

		botPoint = birdMask.overlap(botMask, botOffset)
		topPoint = birdMask.overlap(topMask, topOffset)
		if botPoint or topPoint: #they're not None
			return True
		return False
class Base:
	VELO = 5 #same as pipe
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VELO
		self.x2 -= self.VELO
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH
		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))

def drawWindow(win, birds, pipes, base, score, gen):
	win.blit(BACKGROUND_IMG, (0,0))
	for pipe in pipes:
		pipe.draw(win)
	text = STAT_FONT.render("Score:"+str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 25 - text.get_width(), 5)) #25 for space for another number, 5 for size 
	text = STAT_FONT.render("Gen:"+str(gen), 1, (255,255,255))
	win.blit(text, (10,5)) 
	base.draw(win)
	for bird in birds:
		bird.draw(win)
	pygame.display.update()	

def fitAndPlay(genomes, config):
	global GEN
	GEN +=1
	baseHeight = 670
	spaceBetweenPipes = 600
	birdXPos = 230
	birdYPos = 250
	animationSpeed = 30 #fps

	nets = []
	geno = []
	birds = []

	for _,g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(birdXPos, birdYPos))
		g.fitness = 0
		geno.append(g)
	base = Base(baseHeight) #put it as you please
	pipes = [Pipe(spaceBetweenPipes)] #change if want to spawn them more close to each other
	run = True
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()
	score = 0

	while run:
		clock.tick(animationSpeed)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()


		pipe_indx = 0
		if len(birds) > 0: #if the bird passed the first pipe then look for the next one
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_indx = 1
		else: #no birds left
			run = False
			break
		for x, bird in enumerate(birds): #encourage the bird to stay alive
			bird.move()
			geno[x].fitness += 0.1
			#										distance between top pipe and bird 			distance between bot pipe and bird
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_indx].height), abs(bird.y - pipes[pipe_indx].bot)))
			if output[0] > 0.5:
				bird.jump()
		addPipe = False
		rem = []
		#checks birds and pipes if they collide
		for pipe in pipes:
			for x, bird in enumerate(birds): 
				if pipe.collide(bird):
					geno[x].fitness -= 1
					birds.pop(x)
					nets.pop(x)
					geno.pop(x)
				if not pipe.passed and pipe.x < bird.x: #if the bird hasn't passed the pipe
					pipe.passed = True
					addPipe = True
			if pipe.x + pipe.PIPE_TOP.get_width() < 0: #it's off screen
				rem.append(pipe)
			pipe.move()
		if addPipe: #reward the bird for pass the pipe
			for g in geno:
				g.fitness +=5 
			score+= 1
			pipes.append(Pipe(spaceBetweenPipes))
		for r in rem:
			pipes.remove(r)
		for x,bird in enumerate(birds): 
			if bird.y + bird.img.get_height() >= baseHeight or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				geno.pop(x)

		base.move()
		drawWindow(win,birds, pipes, base, score, GEN)

def run(configPath):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,\
	configPath)
	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(fitAndPlay, 50)
	#save the winner as a pickle file
	#if never ends then put a breakpoint whenever you reach certain score
	#learn how to load what "winner" returns

if __name__ == "__main__":
	localDir = os.path.dirname(__file__)
	configPath = os.path.join(localDir, "neatConfig.txt")
	run(configPath)