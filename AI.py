from constants import MAX_SCORE,MIN_SCORE

class AI:
    def __init__(self,move_engine_class,gamedata_object,chessboard_object):
        self.gamedata_object = gamedata_object
        self.chessboard_object = chessboard_object
        self.move_engine = move_engine_class
        self.ai_colour = self.gamedata_object.ai_colour
        self.difficulty_depth = 0 #not defined yet
        self.hint_depth = 3  # highest depth available: we want most accurate move as hint for user
        self.max_depth = 0 #changes per minimax call - depending on whether minimax call is normal or for hint

        self.best_move = [] #stores only a single tuple - the best move currently found by minimax

    def initialize_depth(self): #called after user picks difficulty from main menu
        if self.gamedata_object.difficulty == 'Expert':
            self.difficulty_depth = 3
        elif self.gamedata_object.difficulty == 'Intermediate':
            self.difficulty_depth = 2
        else: #difficulty = beginner
            self.difficulty_depth = 1

    def generate_move(self,generate_hint = False):
        self.best_move = []

        if self.gamedata_object.ai_colour == 'w': #white = maximizing
            is_maximising = True
        else: #black = minimizing
            is_maximising = False

        if generate_hint:
            is_maximising = not is_maximising #e.g. if A.I = white, player = black, so needs to be False
            self.max_depth = self.hint_depth #highest depth available: we want most accurate move as hint for user
        else:
            self.max_depth = self.difficulty_depth #depends on difficulty of A.I

        #call minimax
        score = self.minimax(self.chessboard_object.digital_board,is_maximising,self.max_depth,MIN_SCORE,MAX_SCORE)
        #we don't actually need the score, but may be handy for testing later

        best_move = self.best_move #the best_move attribute is altered during the evaluation function
        return best_move

    def evaluation_function(self,board):
        material_score = 0
        centre_control_score = 0
        pawn_structure_score = 0

        '''
        • loop through every square on board. For each square:
        #1. Add/subtract to material score (if there is a piece on the square)
        #2. Add/subtract to centre control score if piece controls any central squares
        #3. Add/subtract to pawn structure score if piece is a pawn (evaluate its position)
        
        • Afterwards, evaluate the safety of the white and black kings, which comprise the king safety score
        
        • Calculate the weights of each components, depending on the phase of the game
        '''

        for row_pos,row in enumerate(board): #index of position also obtained using enumerate
            for col_pos,piece in enumerate(row):
                if piece != '00':
                    piece_object = self.chessboard_object.class_dictionary[(row_pos,col_pos)]
                    material_score += self.evaluate_material_score(piece_object)
                    centre_control_score += self.evaluate_centre_control(piece_object)
                    pawn_structure_score += self.evaluate_pawn_structure(board,piece_object)

        king_safety_score = self.evaluate_king_safety(board)
        total_score = self.calculate_total_score(material_score,centre_control_score,pawn_structure_score,king_safety_score)

        return total_score

    def evaluate_material_score(self,piece_object):
        return piece_object.value

    def evaluate_centre_control(self,piece_object):
        central_squares = [(3,3),(3,4),(4,3),(4,4)]
        piece_in_centre_bonus = 6 #values tweaked for optimisation
        pawn_controlling_centre_bonus = 5
        non_pawn_controlling_centre_bonus = 2

        if piece_object.colour == 'w':
            row_vector = -1
            multiplier = 1
        else: #Black piece
            row_vector = 1
            multiplier = -1

        if tuple(piece_object.position) in central_squares: #if the piece is already in the centre
            return piece_in_centre_bonus * multiplier

        if type(piece_object).__name__ == 'pawn':  #pawns are more valuable to control centre, thus more points
            value = pawn_controlling_centre_bonus
            watched_squares = piece_object.capture('filler',row_vector,'filler',True)
            #pawns can only control squares diagonal to them, which is why we use the capture method
        else:
            value = non_pawn_controlling_centre_bonus
            #other pieces score less points than pawns if they control the centre
            watched_squares = piece_object.valid_move_list

        for square in watched_squares:
            if square[1] in central_squares: #if one of the destination squares is a central square
                return value * multiplier

        return 0 #pieces is not controlling any central squares

    def evaluate_pawn_structure(self,board,piece_object):
        if type(piece_object).__name__ != 'pawn': #no need to be evaluated if piece is not a pawn
            return 0

        pawn_structure_score = 0 #valuestweaked for optimisation
        pawn_island_penalty = -1
        double_pawn_penalty = -3 #each pawn on same row e.g. 3 pawns on same row = -6
        pawn_island = True

        if piece_object.colour == 'w':
            multiplier = 1
        else: #Black piece
            multiplier = -1

        row,col = piece_object.position
        surrounding_squares = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

        for square in surrounding_squares:
            new_row,new_col = row+square[0],col+square[1]
            if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                if board[new_row][new_col] == piece_object.initial:
                    #this means that there is a friendly pawn next to this one, NOT isolated
                    pawn_island = False
                    break

        if pawn_island:
            pawn_structure_score += pawn_island_penalty

        while row < 7: #only need to look one way, if its below one pawn, then its above another pawn
            if board[row+1][col] == piece_object.initial: #another pawn on same row, doubled (or worse)
                pawn_structure_score += double_pawn_penalty
                break
            row += 1

        return pawn_structure_score * multiplier

    def evaluate_king_safety(self,board):
        king_safety_score = 0

        white_king_pos = self.gamedata_object.white_king_pos
        white_king_object = self.chessboard_object.class_dictionary[white_king_pos]
        black_king_pos = self.gamedata_object.black_king_pos
        black_king_object = self.chessboard_object.class_dictionary[black_king_pos]

        col_vectors = [-1,0,1]
        castling_bonus = 3 #tweaked for optimisation
        pawn_shield_bonus = 1 #per pawn

        #deduce if kings have yet castled
        if white_king_object.castled: #white king has castled
            king_safety_score += castling_bonus
        if black_king_object.castled: #black king has castled
            king_safety_score -= castling_bonus

        #checking the presence of pawn shield
        for col_vector in col_vectors:
            #check the white pawn shield first
            new_row = white_king_pos[0] - 1
            new_col = white_king_pos[1] + col_vector
            if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                if board[new_row][new_col] == 'wp':
                    king_safety_score += pawn_shield_bonus

            #now check the black pawn shield
            new_row = black_king_pos[0] + 1
            new_col = black_king_pos[1] + col_vector
            if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                if board[new_row][new_col] == 'bp':
                    king_safety_score -= pawn_shield_bonus

        return king_safety_score

    def calculate_total_score(self,material_score,centre_control_score,pawn_structure_score,king_safety_score):
        multipliers = {'Opening':[3,0.2,0.3,0.1],'Middlegame':[3,0.1,0.6,0.15],'Endgame':[3,0,1,0]}
        #multipliers tweaked for optimisation
        #multipliers left to right: material score, centre control, pawn_structure, king safety

        material_multiplier,centre_control_multiplier,pawn_structure_multiplier,king_safety_multiplier = \
        multipliers[self.gamedata_object.game_phase]

        material_score *= material_multiplier
        centre_control_score *= centre_control_multiplier
        pawn_structure_score *= pawn_structure_multiplier
        king_safety_score *= king_safety_multiplier

        total_score = material_score + centre_control_score + pawn_structure_score + king_safety_score
        total_score = round(total_score,2)

        return total_score

    def minimax(self,board,is_maximising,depth,alpha,beta): #board = the main board object
        # A.I is maximising and wants highest score if white,minimizing and wants lowest score if black

        if self.gamedata_object.is_checkmate: #game has ended - return score
            if self.gamedata_object.winner == 'w': #white wins
                score = MAX_SCORE
            elif self.gamedata_object.winner == 'b': # black wins
                score = MIN_SCORE
            else: #stalemate
                score = 0

            return score

        if depth == 0: #maximum depth reached
            return self.evaluation_function(board) #Evaluate the current board and find its current score

        '''
            Iterate through all available moves. For each move, apply the following steps:
            step 1. Perform the move on the board
            step 2. Call the function recursively, decrementing the depth and flipping the isMaximising variable
            step 3. Undo the move on the board
            step 4. If the score is higher/lower than the best score (depending on who is maximising), 
            replace the best score and store that move (if move is at highest depth)
            step 5. Check if alpha >= beta. If true, prune all necessary moves
        '''

        if is_maximising: #white is maximising, wants highest score
            best_move_score = MIN_SCORE #we start with the worst possible score for white
            for available_move in self.gamedata_object.current_valid_move_list:
                self.move_engine.initiate_move(available_move) #step 1.
                score = self.minimax(self.chessboard_object.digital_board,False,depth-1,alpha,beta) #step 2.
                self.move_engine.undo_move()  # step 3.
                if score > best_move_score: #step 4.
                    best_move_score = score
                    if depth == self.max_depth:
                        self.best_move = available_move #new optimal move found, and is stored here

                alpha = max(alpha,best_move_score) #step 5.
                if beta <= alpha:
                    break

        if not is_maximising: #black is minimising, wants lowest score
            best_move_score = MAX_SCORE #we start with the worst possible score for white
            for available_move in self.gamedata_object.current_valid_move_list:
                self.move_engine.initiate_move(available_move) #step 1.
                score = self.minimax(self.chessboard_object.digital_board,True,depth-1,alpha,beta) #step 2.
                self.move_engine.undo_move() #step 3.

                if score < best_move_score: # step 4.
                    best_move_score = score
                    if depth == self.max_depth:
                        self.best_move = available_move #new optimal move found, and is stored here

                beta = min(beta,best_move_score) #step 5.
                if beta <= alpha:
                    break

        return best_move_score