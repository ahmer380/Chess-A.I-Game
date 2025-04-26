from pieces import check_for_checks

class gamedata: #this class stores all important information for the game that will be played
    def __init__(self):
        self.difficulty = '' #must be uppercase - first letter
        self.player_colour = ''  # one letter, w or b
        self.ai_colour = ''

        self.white_king_pos = (7,4)
        self.black_king_pos = (0,4)
        self.game_phase = 'Opening'  # o = opening, m = middlegame, e = endgame
        self.move_count = 0

        self.is_check = False
        self.check_change = False #if there was no check more before but now after/vice versa

        self.is_checkmate = False
        self.is_stalemate = False

        self.white_move_list = []
        self.black_move_list = []
        self.current_valid_move_list = []

        self.move_log_stack = []
        self.capture_log_stack = []

        self.winner = ''

    def update(self,board,colour,class_dictionary,move_data,is_undo):
        #this method will be called after every move is completed, and inspects and updates
        #most of its attributes (if necessary)
        #colour of player who has made move
        self.set_is_check(board)
        self.obtain_all_valid_moves(board,colour,class_dictionary,move_data)

        if not is_undo: #regular move
            self.move_count += 1
            self.push_move_log(move_data)
            self.current_valid_move_list = self.order_moves(board)
        else: #undo command
            self.move_count -= 1

        self.update_gamestate(colour)
        self.game_phase = self.update_gamephase(class_dictionary)

    def obtain_all_valid_moves(self,board,colour,class_dictionary,move_data):
        self.white_move_list = []
        self.black_move_list = []
        self.current_valid_move_list = []  #all moves of the next player AFTER the current move is made

        changed_pieces = self.obtain_changed_pieces(board,colour,move_data)

        if changed_pieces == 'all':
            changed_pieces = class_dictionary.keys() #all  pieces to be changed

        for piece_pos in changed_pieces: #all pieces which their move list may have changed
            piece_object = class_dictionary[piece_pos]
            if piece_object.colour == 'w':
                king_pos = self.white_king_pos
            else:
                king_pos = self.black_king_pos

            ignore = piece_object.calculate_moves(board,king_pos)
            #method call modifies the 'valid_move_list' attribute for the piece, which is what we want

        for piece_pos in class_dictionary:
            piece_object = class_dictionary[piece_pos]
            piece_move_list = piece_object.valid_move_list
            if len(piece_move_list) != 0:
                if piece_object.colour == 'w':
                    for move in piece_move_list:
                        self.white_move_list.append(move)
                else:
                    for move in piece_move_list:
                        self.black_move_list.append(move)

        # we want all moves of the next player AFTER the current move is made
        if colour == 'w': #after white's turn, black move now
            self.current_valid_move_list = self.black_move_list
        else: #after black's turn, white move now
            self.current_valid_move_list = self.white_move_list

    def obtain_changed_pieces(self,board,colour,move_data):
        # this method obtains a record of every single piece which needs to have its moves re-evaluated
        # after a move made
        if move_data == 'first move': #first move
            return 'all'

        start_square = move_data[0]
        end_square = move_data[1]

        if colour == 'w':
            enemy_colour = 'b'
            friendly_king_pos = self.white_king_pos
            enemy_king_pos = self.black_king_pos
        else:
            enemy_colour = 'w'
            friendly_king_pos = self.black_king_pos
            enemy_king_pos = self.white_king_pos

        #if to/from check, or king has moved, search all piece moves
        if board[end_square[0]][end_square[1]][1] == 'K' or self.is_check or self.check_change:
            return 'all' #the signal that all pieces need to be re-evaluated for

        changed_squares = {move_data[1]}
        #destination square obviously needs to have its move re-evaluated

        for square in move_data: #iterate through start and end squares
            changed_squares = changed_squares | set(check_for_checks(board,'w',square,True))
            #gets the location of all pieces that can jump to 'square' in a single move
            #colour irrelevant in call, '|' means union

            changed_squares = changed_squares | set(get_pawn_change_squares(board,square))
            #all pawns that MAY be changed are added (as a precaution )

            in_between_pieces_attacking = get_in_between_squares_attacking(board,enemy_colour,list(square),list(enemy_king_pos))
            if len(in_between_pieces_attacking) == 1: #only 1 piece between king an enemy piece, may be (un)pinned
                changed_squares = changed_squares | set(in_between_pieces_attacking)

            in_between_pieces_defending = get_in_between_squares_defending(board,colour,list(square),list(friendly_king_pos))
            changed_squares = changed_squares | set(in_between_pieces_defending)

        changed_squares = changed_squares | {enemy_king_pos}

        return list(changed_squares)

    def order_moves(self,board):
        ordered_move_queue = []
        capturing_moves = []
        central_moves = []
        king_moves = []
        remaining_moves = []

        central_squares = [(3,3),(3,4),(4,3),(4,4)]

        for move in self.current_valid_move_list:
            start_square = move[0]
            piece_in_start_square = board[start_square[0]][start_square[1]]
            end_square = move[1]
            piece_in_end_square = board[end_square[0]][end_square[1]]

            if piece_in_end_square != '00': #if move is a capturing move
                capturing_moves.append(move)
            elif end_square in central_squares: #if piece is moving to centre
                central_moves.append(move)
            elif piece_in_start_square[1] == 'K': #if the king is moving
                king_moves.append(move)
            else: #all other moves that were not any of the above
                remaining_moves.append(move)

        for capturing_move in capturing_moves:
            ordered_move_queue.append(capturing_move) #enqueue capturing moves first
        for central_move in central_moves:
            ordered_move_queue.append(central_move) #enqueue central moves second
        for remaining_move in remaining_moves:
            ordered_move_queue.append(remaining_move) #enqueue remaining moves third
        for king_move in king_moves:
            ordered_move_queue.append(king_move) #enqueue king moves last

        return ordered_move_queue

    def update_gamestate(self,colour): #searches if there is a check/checkmate/stalemate
        self.winner = ''
        self.is_checkmate = False
        self.is_stalemate = False

        if len(self.current_valid_move_list) == 0: #game has ended
            if self.is_check: #discovered earlier in another subroutine
                self.is_checkmate = True

                if colour == 'w':  # white's turn when move was made
                    self.winner = 'w'
                else:  # black's turn when move was made
                    self.winner = 'b'
                    #print('Black wins!')

            else:
                self.is_stalemate = True

    def update_gamephase(self,class_dictionary):
        white_king_object = class_dictionary[self.white_king_pos]
        black_king_object = class_dictionary[self.black_king_pos]

        if self.move_count < 10 and not(white_king_object.castled and black_king_object.castled):
            return 'Opening'

        major_piece_count = 0
        for piece_object in class_dictionary:
            piece_name = type(class_dictionary[piece_object]).__name__
            if piece_name != 'king' and piece_name != 'pawn': #if the piece is major
                major_piece_count += 1

        if major_piece_count > 3:
            return 'Middlegame'

        return 'Endgame'

    def set_is_check(self,board):
        if check_for_checks(board,'w',self.white_king_pos) or check_for_checks(board,'b',self.black_king_pos):
            #check the safety of both kings

            self.is_check = True
        else:
            self.is_check = False

        self.check_change = False

        if check_for_checks(board,'w',self.white_king_pos) or check_for_checks(board,'b',self.black_king_pos):
            #check the safety of both kings
            if not self.is_check:
                self.check_change = True

            self.is_check = True
        else:
            if self.is_check:
                self.check_change = True

            self.is_check = False

    def log_captured_piece(self,capturing_square,class_dictionary): #capturing square = end square
        if (capturing_square[0],capturing_square[1]) in class_dictionary:
            #if there is an object at the end square, not empty

            captured_piece = class_dictionary[(capturing_square[0],capturing_square[1])]
            self.push_capture_log(captured_piece)
            #object of captured piece is saved into the log (including its unique properties)
            #can be re-gathered and re-implemented into the game at any time
        else:
            self.push_capture_log('.') # '.' means that no piece was captured this turn

    def push_capture_log(self,captured_piece):
        self.capture_log_stack.append(captured_piece)

    def pop_capture_log(self):
        return self.capture_log_stack.pop()

    def push_move_log(self,move_data):
        self.move_log_stack.append(move_data)

    def pop_move_log(self):
        return self.move_log_stack.pop()

def get_difference_vector(target_square,king_pos):
    row_gain = target_square[0] - king_pos[0]
    col_gain = target_square[1] - king_pos[1]
    if not (abs(col_gain) == abs(row_gain) or col_gain == 0 or row_gain == 0):
        return [] #target square is not diagonal or straight relative to the king, i.e. no in between squares

    if row_gain == 0:
        row_vector = 0
    else:
        row_vector = row_gain // abs(row_gain)
    if col_gain == 0:
        col_vector = 0
    else:
        col_vector = col_gain // abs(col_gain)

    #difference_vector such that king_pos + difference_vector*k = target_square
    #where k = no.squares in between the two squares + 1
    difference_vector = (row_vector,col_vector)

    return difference_vector

def get_in_between_squares_attacking(board,colour,target_square,king_pos):
    in_between_pieces = []
    difference_vector = get_difference_vector(target_square,king_pos)
    if difference_vector == []:
        return [] #no pins as target square not in straight line relative to king

    while king_pos != target_square:
        king_pos[0] += difference_vector[0]
        king_pos[1] += difference_vector[1]
        if board[king_pos[0]][king_pos[1]][0] == colour:
            in_between_pieces.append((king_pos[0],king_pos[1]))

    return in_between_pieces

def get_in_between_squares_defending(board,colour,target_square,king_pos):
    in_between_pieces = []
    difference_vector = get_difference_vector(target_square,king_pos)
    if difference_vector == []:
        return [] #no pins as target square not in straight line relative to king

    while 0 <= king_pos[0] <= 7 and 0 <= king_pos[1] <= 7:
        if board[king_pos[0]][king_pos[1]][0] == colour:
            in_between_pieces.append((king_pos[0],king_pos[1]))

        elif board[king_pos[0]][king_pos[1]] != '00': #enemy piece between target square/king - potential pin
            in_between_pieces.pop(0)  #remove first item (the king), as we do not want to count it
            return in_between_pieces

        king_pos[0] += difference_vector[0]
        king_pos[1] += difference_vector[1]

    return [] #no enemy piece between the target square and king inclusive - no threat

def get_pawn_change_squares(board,target_square):
    changed_pawns = [] #stores the squares which contains pawns that can move directly to 'target_square'
    movement_vectors = [(-1,1),(-1,-1),(-1,0),(-2,0), (1,1),(1,-1),(1,0),(2,0)] #movement vectors for pawns
    # 1-4: white pawns|5-8: black pawns

    for vector_no,vector in enumerate(movement_vectors):
        new_row,new_col = target_square[0]+vector[0], target_square[1]+vector[1]
        if 0 <= new_row <= 7 and 0 <= new_col <= 7:
            if board[new_row][new_col][1] == 'p':
                if board[new_row][new_col][0] == 'b' and 0 <= vector_no <= 3:
                    #black pawn (which move DOWN) diagonally or vertically ABOVE the square
                    changed_pawns.append((new_row,new_col))
                elif board[new_row][new_col][0] == 'w' and 4 <= vector_no <= 7:
                    #white pawn (which move UP) diagonally or vertically BELOW the square
                    changed_pawns.append((new_row,new_col))

    return changed_pawns