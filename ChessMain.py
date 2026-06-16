# main driver file, be responsible for handling user input and displaying the current GameState object.

import pygame as p
import ChessBot
import SmartMoveFinder

WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250 # Chiều rộng của bảng ghi log
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8 #dimension of a chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animation later on
IMAGES = {}
SOUNDS = {}

# initialize a global dictionary of images. This will be called exactly once in the main
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def loadSounds():
    SOUNDS['move'] = p.mixer.Sound("sounds/move.ogg")
    SOUNDS['capture'] = p.mixer.Sound("sounds/capture.ogg")
    SOUNDS['check'] = p.mixer.Sound("sounds/check.ogg")

# The main driver for our code. This will handle user input and updating the graphics
def main():
    p.init()
    p.mixer.init()
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessBot.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    loadImages() #only do thís once before the while loop
    loadSounds()
    running = True
    sqSelected = () #no square is selected, keep track of the last click of the user(tuple:(row, col))
    playerClicks = [] #keep track of player clicks (two tuple: [(6, 4), (4, 4)])
    gameOver = False
    replayMode = False
    replayIndex = 0
    gsReplay = None
    playerOne = True #If a human is playing white, then this will be True. If an AI is playing, then this will be False
    playerTwo = False #Same as above but for black
    while running:
        # replay UI button geometry (positioned in the move log panel at top)
        logPanelX = WIDTH
        logPanelY = 5
        buttonW, buttonH = 60, 28
        spacing = 3
        replayRect = p.Rect(logPanelX + 5, logPanelY, buttonW, buttonH)
        leftRect = p.Rect(logPanelX + 5, logPanelY + buttonH + spacing, buttonW, buttonH)
        rightRect = p.Rect(logPanelX + buttonW + spacing + 5, logPanelY + buttonH + spacing, buttonW, buttonH)
        exitRect = p.Rect(logPanelX + (buttonW + spacing) * 2 + 5, logPanelY + buttonH + spacing, buttonW, buttonH)
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                # replay mode / replay button clicks when game over
                if gameOver:
                    if not replayMode:
                        if replayRect.collidepoint(pos):
                            replayMode = True
                            replayIndex = 0
                            gsReplay = ChessBot.GameState()
                            # initial position (0 moves applied)
                            drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
                            p.display.flip()
                            continue
                    else:
                        # inside replay mode: left, right, exit
                        if leftRect.collidepoint(pos):
                            if replayIndex > 0:
                                replayIndex -= 1
                                gsReplay = ChessBot.GameState()
                                for i in range(replayIndex):
                                    gsReplay.makeMove(gs.moveLog[i])
                                drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
                                p.display.flip()
                            continue
                        if rightRect.collidepoint(pos):
                            if replayIndex < len(gs.moveLog):
                                replayIndex += 1
                                # apply first replayIndex moves
                                gsReplay = ChessBot.GameState()
                                for i in range(replayIndex):
                                    gsReplay.makeMove(gs.moveLog[i])
                                # animate forward step if possible
                                if replayIndex > 0:
                                    animateMove(gs.moveLog[replayIndex-1], screen, gsReplay.board, clock)
                                drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
                                p.display.flip()
                            continue
                        if exitRect.collidepoint(pos):
                            replayMode = False
                            gsReplay = None
                            continue
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() #(x, y) location of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if col >= 8:
                        continue
                    if sqSelected == (row, col): #the user clicked the same square twice
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                    if len(playerClicks) == 2:
                        move = ChessBot.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    if not playerOne or not playerTwo:
                        gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    sqSelected = ()
                    playerClicks = []
                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gs = ChessBot.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                if e.key == p.K_p and gameOver: #replay when 'p' is pressed after game over
                    replayGame(screen, gs.moveLog, moveLogFont, clock)
                if e.key == p.K_LEFT and replayMode and gameOver:
                    if replayIndex > 0:
                        replayIndex -= 1
                        gsReplay = ChessBot.GameState()
                        for i in range(replayIndex):
                            gsReplay.makeMove(gs.moveLog[i])
                        drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
                        p.display.flip()
                if e.key == p.K_RIGHT and replayMode and gameOver:
                    if replayIndex < len(gs.moveLog):
                        replayIndex += 1
                        gsReplay = ChessBot.GameState()
                        for i in range(replayIndex):
                            gsReplay.makeMove(gs.moveLog[i])
                        if replayIndex > 0:
                            animateMove(gs.moveLog[replayIndex-1], screen, gsReplay.board, clock)
                        drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
                        p.display.flip()
                if e.key == p.K_ESCAPE and replayMode:
                    replayMode = False
                    gsReplay = None

        #AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = validMoves[0]
            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
               animateMove(gs.moveLog[-1], screen, gs.board, clock)
            last_move = gs.moveLog[-1]
            # 1. Đang bị chiếu Vua
            if gs.inCheck():
                SOUNDS['check'].play()
            # 2. Có ăn quân (hoặc ăn tốt qua đường)
            elif last_move.pieceCaptured != '--' or last_move.isEnpassantMove:
                SOUNDS['capture'].play()
            # 3. Nước đi bình thường
            else:
                SOUNDS['move'].play()
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        if replayMode and gsReplay is not None:
            drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
        else:
            drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        # Cập nhật trạng thái gameOver
        if gs.checkmate or gs.stalemate:
            gameOver = True
        
        # Chỉ hiển thị thông báo kết thúc khi NOT ở chế độ replay
        if gameOver and not replayMode:
            if gs.checkmate:
                if gs.whiteToMove:
                    drawText(screen, 'Black win')
                else:
                    drawText(screen, 'White win')
            elif gs.stalemate:
                drawText(screen, 'Dull draw, no money for both')
        
        # draw replay UI buttons in the move log panel
        drawReplayUI(screen, gameOver, replayMode, replayRect, leftRect, rightRect, exitRect, replayIndex, len(gs.moveLog))
        
        clock.tick(MAX_FPS)
        p.display.flip()

#Highlight square selected and moves for piece selected

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            #highlight selected squared
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency -> 0 transparent; 255 opauqe
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('pink'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


# responsible for all the graphics within a current game state.

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) #draw the squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw tge pieces on top of those squares

    drawMoveLog(screen, gs, moveLogFont)


def drawMoveLog(screen, gs, font):
    # 1. Vẽ cái nền của bảng Log (Màu đen hoặc xám đậm)
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("pink"), moveLogRect)

    moveLog = gs.moveLog
    moveTexts = []

    # 2. Gom nước đi lại thành từng cặp (Trắng - Đen)
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + moveLog[i].getChessNotation() + " "
        if i + 1 < len(moveLog):
            moveString += moveLog[i + 1].getChessNotation()
        moveTexts.append(moveString)

    # ---> BẮT ĐẦU FIX LỖI TRÀN LOG <---
    padding = 5
    lineSpacing = 2
    textY = padding + 75  # leave space for replay buttons at top
    textX = padding

    # Đo chiều cao của 1 dòng chữ và tính sức chứa của màn hình
    lineHeight = font.size("Test")[1] + lineSpacing
    linesPerColumn = (MOVE_LOG_PANEL_HEIGHT - textY - padding) // lineHeight
    maxColumns = MOVE_LOG_PANEL_WIDTH // 115
    maxLinesOnScreen = linesPerColumn * maxColumns

    # Lọc danh sách: Nếu dài quá sức chứa, chỉ lấy đoạn cuối cùng (những nước đi mới nhất)
    if len(moveTexts) > maxLinesOnScreen:
        moveTexts = moveTexts[-maxLinesOnScreen:]
    # ---------------------------------

    # 3. In chữ lên màn hình
    for i in range(len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, True, p.Color('black'))

        # Nếu in xuống dưới bị lố chiều cao màn hình -> Chuyển sang cột mới bên phải
        if textY + textObject.get_height() >= MOVE_LOG_PANEL_HEIGHT:
            textY = padding + 75
            textX += 115  # Chiều rộng của 1 cột

        textLocation = moveLogRect.move(textX, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


# draw the squares on the board. The top left square is always light
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# draw the pieces on the board using the current GameState.board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Animating a move
def animateMove(move, screen, board, clock):
    global colors
    coords = [] #list of coords that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5 #frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                # Tốt bị ăn nằm cùng hàng với Tốt của mình lúc bắt đầu đi
                enPassantRow = move.startRow
                enPassantSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                screen.blit(IMAGES[move.pieceCaptured], enPassantSquare)
            else:
                # Nước ăn quân bình thường
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont('Helvetica', 36, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

def drawSmallText(screen, text, y_offset=40):
    font = p.font.SysFont('Helvetica', 18, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2 + y_offset)
    screen.blit(textObject, textLocation)

def drawButton(screen, rect, text):
    p.draw.rect(screen, p.Color('lightgray'), rect)
    p.draw.rect(screen, p.Color('darkgray'), rect, 2)
    font = p.font.SysFont('Helvetica', 14, True, False)
    textObject = font.render(text, 0, p.Color('black'))
    textRect = textObject.get_rect(center=rect.center)
    screen.blit(textObject, textRect)

def drawReplayUI(screen, gameOver, replayMode, replayRect, leftRect, rightRect, exitRect, replayIndex, moveLogLen):
    """Vẽ nút replay trong bảng log panel"""
    if gameOver:
        if not replayMode:
            drawButton(screen, replayRect, 'Replay')
        else:
            drawButton(screen, leftRect, '<')
            drawButton(screen, rightRect, '>')
            drawButton(screen, exitRect, 'Exit')

def replayGame(screen, moveLog, moveLogFont, clock):
    if not moveLog:
        return
    gsReplay = ChessBot.GameState()
    # draw initial position
    drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
    p.display.flip()
    p.time.wait(500)
    for m in moveLog:
        for ev in p.event.get():
            if ev.type == p.QUIT:
                p.quit()
                return
        gsReplay.makeMove(m)
        animateMove(m, screen, gsReplay.board, clock)
        drawGameState(screen, gsReplay, gsReplay.getValidMoves(), (), moveLogFont)
        p.display.flip()
        p.time.wait(300)

main()