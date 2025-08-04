class GameState():
    def __init__(self):
        # first char is b -> black pieces or w -> white pieces , other char corresponds to the piece
        self.board = [ 
            ["bR", "bN", "bB", "bQ" , "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"], 
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ" , "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
        'Q': self.getQueenMoves, 'K' : self.getKingMoves} # second letter of our strings map to the move function for a piece
        self.whiteToMove = True 
        self.moveLog = [] # track of the previous valid moves made so far
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () #coordinates for square where enpassant is possible
        self.enpassantPossibleLog = [self.enpassantPossible] # list of the coords where it was possible in previous gamestates
        self.currentCastleRights = CastleRights(True,True,True,True) # booleans correspond to castle rights as specificied below ie: wks = True
        self.castleRightsLog = [CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs, 
        self.currentCastleRights.bks, self.currentCastleRights.bqs)] # logs all states of castle logs in the game
       
    
    def makeMove(self, move):
        #empty square that was moved and move that piece to the desired location
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) 
        self.whiteToMove = not self.whiteToMove #swap turns

        #update K location if moved because we need to track king locations for castling and checks
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #automatically promotes piece to Q
        #ideally we implement functionality to make this a choice
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        # since the square we move to isnt the square that is captured we actually have to account for that 
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        """
        -we only update enpassant if the last move that was made was a 2 square pawn advance
        - enpassant is now only valid for the opponents turn and then we can discard the possibility after their move
        """
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        """
        - Castling functions different whether its to the king side or queen side but is the same regardless of the color
        """
        if move.isCastleMove:
            if (move.endCol - move.startCol) == 2: # king side -> essentially if the K moved 2 squares to the right its kingside 
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] # moves rook to the left of the king
                self.board[move.endRow][move.endCol + 1] = "--"
            else: # queenside castle 
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] # move rook to right of king
                self.board[move.endRow][move.endCol - 2] = "--"

        #add enpessant state to the log, this helps keep track of previous states if user undos move
        self.enpassantPossibleLog.append(self.enpassantPossible)


        #update castle rights - when a king or rook moves
        self.updateCastleRight(move)
        #update the log with the new castle rights
        self.castleRightsLog.append(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs, 
        self.currentCastleRights.bks, self.currentCastleRights.bqs))




    
    def undoMove(self):

        if(len(self.moveLog)) != 0: # make sure a move has been made
            #get most recent move info 
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # reverse the turn back

            #make sure we dont lose track of the king 
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
        
            #undo enpassant move and make sure that move can be made again 
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
               
            
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            #revert to previous castle rights 
            self.castleRightsLog.pop()
            self.currentCastleRights = CastleRights(
                self.castleRightsLog[-1].wks,
                self.castleRightsLog[-1].wqs,
                self.castleRightsLog[-1].bks,
                self.castleRightsLog[-1].bqs
            )

            #actually undoing the castling 
            if move.isCastleMove:
                if (move.endCol - move.startCol) == 2: # K side if the K moved to the right
                    self.board[move.endRow][move.endCol + 1] =  self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            self.checkmate = False
            self.stalemate = False

    """
    -If either the King or the Rook have moved from their original square it effects castling rights
    -If K moved that side cannot castle at all
    -If the rook moved that respective side(kingside or queenside) cannot castle 

    """
    def updateCastleRight(self, move):

        if move.pieceMoved == 'wK':
            self.currentCastleRights.wks = False
            self.currentCastleRights.wqs = False

        elif move.pieceMoved == 'bK':
            self.currentCastleRights.bks = False
            self.currentCastleRights.bqs = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # left rook long side castle
                    self.currentCastleRights.wqs = False
                elif move.startCol == 7: # right rook short side castle
                    self.currentCastleRights.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # left rook long side castle
                    self.currentCastleRights.bqs = False
                elif move.startCol == 7: # right rook short side castle
                    self.currentCastleRights.bks = False
        
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0: # left rook long side castle
                    self.currentCastleRights.wqs = False
                elif move.endCol == 7: # right rook short side castle
                    self.currentCastleRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0: # left rook long side castle
                    self.currentCastleRights.bqs = False
                elif move.endCol == 7: # right rook short side castle
                    self.currentCastleRights.bks = False


        
    """
    -The engine generates all possible moves,
    however, it will allow illegal moves as the rules of chess prohibit certain moves in circumstances 
    """
    def getValidMoves(self): 

         #we want to keep enpassant and castle rights constant however whill generating the valid moves these will be corrupted
        temp = self.enpassantPossible
        temp2 = CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs, 
        self.currentCastleRights.bks, self.currentCastleRights.bqs)

        moves = self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        """
        - We parse through all possible moves and make that move. We then check if the move puts or keeps that player in check
        - If it does put/keep the player in checks its illegal else its valid 
        """
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove # need to switch the turns because make move switches the turns
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove #switch turns again because undo move switches the turn
            self.undoMove()

        if(len(moves) == 0): # if no legal moves and the player is in check then its mate else its a stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True 
        else: # make sure to reset the vars so players can undo moves and still keep playing 
            self.checkmate = False
            self.stalemate = False

        self.enpassantPossible = temp
        self.currentCastleRights = temp2
        return moves

    """
    -We check if the current players king is under attack by seeing if another piece can reach the kings square 
    -This helps us deal with pins as since valid moves actually generates the move it can see that playing that move will put itself in check 
    """
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    #determine if enemy can attack the square at r, c
    def squareUnderAttack(self, r, c):
        """
        -switch turns so we can determine if the enemy player can attack the current players king
        - we generate all the opponents moves and see if any of them put the opponent in check
        - this is not the most efficient approach and ideally we can reduce repeated computations
        - this algorithm is not specific to the K but to any piece 
        """
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square can be reached 
                return True
        return False



    """
    Generate all possible moves in the position for white or black, without regard for the rules 
    Pieces still move legally but we do not factor game state ie: checks 
    
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if((turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove)):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    def getPawnMoves(self, r , c, moves):

        if self.whiteToMove:
            if self.board[r-1][c] == "--": #1 square forward for white
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--": # pawn has not been moved and the square in front is open check the one after too
                    moves.append(Move((r,c), (r-2,c), self.board))
            #check if pawn can make legal capture to the left
            if c - 1 >= 0: #check if capture is in bounds
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                #if enpassant can be made for white to the left
                elif (r-1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board, isEnpassantMove=True))


            if c + 1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board, isEnpassantMove=True))
        else: # black pawn moves
            if self.board[r+1][c] == "--": #1 square forward for black
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--": # pawn has not been moved and the square in front is open check the one after too
                    moves.append(Move((r,c),(r+2,c),self.board))
            #check if pawn can make legal capture to the left
            if c - 1 >= 0: #check if capture is in bounds
                if self.board[r+1][c-1][0] == 'w': #enemy piece to capture
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board, isEnpassantMove=True))
                 

    def getRookMoves(self, r, c, moves):
        #1: column decrements -> moving left, 2: col inc -> right, 3: row dec -> mov up, 4: row inc -> down 
        directions = [(0,-1),(0,1), (-1,0), (1,0)]
        #check all valid moves when moving down the col
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1,8):
                row = r + d[0] * i
                col = c + d[1] * i
                if (0 <= row <= 7 )and (0 <= col <= 7):
                    piece = self.board[row][col]
                    if piece == "--":
                        moves.append(Move((r,c),(row,col), self.board))
                    elif piece[0] == enemyColor: # we can go up until enemy piece but not after
                        moves.append(Move((r,c),(row,col), self.board))
                        break
                    else: # do not include the square your own piece is on 
                        break
                else: #oob 
                    break 

        
    def getKnightMoves(self, r, c, moves):
        #1: up right, 2: up left 3: right up, 4: right down, 5:left up 6: left down, 7: down left 8: down right
        directions = [(-2,1), (-2,-1), (-1,2), (1, 2), (1,-2), (-1, -2), (2,-1), (2,1)]
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            row = r + d[0]
            col = c + d[1]
            if (0 <= row <= 7 )and (0 <= col <= 7):
                piece = self.board[row][col]
                if(piece[0] != allyColor):
                    moves.append(Move((r,c),(row,col), self.board))

            


    def getBishopMoves(self, r, c, moves):
        # 1: up and left 2: up and right 3: down and left 4: down row and right
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                row = r + d[0] * i
                col = c + d[1] * i
                if (0 <= row <= 7 )and (0 <= col <= 7):
                    piece = self.board[row][col]
                    if piece == "--":
                        moves.append(Move((r,c),(row,col), self.board))
                    elif piece[0] == enemyColor: # we can go up until enemy piece but not after
                        moves.append(Move((r,c),(row,col), self.board))
                        break
                    else: # do not include the square your own piece is on 
                        break
                else: #oob 
                    break 


    def getKingMoves(self, r, c, moves):
        # 1: down 2: up 3: right 4: left 5: down right 6: up right 7: up left 8: down left
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,1), (-1,-1), (1, -1)]
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            row = r + d[0]
            col = c + d[1]
            if (0 <= row <= 7 )and (0 <= col <= 7):
                piece = self.board[row][col]
                if(piece[0] != allyColor):
                    moves.append(Move((r,c),(row,col), self.board))
    
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)
        


    def getCastleMoves(self, r,c,moves):
        if self.inCheck(): # can't castle while in check
            return

        if (self.whiteToMove and self.currentCastleRights.wks) or (not self.whiteToMove and self.currentCastleRights.bks):
            self.getKingsideCastleMoves(r,c,moves)

        if (self.whiteToMove and self.currentCastleRights.wqs) or (not self.whiteToMove and self.currentCastleRights.bqs):
            self.getQueensideCastleMoves(r,c,moves)

    """
    Castling is legal if the king is not in check the castling squares are empty and no piece can attack them 
    """ 
    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c),(r,c+2),self.board, isCastleMove = True))
        

    def getQueensideCastleMoves(self, r , c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c),(r,c-2),self.board, isCastleMove = True))

        

    

"""
ks = kingside
qs = queenside
Both sides can castle on those sides when the game begins and those rules change as it progresses 
"""
class CastleRights():
    def __init__(self,wks,wqs,bks,bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs
    


class Move():
    #imagine the ranks from whites perspective translated to the 2-d matrix 
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4":4, "5": 3, "6": 2, "7" : 1 , "8":0} 
    rowsToRanks = {v: k for k,v in ranksToRows.items()} #reverses ranks to rows

    filesToCols = {"a": 0, "b": 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    colsToFiles = {v: k for k,v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isEnpassantMove = False , isCastleMove = False): #startSq and endSq are tuples with [0] = row , [1] = col
        #coords of where the piece that was moved started
        self.startRow = startSq[0]
        self.startCol = startSq[1]

        #coords of where it ended
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        #what was the piece that moved and was captured
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #encodes the pos of where the piece started as the first 2 chars and the last 2 of where it ended useful for debugging 
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol 

        self.promotionChoice = 'Q' 
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)

        self.isEnpassantMove = isEnpassantMove # optional parameter and allows us to pass a flag when needed to reduce complexity
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == "bp" else "bp"

        self.isCastleMove = isCastleMove 
        self.isCapture = self.pieceCaptured != "--"


      


    """
    Overriding equals method
    """

    def __eq__(self,other):
        if (isinstance(other,Move)):
            return self.moveID == other.moveID
        return False

    def __repr__(self):
        return f" + {self.moveID}"

    def __str__(self):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        #pawn promotion
        #same type of piece can move to same square
        # + for check or # for mate
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + " " + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        return   self.colsToFiles[c] + self.rowsToRanks[r]

    
