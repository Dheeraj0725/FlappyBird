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
FLOOR = 700 # size of floor

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

    MAX_ROTATION = 25 #max rotation of bird when going up or down {25 degrees}
    IMGS = bird_images #images used 
    ROT_VEL = 20 #speed at which rotation of bird takes place
    ANIMATION_TIME = 5 # How long our bird will flap its wings. Animation of birds wings flapping

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
        self.tick_count = 0 #bird jump and fall 
        self.vel = 0 #velocity of bird at start
        self.height = self.y #tilt and moving of bird
        self.img_count = 0 # Which image of bird is currently being shown{used for animation}
        self.img = self.IMGS[0] #referencing of bird images

    def jump(self):
        """
        making the bird jump
        :return: None
        """

        self.vel = -10.5 #velocity of the bird for jumping
        self.tick_count = 0 #keeps track of last jump for keeping track of jump and fall of bird
        self.height = self.y #original starting point of bird or where the bird jumped from 

    def move(self):
        """
        making the bird move
        :return: None
        """

        self.tick_count += 1 #keeping tack of how much bird moved with regard to last jump or starting

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculating displacement i.e., movement of bird up and down

        # terminal velocity i.e., velocity of bird capped to a value so that bird doesnot move very fast in either direction 
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        
        #jump value or jump height
        if displacement < 0: 
            displacement -= 2

        self.y = self.y + displacement # Change y position based on displacement. moving bird slowly up or down

        # tiltiing of bird is based on displacement. 
        if displacement < 0 or self.y < self.height + 50:  # d < 0 or self.y is bird moving up. Tilting up the bird
            if self.tilt < self.MAX_ROTATION: # for tilt angle of 25 
                self.tilt = self.MAX_ROTATION # if yes then tilt bird by 25 directly
        else:  # tilting down of bird
            if self.tilt > -90: # rotate bird directly by 90 degrees.
                self.tilt -= self.ROT_VEL #looks like bird is nose diving

    def draw(self, win):
        """
        drawing the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1 # How many times game loop is running.

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME: # img_count < 5
            self.img = self.IMGS[0] # display bird 1 image
        elif self.img_count <= self.ANIMATION_TIME*2: # img_count < 10
            self.img = self.IMGS[1] # display bird 2
        elif self.img_count <= self.ANIMATION_TIME*3: #img_count < 15 
            self.img = self.IMGS[2] # display bird 3
        elif self.img_count <= self.ANIMATION_TIME*4: #img_count < 20 
            self.img = self.IMGS[1] # show image 2
        elif self.img_count == self.ANIMATION_TIME*4 + 1: # <16
            self.img = self.IMGS[0] # display image 1
            self.img_count = 0 #reset image count 

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80: #if tilt <= -80
            self.img = self.IMGS[0] # display image 1 when nose diving
            self.img_count = self.ANIMATION_TIME*2 # when we jump back up after diving, motion is in a continous form


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt) #rotate bird image wrt its center 
    
    # For detecting or checking the collision of bird.
    # Mask is a 2D array of where all pixels are inside of the box. helps us check if pixels are colliding rather than box. 
    def get_mask(self): 
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img) # masking all the bird images.


# Class for all pipe related objects
class Pipe():
    """
    represents a pipe object
    """
    GAP = 200 # Space in between pipe
    VEL = 5 # How fast our pipes are moving on screen

    def __init__(self, x):
        """
        initializing pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x #location of pipe in x
        self.height = 0 #height of pipe at start

        #where the top and bottom of the pipe at initialization
        self.top = 0 # Location of top pipe at start 
        self.bottom = 0 # Location of bottom pipe at start 

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True) #rotating of pipe image for top pipe
        self.PIPE_BOTTOM = pipe_img # pipe image

        self.passed = False #check if bird has already passed a pipe

        self.set_height() # Defining where top, bottom pipes are, where gap is and height of top, bottom pipe

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450) #randomizing top of pipe
        self.top = self.height - self.PIPE_TOP.get_height() # Figuring out top left of pipe to draw it on screen, as top pipe will extend down on to the screen. location of top of a pipe
        self.bottom = self.height + self.GAP #Top left of pipe to draw on screen. location of bottom pipe

    def move(self): # To move pipe we have to change x position based on veloity of the game
        """
        moving pipe based on vel
        :return: None
        """
        self.x -= self.VEL #velocity of pipe moving wrt to FPS of game (move pipe to left of screen)

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
        # Masking images
        bird_mask = bird.get_mask() # Getting masked bird ( bird class declaration)
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) #masking top pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) #masking bottom pipe
        
        # Offset checks how far away masks are from each other 
        top_offset = (self.x - bird.x, self.top - round(bird.y)) #offset from bird_mask to top_mask
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) #offset from bird_mask to bottom_mask

        b_point = bird_mask.overlap(bottom_mask, bottom_offset) #checking for pixel collision of bird_mask and bottom pipe(offset of bottom pipe)
        t_point = bird_mask.overlap(top_mask,top_offset) #checking for picel collision of bird_mask and top pipe(offset of top pipe)

        if b_point or t_point: #checking for collision and overlapping of pixels
            return True # checks if bird is colliding with pipe object 
            

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
        self.x1 = 0 #pos of x i.e., image 1
        self.x2 = self.WIDTH # width of base i.e., image 2

    def move(self):
        """
        moving floor 
        :return: None
        """
        self.x1 -= self.VEL # moving x1 image at VEL speed
        self.x2 -= self.VEL # moving x2 image at VEL speed. Both x1 and x2 must move at same speed

        if self.x1 + self.WIDTH < 0: # checking if x1 is off the screen completely
            self.x1 = self.x2 + self.WIDTH # cycling back x1 image behind x2 image for movement

        if self.x2 + self.WIDTH < 0: # checking if x2 is off the screen completely
            self.x2 = self.x1 + self.WIDTH # cycling back x2 image behind x1 image for movement

    def draw(self, win):
        """
        Drawing floor. 
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y)) # drawing base image on game window
        win.blit(self.IMG, (self.x2, self.y)) # drawing base image on game window


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
    win.blit(bg_img, (0,0)) # drawing background image on screen

    # Drawing pipes on screen
    for pipe in pipes: 
        pipe.draw(win) 

    # Drawing base on screen
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
        net = neat.nn.FeedForwardNetwork.create(genome, config) # Neural network creation
        nets.append(net) # appending NN to nets list
        birds.append(Bird(230,350)) # Starting pos of bird and append it to birds list
        ge.append(genome) # appending genomes to ge list

    base = Base(FLOOR) # base and its width
    pipes = [Pipe(700)] # Pipes list. There can be more than 1 pipe on screen at time so list is being used to keep track of all pipes
    score = 0 # starting score

    clock = pygame.time.Clock() # Setting frame rate/ FPS 

    run = True
    while run and len(birds) > 0:
        clock.tick(30) # setting FPS at 30 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
                pygame.quit()
                quit()
                break

        # determine whether to use the first or second pipe on the screen for neural network input
        pipe_ind = 0 # setting index of pipe that is visible to bird as 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): # Checking if bird has passed that pipe 
                #if len(pipes) > 1 we get x position of any bird as x pos is always same, if it is > pipes[0].x we ask bird to look at second pipe at list
                pipe_ind = 1 # Increasing index if bird has passed the pipe                                                                

        for x, bird in enumerate(birds):  
            ge[x].fitness += 0.1 # give each bird a fitness of 0.1 for each frame it stays alive
            bird.move() #moving the bird game window

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            # bird.y is first info we need, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom) = finding bistance b/w top pipe, bottom pipe and bird

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move() # moving base on game window

        rem = [] # list of removed pipes
        add_pipe = False
        for pipe in pipes: # to check for more than 1 pipe
            pipe.move() # moving pipes on game window
            
            # check for collision of all birds with pipes
            for bird in birds:
                if pipe.collide(bird, win): #checking for collision of bird with pipe
                    ge[birds.index(bird)].fitness -= 1 # every time a bird hits pipe -1 fitness is removed from that bird
                    nets.pop(birds.index(bird)) # remove NN of bird that has collided
                    ge.pop(birds.index(bird)) # remove genome of bird that has collided
                    birds.pop(birds.index(bird)) # remove bird that has collided

            # Checking position of pipe
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: #remove pipe when it passes a certain location on screen
                rem.append(pipe) #removing pipe 
            
            # Checking if pipe is passed and addition of new pipe
            if not pipe.passed and pipe.x < bird.x: #check if bird has passes the pipe
                pipe.passed = True #check if bird is passed a pipe
                add_pipe = True #if pipe is passed by bird we add a new pipe

        # Keeping track of new pipes and score variable
        if add_pipe: #adding new pipes
            score += 1 #adding score when bird passes through a pipe
            for genome in ge:
                genome.fitness += 5 #increase fitness when bird passes through a pipe
            pipes.append(Pipe(WIN_WIDTH)) #adding new pipe at the end of game window

        for r in rem: #remove pipe when a bird passes through it
            pipes.remove(r) # getting rid of removed pipes

        
        for bird in birds: # Multiple birds in population and check each bird if it hits ground
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50: # Checking if bird hits the ground and check if bird above the screen
                nets.pop(birds.index(bird)) # remove NN of bird that hit ground
                ge.pop(birds.index(bird)) # remove genome of bird that hit ground
                birds.pop(birds.index(bird)) # remove bird that hit ground

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # break generation score gets large enough and put best bird in pickle file
        if score > 21:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break
        
        
        


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    # Loading all the defined configurations for NEAT.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Creating the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Adding a reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 3 generations.
    winner = p.run(eval_genomes, 3)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. 
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)