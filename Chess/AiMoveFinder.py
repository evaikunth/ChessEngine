import random 
#standard chess piece scoring for AI to use
pieceScore = {"K": 0 , "Q": 9, "R" : 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000 
STALEMATE = 0 
DEPTH = 1 # how many moves ahead the AI is searching, gets exponentially slower as depth increases

"""
These arrays are to help evaluate moreequal positions for the AI
2 pieces are not always equal, for example, a knight  is far stronger in the center then on the outside
We want our engine to consider this and it also helps with reducing move possibilities for the alpha beta pruning
"""
knightScores =  [[1,1,1,1,1,1,1,1],
                [1,2,2,2,2,2,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,2,2,2,2,2,1],
                [1,1,1,1,1,1,1,1]]

bishopScores = [[1.0, 1.4, 1.8, 2.2, 2.2, 1.8, 1.4, 1.0],
                [1.4, 1.8, 2.8, 2.8, 2.8, 2.8, 1.8, 1.4],
                [1.8, 2.8, 3.6, 3.6, 3.6, 3.6, 2.8, 1.8],
                [2.2, 2.8, 3.6, 4.0, 4.0, 3.6, 2.8, 2.2],
                [2.2, 2.8, 3.6, 4.0, 4.0, 3.6, 2.8, 2.2],
                [1.8, 2.8, 3.6, 3.6, 3.6, 3.6, 2.8, 1.8],
                [1.4, 1.8, 2.8, 2.8, 2.8, 2.8, 1.8, 1.4],
                [1.0, 1.4, 1.8, 2.2, 2.2, 1.8, 1.4, 1.0],]

queenScores = [ [1.0, 2.3, 3.6, 4.9, 4.9, 3.6, 2.3, 1.0],
                [2.3, 3.6, 6.2, 6.2, 6.2, 6.2, 3.6, 2.3],
                [3.6, 6.2, 7.9, 7.9, 7.9, 7.9, 6.2, 3.6],
                [4.9, 6.2, 7.9, 9.0, 9.0, 7.9, 6.2, 4.9],
                [4.9, 6.2, 7.9, 9.0, 9.0, 7.9, 6.2, 4.9],
                [3.6, 6.2, 7.9, 7.9, 7.9, 7.9, 6.2, 3.6],
                [2.3, 3.6, 6.2, 6.2, 6.2, 6.2, 3.6, 2.3],
                [1.0, 2.3, 3.6, 4.9, 4.9, 3.6, 2.3, 1.0],]

rookScores =   [[3.0, 3.5, 4.0, 10, 4.5, 10, 3.5, 3.0],
                [3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5],
                [4.0, 4.5, 5.0, 5.0, 5.0, 5.0, 4.5, 4.0],
                [4.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 4.5],
                [4.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 4.5],
                [4.0, 4.5, 5.0, 5.0, 5.0, 5.0, 4.5, 4.0],
                [3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5],
                [3.0, 3.5, 4.0, 4.5, 4.5, 4.0, 3.5, 3.0],]

pawnScores = [  [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14],
                [0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29],
                [0.43, 0.43, 0.43, 0.57, 0.57, 0.43, 0.43, 0.43],
                [0.57, 0.57, 0.71, 0.71, 0.71, 0.71, 0.57, 0.57],
                [0.43, 0.43, 0.57, 0.57, 0.57, 0.57, 0.43, 0.43],
                [0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29, 0.29],
                [0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14],]

piecePositionScores = {'N': knightScores, 'B': bishopScores, 'Q': queenScores, 
'R': rookScores, 'p': pawnScores }


"""
Selects move @ random, works as a fallback if best move doesnt work
"""
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1, -CHECKMATE, CHECKMATE)
    returnQueue.put(nextMove)

"""
This evaluates moves at each depth such that a high score is good for white and black when calculating their respective score
We look at a move and then the responses our opponents can make and so on depending on the depth
Once we hit the base case we evaluate the board and choose the highest score at that depth because we assume our opponent or the engine will play the best moves
alpha - the best score that we can guarantee, beta - the worst score the opponent will give us 
When we find moves that are better than what our opponent would allow at a certain level we stop searching because they would never choose this move

"""
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, turnMultiplier, alpha, beta):
    global nextMove
    if depth == 0: 
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE 
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = - findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -turnMultiplier, -beta, -alpha)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH: 
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: 
            alpha = maxScore
        if alpha >= beta: 
            break

    return maxScore



"""
pos score good for white and neg score good for black
"""
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gs.stalemate:
        return STALEMATE

    return scoreMaterial(gs.board)
        


"""
calculate the score of the board based on material weights
"""
def scoreMaterial(board):
    score = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            square = board[row][col]
            if square != "--":
                piecePositionScore = 0
                if square[1] != 'K':
                    piecePositionScore = piecePositionScores[square[1]][row][col] * 0.1
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore
           
    return score
            
            







