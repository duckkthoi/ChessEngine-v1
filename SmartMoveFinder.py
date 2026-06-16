import random

pieceScore = {"K": 0, "Q": 900, "R": 500, "B": 300, "N": 300, "p": 100}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 4
ttable = {} # TRANPOSITION TABLE (Cuốn sổ tay ghi nhớ thế cờ)
# Thư viện sách khai cuộc siêu to khổng lồ (Chuẩn UCI)
OPENING_BOOK = [
    # ==========================================
    # 1. CÁC VÁN BẮT ĐẦU BẰNG e4 (Tấn công rực lửa)
    # ==========================================

    # Ruy Lopez (Kinh điển)
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5a4", "g8f6", "e1g1"],
    # Ruy Lopez - Berlin Defense (Phòng thủ siêu chắc của Đen)
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6", "e1g1", "f6e4", "d2d4", "e4d6", "b5c6", "d7c6", "d4e5", "d6f5"],
    # Ruy Lopez - Marshall Attack (Đen thí Tốt để phản công điên cuồng)
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5a4", "g8f6", "e1g1", "f8e7", "f1e1", "b7b5", "a4b3", "e8g8",
     "c2c3", "d7d5"],

    # Italian Game & Biến thể
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "c2c3", "g8f6"],
    # Evans Gambit (Trắng thí Tốt b4 để lấy trung tâm)
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "b2b4", "c5b4", "c2c3", "b4a5", "d2d4", "e5d4"],
    # Two Knights Defense (Trắng nhảy Ng5 chơi bẫy Fried Liver)
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "f3g5", "d7d5", "e4d5", "c6a5", "c4b5", "c7c6", "d5c6", "b7c6"],

    # Scotch Game
    ["e2e4", "e7e5", "g1f3", "b8c6", "d2d4", "e5d4", "f3d4", "g8f6"],
    # Vienna Game (Trắng đánh c3, nhắm vào f4)
    ["e2e4", "e7e5", "b1c3", "g8f6", "f2f4", "d7d5"],
    # King's Gambit Accepted (Thí Tốt f4 - Khai cuộc bão táp thế kỷ 19)
    ["e2e4", "e7e5", "f2f4", "e5f4", "g1f3", "g7g5", "h2h4", "g5g4", "f3e5"],

    # Sicilian Defense (Đen phản công)
    ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "a7a6"],  # Najdorf
    ["e2e4", "c7c5", "g1f3", "b8c6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "e7e5"],  # Sveshnikov
    ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "g7g6", "c1e3", "f8g7", "f2f3", "e8g8",
     "d1d2", "b8c6"],  # Dragon (Rồng)
    ["e2e4", "c7c5", "c2c3", "g8f6", "e4e5", "f6d5", "d2d4", "c5d4", "c3d4", "d7d6"],  # Alapin
    ["e2e4", "c7c5", "b1c3", "b8c6", "g2g3", "g7g6", "f1g2", "f8g7", "d2d3", "d7d6", "g1e2", "e7e5"],  # Closed Sicilian

    # French & Caro-Kann
    ["e2e4", "e7e6", "d2d4", "d7d5", "e4e5", "c7c5", "c2c3", "b8c6", "g1f3", "d8b6"],  # French Advance
    ["e2e4", "e7e6", "d2d4", "d7d5", "b1d2", "c7c5", "e4d5", "e6d5"],  # French Tarrasch
    ["e2e4", "c7c6", "d2d4", "d7d5", "e4e5", "c8f5", "g1f3", "e7e6", "f1e2", "c7c5"],  # Caro-Kann Advance
    ["e2e4", "c7c6", "d2d4", "d7d5", "e4d5", "c6d5", "f1d3", "b8c6", "c2c3"],  # Caro-Kann Exchange

    # Các khai cuộc e4 khác
    ["e2e4", "d7d5", "e4d5", "d8d5", "b1c3", "d5a5", "d2d4", "g8f6"],  # Scandinavian
    ["e2e4", "g8f6", "e4e5", "f6d5", "d2d4", "d7d6", "c2c4", "d5b6"],  # Alekhine
    ["e2e4", "d7d6", "d2d4", "g8f6", "b1c3", "g7g6"],  # Pirc Defense

    # ==========================================
    # 2. CÁC VÁN BẮT ĐẦU BẰNG d4 (Chiến lược, tư duy)
    # ==========================================

    ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c1g5", "f8e7", "e2e3", "e8g8"],  # QGD
    ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c4d5", "e6d5", "c1g5", "c7c6"],  # QGD Exchange
    ["d2d4", "d7d5", "c2c4", "d5c4", "g1f3", "g8f6", "e2e3", "e7e6", "f1c4"],  # QGA
    ["d2d4", "d7d5", "c2c4", "c7c6", "g1f3", "g8f6", "b1c3", "d5c4"],  # Slav

    ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7", "e2e4", "d7d6", "g1f3", "e8g8"],  # King's Indian
    ["d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4", "e2e3", "e8g8"],  # Nimzo-Indian
    ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "d7d5", "c4d5", "f6d5"],  # Grünfeld
    ["d2d4", "d7d5", "g1f3", "g8f6", "c1f4", "c7c5", "e2e3", "b8c6"],  # London System
    ["d2d4", "g8f6", "c2c4", "e7e6", "g1f3", "f8b4", "c1d2", "b4d2", "d1d2"],  # Bogo-Indian

    # Các hệ Gambit & Chiến thuật d4 dị
    ["d2d4", "g8f6", "c2c4", "c7c5", "d4d5", "e7e6", "b1c3", "e6d5", "c4d5", "d7d6", "e2e4", "g7g6"],  # Benoni Defense
    ["d2d4", "g8f6", "c2c4", "c7c5", "d4d5", "b7b5", "c4b5", "a7a6", "b5a6", "c8a6"],
    # Benko Gambit (Đen thí b5 để đánh cánh Hậu)
    ["d2d4", "g8f6", "c1g5", "f6e4", "g5f4", "d7d5", "f2f3", "e4f6"],  # Trompowsky Attack
    ["d2d4", "g8f6", "c2c4", "e7e6", "g2g3", "d7d5", "f1g2", "f8e7", "g1f3", "e8g8", "e1g1", "d5c4"],  # Catalan Opening

    # ==========================================
    # 3. CÁC KHAI CUỘC LINH HOẠT KHÁC (Đánh úp đối thủ)
    # ==========================================

    ["c2c4", "e7e5", "b1c3", "g8f6", "g2g3", "d7d5", "c4d5", "f6d5"],  # English
    ["c2c4", "c7c5", "g1f3", "g8f6", "b1c3", "b8c6", "g2g3", "g7g6"],  # Symmetrical English
    ["g1f3", "d7d5", "g2g3", "g8f6", "f1g2", "c7c6", "e1g1", "c8g4"],  # Reti
    ["d2d4", "f7f5", "c2c4", "g8f6", "g2g3", "e7e6", "f1g2", "f8e7", "g1f3", "e8g8"]  # Dutch Defense
]


def getOpeningMove(gs, validMoves):
    # Lấy lịch sử ván đấu hiện tại dưới dạng UCI để tiện so sánh với sách
    gameHistory = [m.getUCI() for m in gs.moveLog]
    currentTurn = len(gameHistory)

    possibleMoves = []
    # Lục tung sách xem có line nào khớp với lịch sử bàn cờ hiện tại không
    for line in OPENING_BOOK:
        if len(line) > currentTurn and line[:currentTurn] == gameHistory:
            possibleMoves.append(line[currentTurn])

    if len(possibleMoves) > 0:
        # Nếu có nhiều đường đi có thể chọn -> Chọn ngẫu nhiên 1 đường để game đa dạng
        chosenUCI = random.choice(possibleMoves)
        # Tìm object Move tương ứng trong danh sách các nước đi hợp lệ
        for move in validMoves:
            if move.getUCI() == chosenUCI:
                return move

    # Nếu hết sách (hoặc đối thủ đánh tào lao không có trong sách), trả về None để AI tự tính toán
    return None
# Mã thích đứng giữa trung tâm
knightScores = [[-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20,   0,   0,   0,   0, -20, -40],
                [-30,   0,  10,  15,  15,  10,   0, -30],
                [-30,   5,  15,  20,  20,  15,   5, -30],
                [-30,   0,  15,  20,  20,  15,   0, -30],
                [-30,   5,  10,  15,  15,  10,   5, -30],
                [-40, -20,   0,   5,   5,   0, -20, -40],
                [-50, -40, -30, -30, -30, -30, -40, -50]]

# Tượng thích đường chéo thoáng
bishopScores = [[-20, -10, -10, -10, -10, -10, -10, -20],
                [-10,   0,   0,   0,   0,   0,   0, -10],
                [-10,   0,   5,  10,  10,   5,   0, -10],
                [-10,   5,   5,  10,  10,   5,   5, -10],
                [-10,   0,  10,  10,  10,  10,   0, -10],
                [-10,  10,  10,  10,  10,  10,  10, -10],
                [-10,   5,   0,   0,   0,   0,   5, -10],
                [-20, -10, -10, -10, -10, -10, -10, -20]]

whitePawnScores = [[800, 800, 800, 800, 800, 800, 800, 800],
                   [50,  50,  50,  50,  50,  50,  50,  50],
                   [10,  10,  20,  30,  30,  20,  10,  10],
                   [ 5,   5,  10,  25,  25,  10,   5,   5],
                   [ 0,   0,   0,  20,  20,   0,   0,   0],
                   [ 5,  -5, -10,   0,   0, -10,  -5,   5],
                   [ 5,  10,  10, -20, -20,  10,  10,   5],
                   [ 0,   0,   0,   0,   0,   0,   0,   0]]

blackPawnScores = whitePawnScores[::-1] # Tốt Đen thì lật ngược mảng Trắng lại

whiteKingScores = [[-30, -40, -40, -50, -50, -40, -40, -30],
                   [-30, -40, -40, -50, -50, -40, -40, -30],
                   [-30, -40, -40, -50, -50, -40, -40, -30],
                   [-30, -40, -40, -50, -50, -40, -40, -30],
                   [-20, -30, -30, -40, -40, -30, -30, -20],
                   [-10, -20, -20, -20, -20, -20, -20, -10],
                   [ 20,  20,   0,   0,   0,   0,  20,  20],
                   [ 20,  30,  10,   0,   0,  10,  30,  20]] # Điểm cao ở g1 (30) và c1 (20)

blackKingScores = whiteKingScores[::-1]
# Xe cực kỳ thích hàng 7 (để ăn Tốt) và các cột trung tâm (d, e). Ghét bị nhốt ở góc.
rookScores = [[0, 0, 5, 10, 10, 5, 0, 0],
              [5, 10, 10, 10, 10, 10, 10, 5],  # Hàng 7 của Trắng
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [-5, 0, 0, 0, 0, 0, 0, -5],
              [0, 0, 0, 5, 5, 0, 0, 0]]

# Hậu đứng giữa tàm tạm, nhưng chủ yếu tránh bị nhốt sát góc bàn cờ
queenScores = [[-20, -10, -10, -5, -5, -10, -10, -20],
               [-10, 0, 0, 0, 0, 0, 0, -10],
               [-10, 0, 5, 5, 5, 5, 0, -10],
               [-5, 0, 5, 5, 5, 5, 0, -5],
               [0, 0, 5, 5, 5, 5, 0, -5],
               [-10, 5, 5, 5, 5, 5, 0, -10],
               [-10, 0, 5, 0, 0, 0, 0, -10],
               [-20, -10, -10, -5, -5, -10, -10, -20]]

# VUA TÀN CUỘC (Endgame): Thích lao ra chiếm trung tâm bàn cờ!
whiteKingEndgameScores = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -30, 0, 0, 0, 0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50]]

blackKingEndgameScores = whiteKingEndgameScores[::-1]

# Cập nhật lại từ điển (Chèn thêm R và Q)
piecePositionScores = {"N": knightScores, "B": bishopScores, "R": rookScores, "Q": queenScores,
                       "wp": whitePawnScores, "bp": blackPawnScores,
                       "wK": whiteKingScores, "bK": blackKingScores}


#Helper method to make first recursive call
def findBestMove(gs, validMoves):
    global nextMove

    # 1. HỎI SÁCH KHAI CUỘC TRƯỚC
    bookMove = getOpeningMove(gs, validMoves)
    if bookMove is not None:
        return bookMove  # Có trong sách thì chốt luôn, tốc độ phản hồi 0.001s !

    # 2. HẾT SÁCH HOẶC RA KHỎI KHAI CUỘC THÌ TỰ VẮT ÓC TÍNH TOÁN
    nextMove = validMoves[0]  # Bảo hiểm văng game
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -float('inf'), float('inf'), 1 if gs.whiteToMove else -1)

    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


def scoreMove(move):
    moveScore = 0

    # 1. Ưu tiên số 1: Ăn quân (MVV-LVA)
    if move.pieceCaptured != '--':
        # Điểm = (Giá trị con mồi * 10) - (Giá trị kẻ đi săn)
        # Nhân 10 để đảm bảo ưu tiên con mồi to trước. VD: PxQ (10*900 - 100 = 8900đ) > QxQ (10*900 - 900 = 8100đ)
        victimValue = pieceScore.get(move.pieceCaptured[1], 0)
        attackerValue = pieceScore.get(move.pieceMoved[1], 0)
        moveScore += (10 * victimValue) - attackerValue

    # 2. Ưu tiên số 2: Phong cấp
    if move.isPawnPromotion:
        moveScore += 900  # Tương đương một con Hậu

    # (Sau này ở các bước sau mình sẽ thêm Killer Move vào đây)

    return moveScore


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, ttable

    # 1. KIỂM TRA DỨT ĐIỂM HÒA/THUA TRƯỚC TIÊN
    # Phải check cái này trước khi tra sổ tay để nếu bị chiếu bí/hòa là báo động ngay
    if gs.checkmate:
        return -CHECKMATE - depth
    elif gs.stalemate:
        return STALEMATE

    # 2. ĐỌC SỔ TAY (Transposition Table)
    hash_key = gs.getStateID()
    # FIX LỖI: CHỈ dùng sổ tay nếu thế cờ này CHƯA từng bị lặp lại (count < 2).
    # Nếu count >= 2, bắt buộc phải tự tính để né đòn Hòa cờ (Tránh bệnh Mù lòa Sổ tay)
    if gs.posHistory.get(hash_key, 0) < 2 and hash_key in ttable:
        entry = ttable[hash_key]
        if entry['depth'] >= depth:
            if entry['flag'] == 'EXACT':
                return entry['score']
            elif entry['flag'] == 'UPPERBOUND' and entry['score'] <= alpha:
                return entry['score']
            elif entry['flag'] == 'LOWERBOUND' and entry['score'] >= beta:
                return entry['score']

    if depth == 0:
        return findMoveQuiescence(gs, alpha, beta, turnMultiplier)

    validMoves.sort(key=scoreMove, reverse=True)

    maxScore = -float('inf')
    alphaOrig = alpha  # Lưu lại alpha ban đầu để chốc nữa đối chiếu

    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        # Cắt tỉa Alpha-Beta
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

    # 3. GHI SỔ TAY
    flag = 'EXACT'
    if maxScore <= alphaOrig:
        flag = 'UPPERBOUND'
    elif maxScore >= beta:
        flag = 'LOWERBOUND'

    ttable[hash_key] = {'score': maxScore, 'depth': depth, 'flag': flag}

    return maxScore


def findMoveQuiescence(gs, alpha, beta, turnMultiplier):
    # 1. Xử lý triệt để Chiếu bí và Hòa cờ ngay trong Quiescence
    if gs.checkmate:
        return -CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    is_in_check = gs.inCheck()

    # 2. CHỈ ĐƯỢC PHÉP "ĐỨNG IM" (Stand Pat) NẾU VUA ĐANG AN TOÀN
    if not is_in_check:
        stand_pat = turnMultiplier * scoreBoard(gs)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

    validMoves = gs.getValidMoves()

    if gs.checkmate:
        return -CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    # 3. LỌC NƯỚC ĐI TÙY THEO TÌNH TRẠNG VUA
    if is_in_check:
        # Nếu đang bị chiếu, BẮT BUỘC duyệt TẤT CẢ các nước hợp lệ để tìm đường sống
        movesToSearch = validMoves
    else:
        # Nếu an toàn, chỉ duyệt các nước ăn quân như bình thường
        movesToSearch = [move for move in validMoves if move.pieceCaptured != '--']

    # 4. Áp dụng MVV-LVA để sắp xếp nước đi (Code Bước 1 của mày)
    movesToSearch.sort(key=scoreMove, reverse=True)

    for move in movesToSearch:
        gs.makeMove(move)
        score = -findMoveQuiescence(gs, -beta, -alpha, -turnMultiplier)
        gs.undoMove()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

# HÀM ĐÁNH GIÁ TƯ DUY CẤU TRÚC TỐT
def evaluatePawnStructure(board):
    pawn_score = 0
    # Lọc nhanh tọa độ cột của tất cả Tốt Trắng và Tốt Đen trên bàn cờ
    w_pawns = [c for r in range(8) for c in range(8) if board[r][c] == 'wp']
    b_pawns = [c for r in range(8) for c in range(8) if board[r][c] == 'bp']

    for col in range(8):
        w_count = w_pawns.count(col)
        b_count = b_pawns.count(col)

        # 1. Phạt TỐT CHỒNG (Doubled Pawns)
        if w_count > 1: pawn_score -= 15 * w_count
        if b_count > 1: pawn_score += 15 * b_count

        # 2. Phạt TỐT CÔ LẬP (Isolated Pawns)
        if w_count > 0 and (col - 1 not in w_pawns) and (col + 1 not in w_pawns):
            pawn_score -= 10 * w_count
        if b_count > 0 and (col - 1 not in b_pawns) and (col + 1 not in b_pawns):
            pawn_score += 10 * b_count

        # 3. Thưởng TỐT THÔNG (Passed Pawns)
        if w_count > 0 and (col not in b_pawns) and (col - 1 not in b_pawns) and (col + 1 not in b_pawns):
            pawn_score += 20 * w_count
        if b_count > 0 and (col not in w_pawns) and (col - 1 not in w_pawns) and (col + 1 not in w_pawns):
            pawn_score -= 20 * b_count

    return pawn_score


def evaluateKingSafety(board, whiteKingLoc, blackKingLoc, isEndgame):
    if isEndgame: return 0  # Tàn cuộc thì Vua là trùm, phải chạy ra ngoài nên không tính lá chắn

    score = 0
    wK_r, wK_c = whiteKingLoc
    bK_r, bK_c = blackKingLoc

    # 1. Xét Tốt bảo vệ Vua Trắng (Chỉ xét nếu Vua chưa lao lên cao)
    if wK_r >= 6:
        shield = 0
        for c in range(max(0, wK_c - 1), min(8, wK_c + 2)):
            if board[wK_r - 1][c] == 'wp' or board[wK_r - 2][c] == 'wp':
                shield += 1
        if shield < 2: score -= 50  # Phạt nặng nếu mất Tốt bảo vệ

    # 2. Xét Tốt bảo vệ Vua Đen
    if bK_r <= 1:
        shield = 0
        for c in range(max(0, bK_c - 1), min(8, bK_c + 2)):
            if board[bK_r + 1][c] == 'bp' or board[bK_r + 2][c] == 'bp':
                shield += 1
        if shield < 2: score += 50  # Phạt điểm (Cộng cho Trắng)

    return score

# THUẬT TOÁN DỒN VUA ĐỊCH VÀO GÓC KHI ĐANG THẮNG ÁP ĐẢO
def evaluateMopUp(winningKingPos, losingKingPos):
    mopUpScore = 0
    losingKingRow, losingKingCol = losingKingPos
    winningKingRow, winningKingCol = winningKingPos

    # 1. ÉP VUA ĐỊCH RA RÌA/GÓC BÀN CỜ
    # Tăng hệ số từ 10 lên 20 (Thưởng cực to để ép nó ra biên)
    centerDistRow = max(3 - losingKingRow, losingKingRow - 4)
    centerDistCol = max(3 - losingKingCol, losingKingCol - 4)
    mopUpScore += (centerDistRow + centerDistCol) * 20

    # 2. XÁCH VUA MÌNH LẠI GẦN VUA ĐỊCH ĐỂ HỖ TRỢ CHIẾU HẾT
    # Tăng hệ số từ 4 lên 10 (Để đè bẹp cái điểm trừ của KingEndgame)
    distRow = abs(winningKingRow - losingKingRow)
    distCol = abs(winningKingCol - losingKingCol)
    mopUpScore += (14 - (distRow + distCol)) * 10

    return mopUpScore
#A positive score is good for white, a negative score is good for black
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE

    whiteMaterial = 0
    blackMaterial = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w' and square[1] not in ('p', 'K'):
                whiteMaterial += pieceScore[square[1]]
            elif square[0] == 'b' and square[1] not in ('p', 'K'):
                blackMaterial += pieceScore[square[1]]

    # Tàn cuộc khi 1 trong 2 bên đã cạn kiệt quân nặng (bằng 0)
    # HOẶC tổng tài nguyên cả 2 bên rớt xuống dưới 1500
    isEndgame = (whiteMaterial == 0) or (blackMaterial == 0) or (whiteMaterial + blackMaterial < 1500)

    # 2. BẮT ĐẦU TÍNH ĐIỂM
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0

                # Chuyển pha cho VUA
                if square[1] == "K":
                    if isEndgame:  # Nếu là Tàn cuộc -> Dùng mảng máu chiến
                        piecePositionScore = whiteKingEndgameScores[row][col] if square[0] == 'w' else \
                        blackKingEndgameScores[row][col]
                    else:  # Nếu là Khai/Trung cuộc -> Dùng mảng núp lùm
                        piecePositionScore = piecePositionScores[square][row][col]
                # Tính điểm cho các quân khác
                elif square[1] == "p":
                    piecePositionScore = piecePositionScores[square][row][col]
                elif square[1] in piecePositionScores:
                    piecePositionScore = piecePositionScores[square[1]][row][col]

                # Cộng trừ tùy phe
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore

    # 3. Đánh giá chiến lược Cấu trúc Tốt
    score += evaluatePawnStructure(gs.board)

    # ---> MÓC THÊM AN TOÀN VUA VÀO ĐÂY <---
    score += evaluateKingSafety(gs.board, gs.whiteKingLocation, gs.blackKingLocation, isEndgame)
    # 4. CHIẾN THUẬT MOP-UP: Tự động chuyển hóa cờ tàn thành Chiếu hết
    if isEndgame:
        # Nếu Trắng đang thắng áp đảo (Hơn từ 1 Tượng/Mã trở lên)
        if score > 300:
            score += evaluateMopUp(gs.whiteKingLocation, gs.blackKingLocation)
        # Nếu Đen đang thắng áp đảo
        elif score < -300:
            score -= evaluateMopUp(gs.blackKingLocation, gs.whiteKingLocation)
    # ---------------------------

    return score


#Score the board based on material.
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score