import pygame # python game module
import random # random module. Used for randomizing generation of pipes
import os # module used for setting up path 
import time # python module for importing time access
from pygame.locals import * # pygame imports

#initializations
pygame.font.init() # init font
pygame.mixer.init()  # pygame sound mixer init

GAME_SOUNDS = {} # game sounds dictionary

#Game window specifications
WIN_WIDTH = 600 # game window width
WIN_HEIGHT = 800 # game window height
PIPE_VEL = 3 # velocity at which pipes move on the screen
FLOOR = 700 # size of floor

#fonts in pygame
STAT_FONT = pygame.font.SysFont("comicsans", 50) # font for score
END_FONT = pygame.font.SysFont("comicsans", 70) # font to restart game

#Display options of game window
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #display pygame window wrt to given width and height
pygame.display.set_caption("Flappy Bird") # Game window caption

#Loading images
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

class Bird:
    """
    Bird class representing the flappy bird
    """

    #WIN_HEIGHT = 0 
    #WIN_WIDTH = 0
    MAX_ROTATION = 25 # max rotation of bird
    IMGS = bird_images # images
    ROT_VEL = 20 # speed at which bird rotates
    ANIMATION_TIME = 5 # animation of birds flapping

    # init method or constructor
    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """

        #Here self represents the Bird class i.e., self.x is same as Bird.x = x
        self.x = x # starting x pos of bird
        self.y = y # starting y pos of bird
        self.gravity = 9.8 # gravity constant
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0 # bird jump and fall 
        self.vel = 0 # velocity of bird at start
        self.height = self.y #tilt and moving of bird
        self.img_count = 0 # Which image of bird is currently being shown{used for animation}
        self.img = self.IMGS[0] # referencing current bird image

    def jump(self):
        """
        make the bird jump
        :return: None
        """

        self.vel = -10.5 # velocity of bird jump
        self.tick_count = 0 # keeps track of last jump for keeping track of jump and fall of bird
        self.height = self.y # original height and starting point of bird
        GAME_SOUNDS['wing'].play() # game sound of wings flapping

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1 # keeping tack of how much bird moved with regard to last jump or starting

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculating displacement i.e., movement of bird up and down 

        # terminal velocity i.e., velocity of bird capped to a value so that bird doesnot move very fast in either direction 
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
            
            
        # jump value or jump height
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement # moving bird slowly up or down. Change y position based on displacement

        if displacement < 0 or self.y < self.height + 50:  # d < 0 or self.y is bird moving up. Tilting up of bird
            if self.tilt < self.MAX_ROTATION: # for tilt angle of 25
                self.tilt = self.MAX_ROTATION # if yes then tilt bird by 25 directly
        else:  # tilting down of bird
            if self.tilt > -90: # rotate bird directly by 90 degrees.
                self.tilt -= self.ROT_VEL #looks like bird is nose diving
                GAME_SOUNDS['swoosh'].play() # game sound of bird falling down

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1
        
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


        # tilt the bird based on its center. 
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt) #rotate bird image wrt its center

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

    WIN_HEIGHT = WIN_HEIGHT # game window width
    WIN_WIDTH = WIN_WIDTH # game window height
    GAP = 200 # gap in between 2 pipes
    VEL = 5 # velocity of pipe moving on screen

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x # starting location of pipe in x
        self.height = 0 # height of pipe at start 
        self.gap = 100  # gap between top and bottom pipe

        # where the top and bottom of the pipe is
        self.top = 0 # Location of top pipe at start 
        self.bottom = 0 # location of bottom pipe at start 

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True) # rotating of pipe image for top pipe
        self.PIPE_BOTTOM = pipe_img # pipe image

        self.passed = False # check if bird has already passed a pipe

        self.set_height() # Defining where top, bottom pipes are, where gap is and height of top, bottom pipe

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450) # randomizing height of pipe
        self.top = self.height - self.PIPE_TOP.get_height() # Figuring out top left of pipe to draw it on screen, as top pipe will extend down on to the screen. location of top of a pipe
        self.bottom = self.height + self.GAP #Top left of pipe to draw on screen. location of bottom pipe

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL # velocity of pipe moving wrt FPS/clock of game

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        
        win.blit(self.PIPE_TOP, (self.x, self.top)) # draw top pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom)) # draw bottom pipe


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask() # getting masked bird
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) # masking top pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) # masking bottom pipe
        
        # Offset checks how far away masks are from each other 
        top_offset = (self.x - bird.x, self.top - round(bird.y)) # offset from bird_mask to top_mask
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) # offset from bird_mask to bottom_mask

        b_point = bird_mask.overlap(bottom_mask, bottom_offset) # checking for pixel collision of bird_mask and bottom pipe (offset of bottom pipe)
        t_point = bird_mask.overlap(top_mask,top_offset) # checking for pixel collision of bird_mask and top pipe (offset of top pipe)

        if b_point or t_point: # checking for collision and overlapping of pixels
            return True # checks if bird is colliding with pipe object 
        

        return False

class Base:
    """
    Represnts the moving floor of the game
    """
    VEL = 5 # velocity of base moving
    #WIN_WIDTH = WIN_WIDTH # width of base
    WIDTH = base_img.get_width() # base image
    IMG = base_img # base image

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y # starting pos of base 
        self.x1 = 0 # position of x i.e., image x1 base x1
        self.x2 = self.WIDTH # width of base i.e., image x2

    def move(self):
        """
        move floor so it looks like its scrolling
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
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


#pipe rotation for top pipe
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


def end_screen(win):
    """
    display an end screen when the player loses
    :param win: the pygame window surface
    :return: None
    """
    run = True
    text_label = END_FONT.render("Press SPACE TO START", 0.5 , (255,0,0))
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main(win)

        #win.blit(text_label, (WIN_WIDTH/2 - text_label.get_width()/2, 500))
        text_rect = text_label.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
        win.blit(text_label, text_rect)

        pygame.display.update()

    pygame.quit()
    quit()


def draw_window(win, bird, pipes, base, score):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :return: None
    """
    win.blit(bg_img, (0,0)) # drawing background image on game window

    # drawing pipes on screen
    for pipe in pipes:
        pipe.draw(win)

    # drawing base on screen
    base.draw(win)
    bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(0,0,255))
    
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()


def main(win):
    """
    Runs the main game loop
    :param win: pygame window surface
    :return: None
    """

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    bird = Bird(230,50) #Starting position of bird
    base = Base(FLOOR) # base on floor
    pipes = [Pipe(700)] # Pipes list. There can be more than 1 pipe on screen at time so list is being used to keep track of all pipes
    score = 0 # starting score

    clock = pygame.time.Clock() # setting frame rate / FPS
    lost = False 

    run = True
    while run:
        pygame.time.delay(30)
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN and not lost:
                if event.key == pygame.K_SPACE:
                    bird.jump()
                    GAME_SOUNDS['wing'].play()

        # Move Bird, base and pipes
        bird.move()
        if not lost:
            base.move()

            rem = [] # list of removed pipes
            add_pipe = False
            for pipe in pipes: # to check for more than 1 pipe
                pipe.move() # moving pipes on game window
        
                if pipe.collide(bird, win): # check for collision
                    GAME_SOUNDS['hit'].play()
                    #GAME_SOUNDS['die'].play()
                    lost = True
                


                if pipe.x + pipe.PIPE_TOP.get_width() < 0: #remove pipe when it passes a certain location on screen
                    rem.append(pipe) # removing pipe

                # Checking if pipe is passed and addition of new pipe
                if not pipe.passed and pipe.x < bird.x: #check if bird has passes the pipe
                    pipe.passed = True #check if bird is passed a pipe
                    add_pipe = True #if pipe is passed by bird we add a new pipe
            
            # Keeping track of new pipes and score variable
            if add_pipe:
                GAME_SOUNDS['point'].play()
                score += 1 #adding score when bird passes through a pipe
                pipes.append(Pipe(WIN_WIDTH)) #adding new pipe at the end of game window
                

            for r in rem: #remove pipe when a bird passes through it
                pipes.remove(r) # removing pipes that have been passed


        if bird.y + bird_images[0].get_height() - 10 >= FLOOR or bird.y < -50: # Checking if bird hits the ground and check if bird above the screen
            #GAME_SOUNDS['hit'].play()
            GAME_SOUNDS['die'].play()
            break

        draw_window(WIN, bird, pipes, base, score)

    end_screen(WIN)

main(WIN)