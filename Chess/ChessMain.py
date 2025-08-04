import pygame as p 
import ChessEngine,AiMoveFinder
from multiprocessing import Process, Queue

"""
Dimensions for the board and the menu screen
"""

BOARD_WIDTH = BOARD_HEIGHT = 512 
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


MENU_WIDTH = 512
MENU_HEIGHT = 400
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 15

#intialize dictionary of global images
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wK', 'wB', 'wQ', 'bp', 'bR', 'bN', 'bK', 'bB', 'bQ' ]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("../images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), text_color=(255, 255, 255)):
        self.rect = p.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = p.font.SysFont("Arial", 24)
        self.hover_color = (150, 150, 150)
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        p.draw.rect(screen, color, self.rect)
        p.draw.rect(screen, (0, 0, 0), self.rect, 3)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
"""
-Draws the buttons on screen and updates them based on user clicks and hovers
"""
def show_menu():
    p.init()
    screen = p.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    p.display.set_caption("Chess Game - Select Players")
    clock = p.time.Clock()
    
    # Player selection states, intially both player are human
    white_is_human = True
    black_is_human = True
    
    # intialize coordinates for the buttons 
    white_button_x = 50
    black_button_x = 330
    button_y = 120
    
    #exact locations of the buttons
    buttons = {
        "white_human": Button(white_button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Human", color=(100, 150, 100)),
        "white_ai": Button(white_button_x, button_y + BUTTON_HEIGHT + 30, BUTTON_WIDTH, BUTTON_HEIGHT, "AI", color=(150, 100, 100)),
        "black_human": Button(black_button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Human", color=(100, 150, 100)),
        "black_ai": Button(black_button_x, button_y + BUTTON_HEIGHT + 30, BUTTON_WIDTH, BUTTON_HEIGHT, "AI", color=(150, 100, 100)),
        "start": Button((MENU_WIDTH - BUTTON_WIDTH) // 2, 300, BUTTON_WIDTH, BUTTON_HEIGHT, "Start Game", color=(50, 100, 200))
    }
    
    # Title font
    title_font = p.font.SysFont("Arial", 28, bold=True)
    label_font = p.font.SysFont("Arial", 20, bold=True)
    
    running = True
    while running:
        mouse_pos = p.mouse.get_pos()
        
        for event in p.event.get(): #handle if the user quits 
            if event.type == p.QUIT:
                return None, None
            
            elif event.type == p.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click and update user choices
                    if buttons["white_human"].is_clicked(mouse_pos):
                        white_is_human = True
                    elif buttons["white_ai"].is_clicked(mouse_pos):
                        white_is_human = False
                    elif buttons["black_human"].is_clicked(mouse_pos):
                        black_is_human = True
                    elif buttons["black_ai"].is_clicked(mouse_pos):
                        black_is_human = False
                    elif buttons["start"].is_clicked(mouse_pos):
                        return white_is_human, black_is_human
        
        # Update button hover states and colors based on selection
        for button in buttons.values():
            button.update_hover(mouse_pos)
        
        # Update button colors based on current selection
        buttons["white_human"].color = (50, 150, 50) if white_is_human else (100, 150, 100)
        buttons["white_ai"].color = (150, 50, 50) if not white_is_human else (150, 100, 100)
        buttons["black_human"].color = (50, 150, 50) if black_is_human else (100, 150, 100)
        buttons["black_ai"].color = (150, 50, 50) if not black_is_human else (150, 100, 100)
        
        # Draw everything
        screen.fill((240, 240, 240))
        
        # Draw title
        title_text = title_font.render("Chess Game Setup", True, (50, 50, 50))
        title_rect = title_text.get_rect(center=(MENU_WIDTH // 2, 30))
        screen.blit(title_text, title_rect)
        
        # Draw player labels
        white_label = label_font.render("White Player", True, (50, 50, 50))
        white_rect = white_label.get_rect(center=(white_button_x + BUTTON_WIDTH // 2, 90))
        screen.blit(white_label, white_rect)
        
        black_label = label_font.render("Black Player", True, (50, 50, 50))
        black_rect = black_label.get_rect(center=(black_button_x + BUTTON_WIDTH // 2, 90))
        screen.blit(black_label, black_rect)
        
        # Draw buttons
        for button in buttons.values():
            button.draw(screen)
        
        p.display.flip()
        clock.tick(MAX_FPS)
    
    return None, None
    
def main():
    # Show menu first
    playerOne, playerTwo = show_menu()
    
    if playerOne and playerTwo is None:  # User quit from menu
        return
    
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))


    gs = ChessEngine.GameState() # grabs our chess engine to simulate the game
    validMoves = gs.getValidMoves() # determine the valid moves in the pos 

    moveMade = False 
    animate = False # only want to animate certain moves, not ones the user undid
    gameOver = False 

    moveLogFont = p.font.SysFont("Calibri", 12, False, False)

    AIThinking = False # whether AI is still mtrying to make a move
    moveFinderProcess = None 
    undoMove = False
  
    loadImages()

    running = True 
    sqSelected = () # no square selected intially - last piece the user clicked on 
    playerClicks = [] # keep track of player clicks -> would have 2 tuples 
    
    while running:
        #white to move and player is a human or black to move and player is a human 
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN: # if player clicks on a piece
                if not gameOver: 
                    location = p.mouse.get_pos() # x, y location of the mouse 
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if(sqSelected == (row,col) or col >=8): # user clicks same square twice or clicked mouse log
                        sqSelected = ()
                        playerClicks = [] # reset clicks and selected square
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # want to append first and second click 

                    if(len(playerClicks) == 2 and humanTurn): # user wants to move 
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1],  gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]: # if the move is valid make the move and animate
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () # reset moves 
                                playerClicks = []
                        if not moveMade: # if invalid keep track of the last piece the user clicked 
                            playerClicks = [sqSelected]
                
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # press z to undo a move
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate() # terminate the thread
                        AIThinking = False
                    undoMove = True 

                    if e.key == p.K_r: #reset board when r is pressed
                        # reset the game state and all flags
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False
                        if AIThinking:
                            moveFinderProcess.terminate()
                            AIThinking = False
                        undoMove = True 
            
            #AI only thinks when the games not over, its their turn, and we didnt just undo a move
            if not gameOver and not humanTurn and not undoMove:
                if not AIThinking:
                    AIThinking = True

                    returnQueue = Queue() #holds the best move found by AI 
                    #creates a process that wull find the best move in parallel with the game program
                    moveFinderProcess = Process(target = AiMoveFinder.findBestMove, args=(gs,validMoves, returnQueue))
                    moveFinderProcess.start()
                    

                if not moveFinderProcess.is_alive(): # if process is finished 
                    AIMove = returnQueue.get() # retrieve AI move 
                    if AIMove is None:
                        AIMove = AiMoveFinder.findRandomMove(validMoves) # fallback if AI couldn't find a move
                    gs.makeMove(AIMove)
                    moveMade = True 
                    animate = True 
                    AIThinking = False
                    
            if moveMade: # if move was made animate it 
                if animate:
                    animateMove(gs.moveLog[-1], screen, gs.board, clock)
                validMoves = gs.getValidMoves()
                moveMade = False
                animate = False
                
            drawGameState(screen, gs, validMoves, sqSelected, moveLogFont) # draw the board based on what point of the game users are in 
            
            #end game as necessary if its a stalemate or checkmate
            if gs.checkmate:
                gameOver = True
                if gs.whiteToMove:
                    drawEnggameText(screen, "black wins by checkmate!")
                else:
                    drawEnggameText(screen, "white wins by checkmate!")

            elif gs.stalemate:
                gameOver = True
                drawEnggameText(screen, "Stalemate")
                
            clock.tick(MAX_FPS)
            p.display.flip()
            undoMove = False


             

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)
"""
-White squares row and col sum up to an even number and black squares do not 
"""
def drawBoard(screen): #alternatively colors each square black and white 
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#draw the pieces according to what the board looks like at this state
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if(piece != "--"):
                screen.blit(IMAGES[piece],p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    coords = [] # list of coords the animation runs through 
    dR = move.endRow - move.startRow # change in row
    dC = move.endCol - move.startCol # change in col
    framesPerSquare = 10 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1): # for each frame is calculates where the piece should be 
        r,c = (move.startRow + dR * frame /frameCount, move.startCol + dC * frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE , SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
    
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enpassantRow = (move.endRow + 1) if move.pieceMoved[0] == 'w' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enpassantRow * SQ_SIZE , SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        #checks if the highlighted piece is of the correct turn 
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            #highlight square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) # transparency val 0 -> 255 
            s.fill(p.Color('blue'))
            screen.blit(s,(c * SQ_SIZE, r * SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s,(SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))


def drawEnggameText(screen, text):
    font = p.font.SysFont("Helvitica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0,0,BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    #we look 2 at a time because each move should have white and blacks move on the same line 
    for i in range(0, len(moveLog), 2):
        #add the moves in string form to a new array
        moveString = "  "+ str(i // 2 + 1) + ". " + str(moveLog[i])  + " " 
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1])
        moveTexts.append(moveString)
             
    padding = 5
    textY = padding 
    movesPerRow = 3
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True ,p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height()

if __name__ == "__main__":      
    main()