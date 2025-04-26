from copy import deepcopy
from constants import MAX_SCORE

def check_for_checks(board,colour,king_pos,get_changed_squares = False):
    changed_squares = []
    king_row,king_col = king_pos
    #king_pos: position of the king to be inspected
    #colour: colour of the king to be inspected

    #For each possible vector traverse direction. If the matching opposite piece is within the path return
    #True (king is being checked)

    piece_vectors = [(1,0),(0,1),(-1,0),(0,-1), (1,1),(1,-1),(-1,1),(-1,-1),
                     (1,2),(2,1),(-1,2),(2,-1),(1,-2),(-2,1),(-1,-2),(-2,-1)]
    #1-4: rook,queen,king|5-8: bishop,queen,king|9-16: knight

    for vector_no,vector in enumerate(piece_vectors):
        row_vector,col_vector = vector[0],vector[1]
        king_new_row,king_new_col = king_row + row_vector, king_col + col_vector

        if 0 <= king_new_row <= 7 and 0 <= king_new_col <= 7:
            if (0 <= vector_no <= 7) and board[king_new_row][king_new_col][1] == 'K':
                changed_squares.append((king_new_row,king_new_col))
                if board[king_new_row][king_new_col][0] != colour and not get_changed_squares:
                    return True  # if an enemy king is adjacent to the king
            elif (8 <= vector_no <= 15) and board[king_new_row][king_new_col][1] == 'N':
                changed_squares.append((king_new_row, king_new_col))
                if board[king_new_row][king_new_col][0] != colour and not get_changed_squares:
                    return True  # if an enemy knight is an 'L' shaped distance away from the king
            if 8 <= vector_no <= 15:
                continue  # vectors 9-16 are only for knights, so the code below can be skipped

        # while loop to check for ranged pieces only
        while 0 <= king_new_row <= 7 and 0 <= king_new_col <= 7:
            if board[king_new_row][king_new_col] != '00':  # if not an empty square
                if (0 <= vector_no <= 3) and (board[king_new_row][king_new_col][1] == 'R' or board[king_new_row][king_new_col][1] == 'Q'):
                    changed_squares.append((king_new_row,king_new_col))
                    if board[king_new_row][king_new_col][0] != colour and not get_changed_squares: #enemy piece
                        return True  # if an enemy queen/rook is horizontal or vertical to the king
                elif (4 <= vector_no <= 7) and (board[king_new_row][king_new_col][1] == 'B' or board[king_new_row][king_new_col][1] == 'Q'):
                    changed_squares.append((king_new_row,king_new_col))
                    if board[king_new_row][king_new_col][0] != colour and not get_changed_squares: #enemy piece
                        return True  # if an enemy queen/bishop is diagonal to the king
                break

            #for each direction, keep traversing the paths for the king until the square is outside the board,
            #or there is a piece blocking the direction (also examine said piece)
            king_new_row += row_vector
            king_new_col += col_vector

    if get_changed_squares:
        return changed_squares

    # check if pawns are attacking
    if colour == 'w':
        row_vector = -1 #black pawns will be on the top end of the board
    else:
        row_vector = 1 #white pawns will be on the bottom end of the board

    if 0 <= king_row + row_vector <= 7:
        col_vectors = [1,-1]
        for col in col_vectors:
            if 1 <= king_col + col <= 7:
                if board[king_row + row_vector][king_col + col][0] != colour:
                    if board[king_row + row_vector][king_col + col][1] == 'p':
                        return True

    return False  # no checks identified

class chesspiece:
    def __init__(self,colour,position,signature,is_promoted,value):
        self.initial = colour[0]+signature
        self.colour = colour[0] #first letter of colour is used ('w' = white, 'b' = black)
        self.position = position
        self.move_count = 0
        self.is_promoted = is_promoted #If 'True', the chess piece is stemmed from a promoted pawn
        self.valid_move_list = []

        if self.colour == 'w':
            self.value = value
        elif self.colour == 'b': #black pieces possess negative value
            self.value = value * -1

    def calculate_moves(self,vectors,board,is_range,king_pos):
        #this method will be overridden by most of its sub-classes
        valid_moves = [] #each piece of data will contain:(start_square,end_square),start_square = self.position
        row,col = self.position

        for vector in vectors:
            row_vector,col_vector = vector[0],vector[1]
            new_row,new_col = row+row_vector,col+col_vector

            if not is_range: #used for the king and knights, as they do not possess range
                if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                    if board[new_row][new_col][0] != self.colour:
                    #ensures that the new position isn’t already occupied by a piece of the same colour
                        if not self.is_checks(board,(new_row,new_col),king_pos):
                            start_square = tuple(self.position)
                            end_square = (new_row,new_col)
                            valid_moves.append([start_square,end_square])

            else: #used for the queen, rook and bishop, as they do possess range
                while 0 <= new_row <= 7 and 0 <= new_col <= 7:
                    if board[new_row][new_col] != '00': #if not an empty square
                        if board[new_row][new_col][0] != self.colour: #if it is an enemy piece
                            if not self.is_checks(board,(new_row,new_col),king_pos):
                                start_square = tuple(self.position)
                                end_square = (new_row,new_col)
                                valid_moves.append([start_square,end_square])
                        break

                    if not self.is_checks(board,(new_row,new_col),king_pos):
                        start_square = tuple(self.position)
                        end_square = (new_row,new_col)
                        valid_moves.append([start_square,end_square])
                    new_row += row_vector
                    new_col += col_vector

        return valid_moves

    def is_checks(self,board,end_square,king_pos):
        #ensures that a potential valid move will NOT leave its own king being exposed

        duplicate_board = deepcopy(board)
        #this variable will be tweaked without changing the contents of the original board

        #Make the move on the duplicate board
        duplicate_board[end_square[0]][end_square[1]] = duplicate_board[self.position[0]][self.position[1]]
        duplicate_board[self.position[0]][self.position[1]] = '00'

        if duplicate_board[end_square[0]][end_square[1]][1] == 'K':
            king_pos = end_square[0],end_square[1] #position of king needs to be updated if king is moving

        return check_for_checks(duplicate_board,self.colour,king_pos)

class rook(chesspiece):
    value = None

    def __init__(self,colour,position,is_promoted_piece = False):
        super().__init__(colour,position,'R',is_promoted_piece,rook.value)

    def calculate_moves(self,board,king_pos):
        rook_vectors = [(1,0),(0,1),(-1,0),(0,-1)] #movement patterns for a rook
        self.valid_move_list = super().calculate_moves(rook_vectors,board,True,king_pos)
        return self.valid_move_list

class bishop(chesspiece):
    value = None

    def __init__(self,colour,position,is_promoted_piece = False):
        super().__init__(colour,position,'B',is_promoted_piece,bishop.value)

    def calculate_moves(self,board,king_pos):
        bishop_vectors = [(1,1),(1,-1),(-1,1),(-1,-1)] #movement patterns for a bishop
        self.valid_move_list = super().calculate_moves(bishop_vectors,board,True,king_pos)
        return self.valid_move_list

class queen(chesspiece):
    value = None

    def __init__(self,colour,position,is_promoted_piece = False):
        super().__init__(colour,position,'Q',is_promoted_piece,queen.value)

    def calculate_moves(self,board,king_pos): #queen_moves = rook_moves + bishop_moves
        queen_vectors = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        self.valid_move_list = super().calculate_moves(queen_vectors,board,True,king_pos)
        return self.valid_move_list

class knight(chesspiece):
    value = None

    def __init__(self,colour,position,is_promoted_piece = False):
        super().__init__(colour,position,'N',is_promoted_piece,knight.value)

    def calculate_moves(self,board,king_pos):
        knight_vectors = [(1,2),(2,1),(-1,2),(2,-1),(1,-2),(-2,1),(-1,-2),(-2,-1)]
        self.valid_move_list = super().calculate_moves(knight_vectors,board,False,king_pos)
        return self.valid_move_list

class king(chesspiece):
    value = MAX_SCORE #99999999

    def __init__(self,colour,position,is_promoted_piece = False):
        super().__init__(colour,position,'K',is_promoted_piece,king.value)
        self.castled = False

    def calculate_moves(self,board,king_pos):
        king_vectors = [(1,0),(0,1),(0,-1),(-1,0),(1,-1),(-1,1),(1,1),(-1,-1)]
        standard_moves = super().calculate_moves(king_vectors,board,False,king_pos)
        castling_moves = self.castle(board,king_pos)
        self.valid_move_list = castling_moves + standard_moves
        return self.valid_move_list

    def castle(self,board,king_pos):
        castling_moves = []
        if self.move_count != 0: #illegal to castle if king has already moved
            return castling_moves

        row = self.position[0] #only row is required

        #castling queen side
        if (board[row][1] == '00') and (board[row][2] == '00') and (board[row][3] == '00'):
            #checks if squares between rook (queen side) and king are empty

            if board[row][0] == self.colour + 'R': #if rook on edge is same colour to king
                end_square = (row,2)
                if not self.is_checks(board, end_square,king_pos):
                    start_square = tuple(self.position)
                    castling_moves.append([start_square,end_square]) #add castle queen side to castling_moves

        #castling king side
        if (board[row][5] == '00') and (board[row][6] == '00'):
            # checks if squares between rook (king side) and king are empty

            if board[row][7] == self.colour + 'R':
                end_square = (row,6)
                if not self.is_checks(board,end_square,king_pos):
                    start_square = tuple(self.position)
                    castling_moves.append([start_square,end_square]) #add castle king side to castling moves

        return castling_moves

class pawn(chesspiece):
    value = None

    def __init__(self,colour,position,is_promoted_piece = False):
        super().__init__(colour,position,'p',is_promoted_piece,pawn.value)
        self.capture_move_list = [] #used to evaluate centre control

    def calculate_moves(self,board,king_pos):
        if self.colour == 'w': #white pawns move up the board
            row_vector = -1
        else: #black pawns move down the board
            row_vector = 1

        standard_moves = self.move_vertical(board,row_vector,king_pos) #pawn is only moving vertically, no capturing
        self.capture_move_list = self.capture(board,row_vector,king_pos) #pawn is moving diagonally, capturing

        self.valid_move_list = self.capture_move_list + standard_moves
        return self.valid_move_list

    def move_vertical(self,board,row_vector,king_pos):
        standard_moves = []
        row,col = self.position
        new_row = row+row_vector

        if board[new_row][col] == '00': #checks if square in front is empty
            if not self.is_checks(board,(new_row,col),king_pos):
                start_square = tuple(self.position)
                end_square = (new_row,col)
                standard_moves.append([start_square,end_square])
        else:
            return standard_moves #no need to look further if square in front is blocked

        if self.move_count == 0: #first move
            new_row = row+(row_vector*2)
            if board[new_row][col] == '00':
                if not self.is_checks(board,(new_row,col),king_pos):
                    start_square = tuple(self.position)
                    end_square = (new_row,col)
                    standard_moves.append([start_square,end_square])

        return standard_moves

    def capture(self,board,row_vector,king_pos,centre_scanning = False):
        central_moves = []
        capture_moves = []
        row,col = self.position
        new_row = row+row_vector
        col_vectors = [-1,1]

        for col_vector in col_vectors:
            new_col = col+col_vector
            if 0 <= new_col <= 7 and 0 <= new_row <= 7:
                start_square = tuple(self.position)
                end_square = (new_row,new_col)

                if centre_scanning: #doesn't matter whether diagonal square is filled or not
                    central_moves.append([start_square,end_square])
                else:
                    if board[new_row][new_col] != '00':  #if not an empty square
                        if board[new_row][new_col][0] != self.colour: #if it is an enemy piece
                            if not self.is_checks(board,end_square,king_pos):
                                capture_moves.append([start_square,end_square])

        if centre_scanning:
            return central_moves

        return capture_moves

    def check_for_promote(self):
        #called every time a pawn is moved. If pawn at end row, then it should promote

        current_row = self.position[0]
        if self.colour == 'w': #the top row is the row where white pawns promote
            opposite_row = 0
        else: #the bottom row is the row where black pawns promote
            opposite_row = 7
        if current_row == opposite_row: #pawn is at opposite row of board
            return True

        return False