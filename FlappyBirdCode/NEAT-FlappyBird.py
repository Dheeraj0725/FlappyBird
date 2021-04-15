import pygame #python game module
import random #used for randomizing the pipes
import os #used for setting up path for pickle file 
import time #python module for time
import neat #NEAT algorithm module 
import pickle #module to include pickle file


pygame.font.init()  # init font

#Window specifications
WIN_WIDTH = 600 #window screen width size
WIN_HEIGHT = 800 #window screen height size
FLOOR = 730 # size of floor

#fonts in pygame
STAT_FONT = pygame.font.SysFont("comicsans", 50) #font style
END_FONT = pygame.font.SysFont("comicsans", 70) #font style

DRAW_LINES = True #draw lines from each bird to top and bottom of the pipe

#Display options of window
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #display pygame window wrt to given width and height
pygame.display.set_caption("Flappy Bird") #Window caption

#Loading images 
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha()) #pipe img
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900)) #background img
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)] #bird images
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha()) #base img

gen = 0 #generation of birds = 0


class Bird:
    """
    Bird class representing the flappy bird
    """

    MAX_ROTATION = 25 #max rotation of bird 
    IMGS = bird_images #images used 
    ROT_VEL = 20 #speed at which rotation of bird takes place
    ANIMATION_TIME = 5 #animation of birds wings flapping

    def __init__(self, x, y):
        """
        Initializing the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """

        self.x = x #starting x pos of bird
        self.y = y #starting y pos of bird
        self.tilt = 0  # starting tilt of bird
        self.tick_count = 0 #bird jump and fall physics
        self.vel = 0 #velocity of bird at start
        self.height = self.y #tilt and moving of bird
        self.img_count = 0 #image shown for the bird
        self.img = self.IMGS[0] #referencing of bird images

    def jump(self):
        """
        making the bird jump
        :return: None
        """

        self.vel = -10.5 #velocity of the bird for jumping
        self.tick_count = 0 #keeps track of last jump for keeping track of jump and fall of bird
        self.height = self.y #original height and starting point of bird

    def move(self):
        """
        making the bird move
        :return: None
        """

        self.tick_count += 1 #keeping tack of how much bird moved with regard to last jump

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculating displacement i.e., movement of bird up and down

        # terminal velocity i.e., velocity of bird capped to a value so that bird doesnot move very fast in either direction 
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        
        #jump value or jump height
        if displacement < 0: 
            displacement -= 2

        self.y = self.y + displacement #moving bird slowly up or down

        if displacement < 0 or self.y < self.height + 50:  # tilting up the bird
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilting down of bird
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        drawing the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[0]
            self.img_count = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


# Class for all pipe related objects
class Pipe():
    """
    represents a pipe object
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        initializing pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x #location of pipe in x
        self.height = 0 #height of pipe at start of initialization

        #where the top and bottom of the pipe at initialization
        self.top = 0 # Location of top pipe at start 
        self.bottom = 0 # Location of bottom pipe at start 

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True) #rotating of pipe image for top pipe
        self.PIPE_BOTTOM = pipe_img # pipe image

        self.passed = False #check if bird has already passed a pipe

        self.set_height() # height of pipe

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450) #randomizing top and bottom of pipe
        self.top = self.height - self.PIPE_TOP.get_height() #location of top of a pipe
        self.bottom = self.height + self.GAP #location of bottom pipe

    def move(self):
        """
        moving pipe based on vel
        :return: None
        """
        self.x -= self.VEL #velocity of pipe moving wrt to FPS of game

    def draw(self, win):
        """
        drawing top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        win.blit(self.PIPE_TOP, (self.x, self.top)) #draw top pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom)) #draw bottom pipe


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask() #masking bird
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) #masking top pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) #masking bottom pipe
        top_offset = (self.x - bird.x, self.top - round(bird.y)) #offset from bird_mask to top_mask
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) #offset from bird_mask to bottom_mask

        b_point = bird_mask.overlap(bottom_mask, bottom_offset) #checking for pixel collision of bird_mask and bottom pipe(offset of bottom pipe)
        t_point = bird_mask.overlap(top_mask,top_offset) #checking for picel collision of bird_mask and top pipe(offset of top pipe)

        if b_point or t_point: #checking for collision and overlapping of pixels
            return True
            

        return False

class Base:
    """
    Represnting the moving floor of the game
    """
    VEL = 5 #velocity of base moving
    WIDTH = base_img.get_width() #width of base
    IMG = base_img #base img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y #starting pos of base
        self.x1 = 0 #pos of x
        self.x2 = self.WIDTH # width of base

    def move(self):
        """
        moving floor 
        :return: None
        """
        self.x1 -= self.VEL 
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Drawing floor. 
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1                                                                 # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win): #checking for collision of bird with pipe
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: #remove pipe when it passes a certain location on screen
                rem.append(pipe) #removing pipe 

            if not pipe.passed and pipe.x < bird.x: #check if bird has passes the pipe
                pipe.passed = True #check if bird is passed a pipe
                add_pipe = True #if pipe is passed by bird we add a new pipe

        if add_pipe: #adding new pipes
            score += 1 #adding score when bird passes through a pipe
            for genome in ge:
                genome.fitness += 5 #increase fitness when bird passes a pipe
            pipes.append(Pipe(WIN_WIDTH)) #adding new pipe on window

        for r in rem: #remove pipe when a bird passes through it
            pipes.remove(r)

        for bird in birds: #checking if bird hits floor, bird dies
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # break generation score gets large enough and put best bird in pickle file
        '''
        if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break
        '''


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Creating the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Adding a reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. 
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)