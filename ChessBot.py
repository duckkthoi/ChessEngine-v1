# responsible for storing all the current state of a chess game, also responsible for determining the valid moves
# at the current state, also keep a move log

class GameState():
    def __init__(self):
        #board is an 8x8 2d list, each element of the list has 2 characters
        # "--" represents an empty space with no pieces
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R':self.getRookMoves, "N": self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.posHistory = {}

        self.halfMoveClock = 0
        self.halfMoveClockLog = []

    def getStateID(self):
        # Nâng cấp: Dùng Tuple thay vì String để Python tính Hash bằng C-engine siêu tốc
        board_tuple = tuple(tuple(row) for row in self.board)
        rights = (self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                  self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        # Gom tất cả vào 1 tuple và dùng hàm hash() mặc định của Python (chạy cực nhanh)
        return hash((board_tuple, self.whiteToMove, rights, self.enpassantPossible))

    def isInsufficientMaterial(self):
        """Kiểm tra hòa cờ do không đủ quân: K vs K, K+N vs K, K+B vs K"""
        whitePieces = []
        blackPieces = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece[0] == 'w' and piece[1] != 'K':
                    whitePieces.append(piece[1])
                elif piece[0] == 'b' and piece[1] != 'K':
                    blackPieces.append(piece[1])
        
        # K vs K (cả 2 chỉ còn vua)
        if len(whitePieces) == 0 and len(blackPieces) == 0:
            return True
        
        # K + N vs K hoặc K vs K + N
        if len(whitePieces) == 1 and len(blackPieces) == 0 and whitePieces[0] == 'N':
            return True
        if len(blackPieces) == 1 and len(whitePieces) == 0 and blackPieces[0] == 'N':
            return True
        
        # K + B vs K hoặc K vs K + B
        if len(whitePieces) == 1 and len(blackPieces) == 0 and whitePieces[0] == 'B':
            return True
        if len(blackPieces) == 1 and len(whitePieces) == 0 and blackPieces[0] == 'B':
            return True
        
        return False


    # Take a Move as a parameter and execute it (this will not work for castling, pawn promotion, and en-passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later

        self.halfMoveClockLog.append(self.halfMoveClock)
        if move.pieceMoved[1] == 'p' or move.pieceCaptured != '--':
            self.halfMoveClock = 0  # Reset nếu đẩy tốt hoặc ăn quân
        else:
            self.halfMoveClock += 1  # Tăng biến đếm

        self.whiteToMove = not self.whiteToMove #swap players
        #update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #enpassanct move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #caturing the pawn

        #update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
        self.enpassantPossibleLog.append(self.enpassantPossible)

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the rook
                self.board[move.endRow][move.endCol+1] = '--' #erase old rook
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'


        #update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

        stateID = self.getStateID()
        self.posHistory[stateID] = self.posHistory.get(stateID, 0) + 1




    #Undo the last move made
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            stateID = self.getStateID()
            self.posHistory[stateID] -= 1
            if self.posHistory[stateID] == 0:
                del self.posHistory[stateID]

            move = self.moveLog.pop()

            self.halfMoveClock = self.halfMoveClockLog.pop()

            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turns back
            #update the king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                #self.enpassantPossible = (move.endRow, move.endCol)
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            #undo a 2 square pawn advances

            #undo castling rights
            self.castleRightsLog.pop() #get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            #undo the castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            self.checkmate = False
            self.stalemate = False



    #Update the castle rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    # All moves considering checks
    def getValidMoves(self):
        #tempEnpassantPossible = self.enpassantPossible
        #tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
        #                                self.currentCastlingRight.wqs,self.currentCastlingRight.bqs) #copy the current castling rights
        #1. generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        #2. for each move, make the move
        for i in range(len(moves)-1, -1, -1): #when removing from a list go backwards through that list
            self.makeMove(moves[i])
            #3. generate all opponent's move

            #4. for each of your opponent's move, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  #5. if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: #either checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        # self.enpassantPossible = tempEnpassantPossible
        # self.currentCastlingRight = tempCastleRights
        if self.posHistory.get(self.getStateID(), 0) >= 3:
            self.stalemate = True
            moves = []
        
        # Kiểm tra hòa cờ do không đủ quân
        if self.isInsufficientMaterial():
            self.stalemate = True

        if self.halfMoveClock >= 100:
            self.stalemate = True
            moves = []

        return moves


    #Determine if the current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    #Determine if the enemy can attack the square r, c
    def squareUnderAttack(self, r, c):
        enemyColor = 'b' if self.whiteToMove else 'w'
        allyColor = 'w' if self.whiteToMove else 'b'

        # 1. Phóng tia nhìn ra 8 hướng (Trên, Dưới, Trái, Phải, và 4 đường chéo)
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:  # Bị quân mình che chắn -> Hướng này an toàn
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # Quy tắc tấn công:
                        # Hướng 0-3 (Thẳng/Ngang) -> Xe
                        # Hướng 4-7 (Chéo) -> Tượng
                        # 1 ô chéo đúng hướng -> Tốt
                        # Mọi hướng -> Hậu
                        # 1 ô mọi hướng -> Vua
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or \
                                (i == 1 and type == 'K'):
                            return True
                        else:  # Là quân địch nhưng không có khả năng tấn công theo hướng này
                            break
                else:  # Đụng tường bàn cờ
                    break

        # 2. Quét kiểm tra Mã địch (hình chữ L)
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    return True

        return False


    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given rows
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function based on piece type
        return moves


    #Get all the pawn moves for the pawn located at row, col, and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: #capture to the left
                if self.board[r-1][c-1][0] == "b": #enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board), )
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7: #capture to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))

        else: #black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))
        #add pawn promotion later



    # Get all the rook moves for the rook located at row, col, and add these moves to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))    #up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off board
                    break

    # Get all the knight moves for the knight located at row, col, and add these moves to the list
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Get all the bishop moves for the bishop located at row, col, and add these moves to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1)) #4 diagnols
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #is it on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #friendly piece invalid
                        break
                else: #off the board
                    break

    # Get all the queen moves for the queen located at row, col, and add these moves to the list
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # Get all the king moves for the king located at row, col, and add these moves to the list
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    #Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  #can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves, ):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))



class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    fileToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e":4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v:k for k, v in fileToCols.items()}
    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        #enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castle move
        self.isCastleMove = isCastleMove


        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 +self.endCol

    #Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # 1. Nhập thành (Castling)
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)

        # 2. Tốt di chuyển (Pawn moves)
        if self.pieceMoved[1] == 'p':
            if self.pieceCaptured != '--' or self.isEnpassantMove:
                # Ăn quân (ví dụ: exd5)
                moveString = self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                # Đi thẳng (ví dụ: e4)
                moveString = endSquare

            # Phong cấp (Pawn Promotion)
            if self.isPawnPromotion:
                moveString += "=Q"  # Tạm thời luôn mặc định biến thành Hậu
            return moveString

        # 3. Quân nặng di chuyển (Piece moves)
        moveString = self.pieceMoved[1]  # Lấy ký tự K, Q, R, B, N
        if self.pieceCaptured != '--':
            moveString += "x"  # Thêm chữ x nếu có ăn quân (ví dụ: Bxf7)

        return moveString + endSquare

    # Hàm giữ lại: Trả về chuẩn UCI cho máy đọc (Dành cho Sách Khai Cuộc sau này)
    def getUCI(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]