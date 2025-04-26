from constants import *
from pieces import pawn,knight,bishop,rook,queen,king
from gamedata import gamedata
from AI import AI

pygame.init()
pygame.display.set_caption('Chess')
clock = pygame.time.Clock()

game_active = False #initiaize to false

current_turn = 'w'
mouse_pos = (0,0)

class appendices:
    #this class neatly stores all additional functions that are frequently used
    #within the rest of the program, but are not distinctly part of a specific class

    @staticmethod
    def flip_current_turn(turn):
        if turn == 'w':
            turn = 'b'
        else:
            turn = 'w'
        return turn

    @staticmethod
    def map_piece_to_image():
        dictionary = {} #use of global dictionary allows easy access when mapping a piece to its image
        pieces = ['bB','bK','bN','bp','bQ','bR','wB','wK','wN','wp','wQ','wR']
        for piece in pieces:
            image_png = pygame.image.load('Extras/pieces/'+piece+'.png').convert_alpha()
            dictionary[piece] = pygame.transform.scale(image_png,(cell_size,cell_size))
            #initial size of pieces set to cover a square on the board

        return dictionary

    @staticmethod
    def map_pos_to_square():
        dictionary = {} #converts a position in a python array to its corresponding chess square
        if gamedata.player_colour == 'w':
            files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        else:  # if player_colour = black
            files = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
            ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        for row in range(cell_number):
            for col in range(cell_number):
                square_pos = files[col]+ranks[row]
                dictionary[(row,col)] = square_pos

        return dictionary

    @staticmethod
    def get_col_row_from_pos(x_pos,y_pos):
        if gamedata.player_colour == 'w':
            clicked_row = y_pos // cell_size
        else: #player_colour is black, so vertically invert 'clicked_row'
            clicked_row = 7 - (y_pos // cell_size)

        clicked_col = x_pos // cell_size

        return clicked_row,clicked_col

    @staticmethod
    def text_schematic(text,x_pos,y_pos,size,colour,point):
        #creates text of any colour,font and size in a given position

        font = pygame.font.Font(game_font, size)
        surface = font.render(str(text),True,colour)
        if point == 'centre': #if x_pos,y_pos is a central point
            rect = surface.get_rect(center = (x_pos,y_pos))
        elif point == 'midleft': #if x_pos,y_pos is the middle-left point
            rect = surface.get_rect(midleft = (x_pos,y_pos))
        elif point == 'topleft': #if x_pos,y_pos is the top-left point
            rect = surface.get_rect(topleft = (x_pos,y_pos))
        elif point == 'topright': # if x_pos,y_pos is the top-right point
            rect = surface.get_rect(topright = (x_pos,y_pos))
        elif point == 'bottomleft': #if x_pos,y_pos is the bottom-left point
            rect = surface.get_rect(bottomleft = (x_pos,y_pos))
        else:
            return 'Invalid information'
        return surface,rect

    @staticmethod
    def border_schematic(rect): #if given a rectangle, will create a perimeter rectangle around it
        border_rect = pygame.Rect(rect.left,rect.top,rect.width,rect.height)
        return border_rect

    @staticmethod
    def begin_game(difficulty_chosen,colour_chosen):
        #instantiates/updates all necessary variables/objects when user clicks start button (successfully)
        global game_active
        game_active = True
        gamedata.difficulty = difficulty_chosen

        if colour_chosen == 'w': #user chose white, A.I is black
            gamedata.player_colour = 'w'
            gamedata.ai_colour = 'b'
            ai.ai_colour = 'b'
        else: #user chose black, A.I is white
            gamedata.player_colour = 'b'
            gamedata.ai_colour = 'w'
            ai.ai_colour = 'w'

        chessboard.initialize_pieces()
        ai.initialize_depth()
        gamedata.obtain_all_valid_moves(chessboard.digital_board,'b',chessboard.class_dictionary,'first move')
        post_game_report.player_colour = colour_chosen
        # if A.I is white, it already will have some moves to choose from

class main_menu:
    def __init__(self):
        self.is_difficulty = False #true if difficulty has been chosen, false if not
        self.difficulty_chosen = ''
        self.is_player_colour = False #true if player colour has been chosen, false if not
        self.player_colour_chosen = ''

    def display(self):
        screen.fill(GREY)
        self.display_start_button()
        self.display_prompts()
        self.display_title()
        self.display_and_update_piece_select()
        self.display_and_update_difficulty_select()
        self.display_status_box()

    def check_status(self,start_button_textbox):
        if start_button_textbox.collidepoint(mouse_pos[0],mouse_pos[1]) == 1:
            #if the start button has been clicked, check if game can begin
            if self.is_difficulty == True and self.is_player_colour == True:
                #start button is clicked and necessary data has been entered
                appendices.begin_game(self.difficulty_chosen,self.player_colour_chosen)

    def display_prompts(self):
        difficulty_prompt_surface,difficulty_prompt_rect = appendices.text_schematic('• Enter difficulty',70,620,30,RED,'midleft')
        colour_prompt_surface,colour_prompt_rect = appendices.text_schematic('• Enter colour',difficulty_prompt_rect.left,difficulty_prompt_rect.bottom,30,RED,'topleft')

        if not self.is_difficulty:
            screen.blit(difficulty_prompt_surface,difficulty_prompt_rect)
        if not self.is_player_colour:
            screen.blit(colour_prompt_surface,colour_prompt_rect)

    def display_start_button(self):
        if self.is_difficulty == True and self.is_player_colour == True:
            border_colour = GREEN #highlight start button in green if it is allowed to be clicked
        else:
            border_colour = RED #highlight start button in red if details are missing

        start_button_surface,start_button_rect = appendices.text_schematic('START',580,650,50,WHITE,'centre')
        border_rect = appendices.border_schematic(start_button_rect)
        pygame.draw.rect(screen,border_colour,border_rect,5)
        screen.blit(start_button_surface,start_button_rect)

        self.check_status(start_button_rect)

    def display_title(self):
        title_surface,title_rect = appendices.text_schematic('CHESS',360,50,80,WHITE,'centre')
        underline_rect = pygame.Rect(title_rect.left,title_rect.bottom,title_rect.width,20)
        pygame.draw.rect(screen,WHITE,underline_rect,2)
        screen.blit(title_surface,title_rect)

    def display_and_update_piece_select(self):
        if self.player_colour_chosen == 'w': #highlight around the white piece only
            self.is_player_colour = True
            white_colour = GREEN
            black_colour = WHITE

        elif self.player_colour_chosen == 'b': #highlight around the black piece only
            self.is_player_colour = True
            white_colour = WHITE
            black_colour = GREEN
        else: #player piece not yet chosen, don't highlight around either piece
            white_colour = WHITE
            black_colour = WHITE

        colour_text_surface,colour_text_rect = appendices.text_schematic('Colour',450,200,40,WHITE,'centre')
        screen.blit(colour_text_surface, colour_text_rect)

        colour_text_underline_rect = pygame.Rect(colour_text_rect.left,colour_text_rect.bottom,colour_text_rect.width,10)
        pygame.draw.rect(screen, WHITE, colour_text_underline_rect)

        #creating and displaying the image of the white king
        white_king_display = pygame.transform.rotozoom(piece_images_dictionary['wK'],0,1.5)
        white_rect = white_king_display.get_rect(topleft = (colour_text_underline_rect.left,colour_text_underline_rect.bottom+10))
        white_border_rect = appendices.border_schematic(white_rect)
        screen.blit(white_king_display, white_rect)
        pygame.draw.rect(screen, white_colour, white_border_rect, 5)

        #creating and displaying the image of the black king
        black_king_display = pygame.transform.rotozoom(piece_images_dictionary['bK'],0,1.5)
        black_rect = black_king_display.get_rect(topleft = (white_rect.right+30,white_rect.top))
        black_border_rect = appendices.border_schematic(black_rect)
        screen.blit(black_king_display,black_rect)
        pygame.draw.rect(screen,black_colour,black_border_rect,5)

        self.process_colour_input(white_rect,black_rect,mouse_pos)

    def process_colour_input(self,white_piece_image,black_piece_image,clicked_pos):
        #if the images of the black or white pieces are clicked, update the attributes of the colour chosen
        if white_piece_image.collidepoint(clicked_pos[0],clicked_pos[1]) == 1:
            self.player_colour_chosen = 'w'
        elif black_piece_image.collidepoint(clicked_pos[0],clicked_pos[1]) == 1:
            self.player_colour_chosen = 'b'

    def display_and_update_difficulty_select(self):
        if self.difficulty_chosen == 'Beginner': #highlight the text 'Beginner' in green only
            self.is_difficulty = True
            beginner_colour = GREEN
            intermediate_colour = WHITE
            expert_colour = WHITE
        elif self.difficulty_chosen == 'Intermediate': #highlight the text 'Intermediate' in green only
            self.is_difficulty = True
            beginner_colour = WHITE
            intermediate_colour = GREEN
            expert_colour = WHITE
        elif self.difficulty_chosen == 'Expert': #highlight the text 'Expert' in green only
            self.is_difficulty = True
            beginner_colour = WHITE
            intermediate_colour = WHITE
            expert_colour = GREEN
        else: #difficulty not yet chosen, don't highlight any text
            beginner_colour = WHITE
            intermediate_colour = WHITE
            expert_colour = WHITE

        #creating and displaying surfaces for the difficulty UI
        difficulty_text_surface,difficulty_text_rect = appendices.text_schematic('Difficulty',50,200,40,WHITE,'midleft')
        screen.blit(difficulty_text_surface,difficulty_text_rect)

        difficulty_text_underline_rect = pygame.Rect(difficulty_text_rect.left,difficulty_text_rect.bottom,difficulty_text_rect.width,10)
        pygame.draw.rect(screen,WHITE,difficulty_text_underline_rect)

        beginner_surface,beginner_rect = appendices.text_schematic('Beginner',difficulty_text_underline_rect.left,difficulty_text_underline_rect.bottom,30,beginner_colour,'topleft')
        screen.blit(beginner_surface,beginner_rect)

        intermediate_surface,intermediate_rect = appendices.text_schematic('Intermediate',beginner_rect.left,beginner_rect.bottom+10,30,intermediate_colour,'topleft')
        screen.blit(intermediate_surface, intermediate_rect)

        expert_surface,expert_rect = appendices.text_schematic('Expert',intermediate_rect.left,intermediate_rect.bottom+10,30,expert_colour,'topleft')
        screen.blit(expert_surface,expert_rect)

        self.process_difficulty_input(beginner_rect,intermediate_rect,expert_rect,mouse_pos)

    def process_difficulty_input(self,beginner_textbox,intermediate_textbox,expert_textbox,clicked_pos):
        # if the 'beginner', 'intermediate' or 'expert' buttons are clicked, update the difficulty
        if beginner_textbox.collidepoint(clicked_pos[0],clicked_pos[1]) == 1:
            self.difficulty_chosen = 'Beginner'
        elif intermediate_textbox.collidepoint(clicked_pos[0],clicked_pos[1]) == 1:
            self.difficulty_chosen = 'Intermediate'
        elif expert_textbox.collidepoint(clicked_pos[0],clicked_pos[1]) == 1:
            self.difficulty_chosen = 'Expert'

    def display_status_box(self):
        if self.player_colour_chosen == 'w':
            colour = 'white'
        elif self.player_colour_chosen == 'b':
            colour = 'black'
        else:
            colour = ''

        difficulty_status_surface,difficulty_status_rect = appendices.text_schematic('Difficulty: '+self.difficulty_chosen,50,500,30,WHITE,'midleft')
        colour_status_surface,colour_status_rect = appendices.text_schematic('Colour: '+colour,difficulty_status_rect.left,difficulty_status_rect.bottom,30,WHITE,'topleft')
        border_rect = appendices.border_schematic(difficulty_status_rect)
        border_rect[3] += colour_status_rect.height # updates the height of the border rectangle so that it outlines both difficulty and colour
        border_rect[2] = 398 #the maximum width the border rectangle will be is 398 pixels, if the word intermediate is displayed

        screen.blit(difficulty_status_surface,difficulty_status_rect)
        screen.blit(colour_status_surface,colour_status_rect)
        pygame.draw.rect(screen,WHITE,border_rect,2)

class chessboard:
    def __init__(self):
        self.class_dictionary = {}
        #enter a co-ordinate in order to return an object (if any) of the piece on that square

        self.digital_board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['00','00','00','00','00','00','00','00'],
            ['00','00','00','00','00','00','00','00'],
            ['00','00','00','00','00','00','00','00'],
            ['00','00','00','00','00','00','00','00'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']
        ]

        self.hint_move = []

    def initialize_pieces(self):
        #initiating material scores for each piece, king value already defined
        if gamedata.difficulty == 'Expert':
            #these are the optimal values
            pawn.value = 1
            knight.value = 3
            bishop.value = 3
            rook.value = 5
            queen.value = 9
        if gamedata.difficulty == 'Intermediate':
            pawn.value = 1
            knight.value = 4
            bishop.value = 4
            rook.value = 4
            queen.value = 8
        if gamedata.difficulty == 'Beginner':
            pawn.value = 1
            knight.value = 3
            bishop.value = 3
            rook.value = 5
            queen.value = 5

        #create black major pieces
        self.class_dictionary[(0,0)] = rook('b',[0,0])
        self.class_dictionary[(0,1)] = knight('b',[0,1])
        self.class_dictionary[(0,2)] = bishop('b',[0,2])
        self.class_dictionary[(0,3)] = queen('b',[0,3])
        self.class_dictionary[(0,4)] = king('b',[0,4])
        self.class_dictionary[(0,5)] = bishop('b',[0,5])
        self.class_dictionary[(0,6)] = knight('b',[0,6])
        self.class_dictionary[(0,7)] = rook('b',[0,7])

        #create white major pieces
        self.class_dictionary[(7,0)] = rook('w',[7,0])
        self.class_dictionary[(7,1)] = knight('w',[7,1])
        self.class_dictionary[(7,2)] = bishop('w',[7,2])
        self.class_dictionary[(7,3)] = queen('w',[7,3])
        self.class_dictionary[(7,4)] = king('w',[7,4])
        self.class_dictionary[(7,5)] = bishop('w',[7,5])
        self.class_dictionary[(7,6)] = knight('w',[7,6])
        self.class_dictionary[(7,7)] = rook('w',[7,7])

        #create black and white pawns
        for create_pawn in range(cell_number):
            self.class_dictionary[(1,create_pawn)] = pawn('b',[1,create_pawn])
            self.class_dictionary[(6,create_pawn)] = pawn('w',[6,create_pawn])

    def update(self,start_square,end_square,is_undo):
        #updates all the common necessary objects and attributes, called every time a piece moves
        self.update_class_dictionary(start_square,end_square,is_undo)
        self.update_digital_board(start_square,end_square)

    def update_class_dictionary(self,start_square,end_square,is_undo):
        self.class_dictionary[(end_square[0],end_square[1])] = self.class_dictionary[(start_square[0],start_square[1])]
        #transfer the piece object to its new square (overwrites any piece object on that square before)
        self.class_dictionary.pop((start_square[0], start_square[1])) #delete the piece object from its old square

        self.class_dictionary[(end_square[0],end_square[1])].position = [end_square[0],end_square[1]]
        #updates the attribute 'position' of the piece object

        #increments/decrements the attribute 'move_count' by 1
        if is_undo:
            self.class_dictionary[(end_square[0], end_square[1])].move_count -= 1
        else:
            self.class_dictionary[(end_square[0], end_square[1])].move_count += 1

    def update_digital_board(self,start_square,end_square):
        self.digital_board[end_square[0]][end_square[1]] = self.digital_board[start_square[0]][start_square[1]]
        #new square marked as signature of new piece
        self.digital_board[start_square[0]][start_square[1]] = '00'
        #old square marked as empty

    def add_new_object(self,square,class_info):
        #creates new object in the class dictionary, and updates digital board
        self.class_dictionary[(square[0],square[1])] = class_info
        self.digital_board[square[0]][square[1]] = class_info.initial

    def display_valid_moves(self,clicked_pos):
        available_moves = self.generate_valid_moves(clicked_pos)
        #returns a list of moves, containing the start and end squares

        if gamedata.player_colour == 'b':
            inverse_multiplier = 7 #used in order optimise blacks perspective by vertically inverting the board
        else:
            inverse_multiplier = 0
        for move in available_moves:
            end_square_x = move[1][1]
            end_square_y = move[1][0]
            x_pos = (end_square_x * cell_size) + (cell_size // 2)
            y_pos = (abs(inverse_multiplier - end_square_y) * cell_size) + (cell_size // 2)
            #the 2 lines above provide the co-ordinates of the centre of each square the piece could go to
            pygame.draw.circle(screen,GREY,(x_pos,y_pos),10)
            pygame.display.update()

        return available_moves

    def generate_valid_moves(self,clicked_pos):
        if self.digital_board[clicked_pos[0]][clicked_pos[1]][0] == current_turn:
            #user has clicked on one of their pieces

            piece_object = self.class_dictionary[(clicked_pos[0],clicked_pos[1])]
            if piece_object.colour == 'w':
                king_pos = gamedata.white_king_pos
            else:
                king_pos = gamedata.black_king_pos
            available_moves = piece_object.calculate_moves(self.digital_board,king_pos)
            return available_moves
        else: #user has clicked on an empty square or on a square of a piece it cannot control
            return []

    def display_board(self,colour1,colour2):
        self.display_chessboard_pattern(colour1,colour2)
        self.display_hint()
        self.display_labels(colour1,colour2)
        self.display_pieces()

    def display_chessboard_pattern(self,colour1,colour2): #input 2 colours, and a chequered pattern is created
        screen.fill(colour1)
        for row in range(cell_number):
            for col in range(cell_number):
                if ((row % 2) == 0 and (col % 2) == 0) or ((row % 2) == 1 and (col % 2) == 1):
                    square_rect = pygame.Rect(row*cell_size,col*cell_size,cell_size,cell_size)
                    pygame.draw.rect(screen,colour2,square_rect)

    def display_labels(self,colour1,colour2): #creating the file labels 'a-h', and rank labels '1-8'
        file_order = ['a','b','c','d','e','f','g','h']
        if gamedata.player_colour == 'w':
            rank_order = ['8','7','6','5','4','3','2','1']
        else: #if player_colour = black
            rank_order = ['1','2','3','4','5','6','7','8']

        for square in range(cell_number):
            if square % 2 == 1:
                label_colour = colour1
            else:
                label_colour = colour2

            file_surface,file_rect = appendices.text_schematic(file_order[square],square*cell_size,cell_number*cell_size,20,label_colour,'bottomleft')
            rank_surface,rank_rect = appendices.text_schematic(rank_order[square],cell_number*cell_size,square*cell_size,20,label_colour,'topright')
            screen.blit(file_surface,file_rect)
            screen.blit(rank_surface,rank_rect)

    def display_pieces(self):
        if gamedata.player_colour == 'b':
            inverse_multiplier = 7 #used in order optimise blacks perspective by vertically inverting the board
        else:
            inverse_multiplier = 0
        for row in range(cell_number):
            for col in range(cell_number):
                square = self.digital_board[row][col]
                if square != '00': #if the position is not an empty square
                    piece_image = piece_images_dictionary[square]
                    square_rect = piece_image.get_rect(topleft = (col*cell_size,abs(inverse_multiplier-row)*cell_size))
                    screen.blit(piece_image,square_rect)

    def display_hint(self):
        if self.hint_move == []:
            return

        if gamedata.player_colour == 'b': #used in order optimise blacks perspective by vertically inverting the board
            inverse_multiplier = 7
        else:
            inverse_multiplier = 0

        start_square_x = self.hint_move[0][1] * cell_size
        start_square_y = abs(inverse_multiplier-self.hint_move[0][0]) * cell_size
        end_square_x = self.hint_move[1][1] * cell_size
        end_square_y = abs(inverse_multiplier-self.hint_move[1][0]) * cell_size


        #shade the start and end squares of the hint move in orange
        start_square_rect = pygame.Rect(start_square_x,start_square_y,cell_size,cell_size)
        pygame.draw.rect(screen,ORANGE,start_square_rect)

        end_square_rect = pygame.Rect(end_square_x,end_square_y,cell_size,cell_size)
        pygame.draw.rect(screen,ORANGE,end_square_rect)

class move_engine:
    @staticmethod
    def initiate_move(move_data):
        #this is called to initiate a move. Everything in the program is updated here including:
        #1. Updating the gamedata attribute capture stack
        #2. updating the chessboard object
        #3. Initializing special moves such as castling and pawn promotions (if executed by player/A.I)
        #4. Updating the gamedata object
        #5. Flipping the current_turn
        #6. Emptying the contents of move_data

        global current_turn
        start_square = move_data[0]
        end_square = move_data[1]

        #1.
        gamedata.log_captured_piece(end_square,chessboard.class_dictionary)

        #2.
        chessboard.update(start_square,end_square,False)

        #3.
        piece_object = chessboard.class_dictionary[(end_square[0],end_square[1])]
        #gets object of piece that just moved
        if type(piece_object).__name__ == 'king':  # if the piece_object moved is the king
            move_engine.initiate_move_king(start_square,end_square,piece_object)

        if type(piece_object).__name__ == 'pawn':  # if the piece_object moved is a pawn, may promote
            move_engine.pawn_promotion(end_square,piece_object)

        #4.
        gamedata.update(chessboard.digital_board,current_turn,chessboard.class_dictionary,move_data,False)

        #5.
        current_turn = appendices.flip_current_turn(current_turn)

        #6.
        return []

    @staticmethod
    def initiate_move_king(start_square,end_square,king_object):
        # 1.check if castled
        if abs(end_square[1]-start_square[1]) == 2:  # if the king has moved 2 squares to the right/left i.e.castled
            king_object.castled = True
            # rook also needs to move, which is what the lines below achieve
            if end_square[1] == 6:  # if player castled king side
                rook_start_pos = (start_square[0],7)
                rook_new_pos = (start_square[0],5)
            else:  # if player castled queen side
                rook_start_pos = (start_square[0],0)
                rook_new_pos = (start_square[0],3)
            chessboard.update(rook_start_pos,rook_new_pos,False)

        # 2.update white/black_king_pos attributes
        if king_object.colour == 'w':
            gamedata.white_king_pos = (end_square[0],end_square[1])
        else:
            gamedata.black_king_pos = (end_square[0],end_square[1])

    @staticmethod
    def undo_move_king(start_square,end_square,king_object):
        # 1.check if de-castled
        if abs(end_square[1]-start_square[1]) == 2:  # if the king has moved 2 squares to the right/left i.e.castled
            king_object.castled = False

            #rook also needs to move, which is what the lines below achieve
            if start_square[1] == 6:  #if player castled king side
                rook_start_pos = (start_square[0],5)
                rook_new_pos = (start_square[0],7)
            else:  # if player castled queen side
                rook_start_pos = (start_square[0],3)
                rook_new_pos = (start_square[0],0)
            chessboard.update(rook_start_pos,rook_new_pos,True)

        # 2.update white/black_king_pos attributes
        if king_object.colour == 'w':
            gamedata.white_king_pos = (end_square[0],end_square[1])
        else:
            gamedata.black_king_pos = (end_square[0],end_square[1])

    @staticmethod
    def pawn_promotion(end_square,pawn_object):
        if pawn_object.check_for_promote(): #pawn can promote. Replace pawn class object to queen
            chessboard.add_new_object(end_square,queen(pawn_object.colour,[end_square[0],end_square[1]],True))
            #final argument 'True' represents the fact that this object originates from a promoted pawn

    @staticmethod
    def check_depromote(end_square,piece_object):
        if piece_object.is_promoted and piece_object.move_count == -1:
            #if the piece object stems from a pawn and hasn't moved yet

            chessboard.add_new_object(end_square,pawn(piece_object.colour,[end_square[0],end_square[1]]))

    @staticmethod
    def undo_move():
        #this is called to undo a move. Everything in the program is updated here including:
        #1. Access the previous move played from the move log held in the gamedata class
        #2. Updating the chessboard object (for piece moving back)
        #3. Recover the captured piece (if there is one for that turn)
        #4. De-castle (if necessary)
        #5. De-promote (if necessary)
        #6. Flipping the current turn
        #7. Updating the gamedata object
        global current_turn

        #1.
        previous_move = gamedata.pop_move_log()
        start_square = previous_move[1]
        end_square = previous_move[0]

        #2.
        chessboard.update(start_square,end_square,True)

        #3.
        recovered_piece = gamedata.pop_capture_log()  #obtains the object of the last captured piece (if any)
        if recovered_piece != '.':
            chessboard.add_new_object(start_square,recovered_piece)

        #4.
        piece_object = chessboard.class_dictionary[(end_square[0],end_square[1])] #object of piece moving back
        if type(piece_object).__name__ == 'king':  #if the piece_object moved is the king
            move_engine.undo_move_king(start_square,end_square,piece_object)

        #5.
        move_engine.check_depromote(end_square,piece_object)

        #6.
        current_turn = appendices.flip_current_turn(current_turn)

        #7.
        gamedata.update(chessboard.digital_board,current_turn,chessboard.class_dictionary,(start_square,end_square),True)

class post_game:
    def __init__(self):
        self.evaluation_queue = [0]
        self.player_colour = ''
        self.standard_moves = 0
        self.strong_moves = 0
        self.blunder_moves = 0

    def push_evaluation_queue(self,is_checkmate_or_stalemate,winner,evaluation):
        if is_checkmate_or_stalemate:
            if winner == 'w':
                self.evaluation_queue.append(MAX_SCORE)
            elif winner == 'b':
                self.evaluation_queue.append(MIN_SCORE)
            else:
                self.evaluation_queue.append(0)
        else:
            self.evaluation_queue.append(evaluation)

    def pop_evaluation_queue(self):
        self.evaluation_queue.pop()

    def evaluate_all_player_moves(self):
        if self.player_colour == 'w':
            player_move_sync = 1 #every odd index in the queue is an evaluation for white
        else:
            player_move_sync = 0 #every even index (other than index 0) in the queue is an evaluation for black

        for move_number in range(len(self.evaluation_queue)):
            if move_number % 2 == player_move_sync and move_number != 0: #player made move at said 'move number'
                self.evaluate_single_player_move(move_number)

    def evaluate_single_player_move(self,move_number):
        if move_number == len(self.evaluation_queue) -1: #final move
            player_evaluation = self.evaluation_queue[move_number]
            if self.player_colour == 'b': #if player is black, a negative score after is good
                player_evaluation *= -1
        else:
            player_evaluation = self.find_evaluation_difference(move_number-1,move_number+1)

        if player_evaluation > 3:
            self.strong_moves += 1
        elif player_evaluation < -5:
            self.blunder_moves += 1
        else:
            self.standard_moves += 1

    def find_evaluation_difference(self,ai_move_before,ai_move_after):
        ai_evaluation_before = self.evaluation_queue[ai_move_before]
        ai_evaluation_after = self.evaluation_queue[ai_move_after]

        evaluation_difference = ai_evaluation_after-ai_evaluation_before
        if self.player_colour == 'b': #if player is black, a negative score after is good
            evaluation_difference *= -1

        return evaluation_difference

    def display(self,move_count,winner):
        screen.fill(GREY)
        self.display_game_over()
        self.display_winner(winner)
        self.display_game_length(move_count)
        self.display_move_analysis()

    def display_game_over(self):
        game_over_surface,game_over_rect = appendices.text_schematic('GAME OVER',360,50,80,WHITE,'centre')
        underline_rect = pygame.Rect(game_over_rect.left,game_over_rect.bottom,game_over_rect.width,20)
        pygame.draw.rect(screen,WHITE,underline_rect,2)
        screen.blit(game_over_surface,game_over_rect)

    def display_winner(self,winner):
        #if statements ensure that 'winner' is written in full
        if winner == 'w':
            winner = 'White'
        elif winner == 'b':
            winner = 'Black'
        else: #stalemate
            winner = 'Draw'

        winner_surface,winner_rect = appendices.text_schematic('Winner: ' + winner,100,150,40,WHITE,'topleft')
        screen.blit(winner_surface,winner_rect)

    def display_game_length(self,move_count):
        game_length_surface,game_length_rect = appendices.text_schematic('Length of game: '+str(move_count)+' moves',100,250,40,WHITE,'topleft')

        screen.blit(game_length_surface,game_length_rect)

    def display_move_analysis(self):
        #displaying the standard move count
        standard_move_surface, standard_move_rect = appendices.text_schematic('Standard moves: ' + str(self.standard_moves),100,350,40,WHITE,'topleft')
        screen.blit(standard_move_surface,standard_move_rect)

        #displaying the strong move count
        strong_move_surface, strong_move_rect = appendices.text_schematic('Strong moves: ' + str(self.strong_moves),100,450,40,WHITE,'topleft')
        screen.blit(strong_move_surface, strong_move_rect)

        # displaying the blunder move count
        blunder_move_surface, blunder_move_rect = appendices.text_schematic('blunder moves: ' + str(self.blunder_moves),100, 550, 40, WHITE, 'topleft')
        screen.blit(blunder_move_surface,blunder_move_rect)

#instantiating classes
main_menu = main_menu()
chessboard = chessboard()
gamedata = gamedata()
ai = AI(move_engine,gamedata,chessboard)
post_game_report = post_game()

piece_images_dictionary = appendices.map_piece_to_image()
pos_to_square_dictionary = appendices.map_pos_to_square()

def main(): #main game loop
    global mouse_pos,current_turn,game_active
    move_data = [] #contains 2 tuples: location of start and end squares clicked by the user
    while True:
        mouse_pos = (0,0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #close window
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and game_active:
                if event.key == pygame.K_u: # 'U' key is pressed = U = Undo move
                    if len(gamedata.move_log_stack) != 0 and len(gamedata.move_log_stack) != 1:
                        #cannot undo a move if no moves have taken place

                        move_engine.undo_move()
                        post_game_report.pop_evaluation_queue()
                        move_engine.undo_move() #called twice as A.I move also needs to be undone
                        post_game_report.pop_evaluation_queue()
                        move_data = []
                        game_active = True
                elif event.key == pygame.K_h and chessboard.hint_move == []: # 'H' key is pressed = H = Show hint
                    chessboard.hint_move = ai.generate_move(True)

            if event.type == pygame.MOUSEBUTTONDOWN: #user click
                mouse_pos = pygame.mouse.get_pos()
                if game_active:
                    clicked_pos = appendices.get_col_row_from_pos(mouse_pos[0],mouse_pos[1])
                    if move_data == []:
                        move_data.append(clicked_pos)
                    else:
                        if clicked_pos == move_data[0]: #same square is clicked twice: deselect
                            move_data = []
                        else:
                            move_data.append(clicked_pos)

        if not game_active: #display main menu/post_game_report if false, display game if true
            if gamedata.is_checkmate or gamedata.is_stalemate: #after game is finished
                post_game_report.display(gamedata.move_count,gamedata.winner)
            else: #before game begins
                main_menu.display()
        else: #game is active, display chessboard
            chessboard.display_board(MINT,ARCTIC)
            if current_turn != gamedata.player_colour: #AI's turn
                move_data = ai.generate_move()
                move_data = move_engine.initiate_move(move_data)

                if gamedata.is_checkmate or gamedata.is_stalemate:
                    post_game_report.push_evaluation_queue(True, gamedata.winner, 'filler')
                    post_game_report.evaluate_all_player_moves()
                    game_active = False
                else:
                    post_game_report.push_evaluation_queue(False,'filler',ai.evaluation_function(chessboard.digital_board))

            if len(move_data) == 1: #user has clicked on a square once
                available_moves = chessboard.display_valid_moves(move_data[0])
            elif len(move_data) == 2:
                if move_data in available_moves:
                    #if the second square clicked is a possible destination from the first

                    move_data = move_engine.initiate_move(move_data)
                    chessboard.hint_move = []
                    chessboard.display_board(MINT,ARCTIC) #update board
                    if gamedata.is_checkmate or gamedata.is_stalemate:
                        post_game_report.push_evaluation_queue(True,gamedata.winner,'filler')
                        post_game_report.evaluate_all_player_moves()
                        game_active = False
                    else:
                        post_game_report.push_evaluation_queue(False,'filler',ai.evaluation_function(chessboard.digital_board))
                else: #if the second square clicked is independent from the first
                    move_data.pop(0) #have the second square chosen be the first square now
                    #this also handles the situation when the first square by user is 'invalid'. If invalid,
                    #available_moves will empty, so when the second item of move_data is entered, the first
                    #invalid item will ALWAYS be popped

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()