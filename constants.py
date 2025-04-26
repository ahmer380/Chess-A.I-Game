import pygame,sys

#colour RGB values
ARCTIC = (244,243,239)
BLACK = (0,0,0)
GREEN = (11,102,35)
GREY = (58,59,60)
MINT = (65,105,88)
RED = (138,3,3)
ORANGE = (237,135,45)
WHITE = (255,255,255)

cell_size = 90
cell_number = 8
MAX_SCORE = 99999999
MIN_SCORE = -99999999
screen = pygame.display.set_mode((720,720)) #720 = cell_size x cell_number =  90 x 8
game_font = 'Extras/MochiyPopPOne-Regular.ttf'