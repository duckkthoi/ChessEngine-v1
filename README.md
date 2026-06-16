# Chess AI Engine – Python & Pygame

Một dự án phát triển game Cờ vua tích hợp AI Máy tính (Chess Engine) hoàn chỉnh được viết hoàn toàn bằng **Python** và thư viện đồ họa **Pygame**. Dự án triển khai toàn bộ các bộ luật cờ vua quốc tế hiện hành cùng hệ thống tìm kiếm nước đi tối ưu hóa sâu, mang lại trải nghiệm chơi mượt mà và thử thách.

---

## 🚀 Tính Năng Cốt Lõi

### 1. Luật Chơi & Quản Lý Trạng Thái (`ChessBot.py`)
* **Bàn cờ chuẩn:** Biểu diễn trạng thái 8x8 với cơ chế ghi log lịch sử nước đi (`moveLog`), hỗ trợ tính năng **Undo (Hoàn tác nước đi)** không giới hạn và đồng bộ chính xác.
* **Bộ luật đầy đủ:** Triển khai chính xác các luật nâng cao bao gồm: Nhập thành (Castling - cả cánh Vua và cánh Hậu), Bắt tốt qua đường (En Passant), và Phong cấp Tốt (Pawn Promotion - mặc định lên Hậu).
* **Xử lý chiếu và chiếu bí:** Thuật toán lọc nước đi hợp lệ (`getValidMoves`) kiểm tra toàn bộ các hướng tấn công để xác định trạng thái Chiếu Vua (In Check), Chiếu bí (Checkmate), hoặc Hòa cờ (Stalemate).
* **Xử lý Hòa cờ tự động theo luật FIDE:**
    * **Lặp lại 3 lần thế cờ (3-fold repetition):** Tối ưu bằng hàm băm trạng thái nâng cao dùng Tuple, tính toán cực nhanh qua C-engine của Python.
    * **Không đủ quân để chiếu bí (Insufficient Material):** Tự động nhận diện các kịch bản hòa cờ kinh điển như Vua vs Vua, Vua + Mã vs Vua, Vua + Tượng vs Vua.
    * **Luật 50 nước liên tiếp (50-move rule):** Bộ đếm tự động tăng tiến và reset ngay lập tức khi có nước đẩy Tốt hoặc ăn quân, chốt hòa chuẩn xác khi chạm mốc 100 ply liên tiếp.

### 2. Giao Diện Đồ Họa & Trải Nghiệm Người Chơi (`ChessMain.py`)
* **Hiển thị trực quan:** Tô sáng ô cờ đang chọn (Màu xanh lam) và hiển thị toàn bộ các ô có thể di chuyển hợp lệ (Màu hồng) của quân cờ đó.
* **Bảng Log nước đi thông minh (Move Log Panel):** Ghi nhận biên bản ván đấu theo chuẩn ký hiệu cờ vua (Chess Notation) như `e4`, `Nf3`, `Bxf7`, `O-O`. Thiết kế thuật toán chống tràn chữ tự động bẻ dòng và phân chia đa cột linh hoạt khi ván đấu kéo dài.
* **Hệ thống âm thanh sống động:** Hiệu ứng âm thanh chân thực được tách biệt rõ ràng cho 3 kịch bản: nước đi thường (`move`), ăn quân (`capture`), và chiếu Vua (`check`).
* **Chế độ Replay (Xem lại ván đấu) nâng cao:** Khi trận đấu kết thúc, người chơi có thể kích hoạt chế độ Replay thông qua giao diện nút nhấn (`<`, `>`, `Exit`) hoặc phím mũi tên bàn phím để tiến/lùi từng nước cờ có kèm hiệu ứng chuyển động hoạt họa (Animation).

### 3. Trí Tuệ Nhân Tạo Thông Minh (`SmartMoveFinder.py`)
* **Sách khai cuộc đồ sộ (Opening Book):** Tích hợp hơn 40 hệ thống khai cuộc và biến thể phổ biến nhất thế giới (Ruy Lopez, Berlin Defense, Sicilian Najdorf/Dragon/Sveshnikov, French, Caro-Kann, King's Indian, Nimzo-Indian, Queen's Gambit, London System, v.v.) giúp AI phản hồi nước đi trong 0.001 giây ở giai đoạn đầu trận.
* **Thuật toán Tìm kiếm Nâng cao:**
    * **Negamax Alpha-Beta Pruning:** Tìm kiếm sâu tới 4 lớp nước đi (`DEPTH = 4`), cắt tỉa các nhánh cờ thừa giúp tối ưu hóa hiệu suất tính toán.
    * **Sắp xếp nước đi (Move Ordering):** Áp dụng nguyên lý MVV-LVA (*Most Valuable Victim - Least Valuable Attacker*) phối hợp ưu tiên phong cấp, đưa các nước đi ăn quân béo bở lên đầu để tối đa hóa tỷ lệ cắt tỉa nhánh cờ.
    * **Quiescence Search (Tìm kiếm tĩnh tâm):** Triển khai tìm kiếm sâu thêm ở các biến thế ăn quân hoặc chống chiếu nhằm loại bỏ "hiệu ứng chân trời" (Horizon Effect), giúp AI không đánh giá sai thế trận.
    * **Bảng Chuyển Vị (Transposition Table):** Cuốn sổ tay ghi nhớ mã hóa trạng thái bàn cờ giúp AI không cần tính toán lại các thế cờ trùng lặp, tích hợp logic né bẫy lặp lại thế cờ dẫn tới hòa khi AI đang ở thế thắng.
* **Hàm Đánh Giá Chiến Thuật Toàn Diện (Evaluation Function):**
    * *Giá trị quân cờ (Material):* Định điểm chuẩn cho từng loại quân.
    * *Bảng vị trí (Piece-Square Tables):* Ép Mã chiếm trung tâm, Tượng chiếm đường chéo thoáng, Xe chiếm hàng 7 ăn Tốt và cột mở, kiểm soát Vua núp góc trung cuộc và lao ra trung tâm lúc tàn cuộc.
    * *Cấu trúc Tốt (Pawn Structure):* Khấu trừ điểm Tốt chồng (Doubled), Tốt cô lập (Isolated) và cộng thưởng lớn cho Tốt thông (Passed).
    * *An toàn Vua (King Safety):* Đánh giá lá chắn bảo vệ xung quanh Vua để phạt các lỗi hở sườn.
    * *Chiến thuật Mop-Up (Dồn Vua tàn cuộc):* Khi AI chiếm ưu thế áp đảo ở cờ tàn, thuật toán sẽ tự động chuyển pha ép Vua đối phương vào góc/biên bàn cờ đồng thời xách Vua mình lên hỗ trợ ép chiếu bí nhanh chóng.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
├── ChessBot.py          # Xử lý Logic trò chơi, tạo nước đi hợp lệ và quản lý trạng thái bàn cờ
├── ChessMain.py         # Điểm khởi chạy ứng dụng (Main Driver), xử lý UI/UX và tương tác từ chuột/phím
├── SmartMoveFinder.py   # Bộ não AI Engine (Thuật toán tìm kiếm, sách khai cuộc và hàm đánh giá)
├── images/              # Chứa các file hình ảnh quân cờ (wp.png, bR.png, v.v.)
└── sounds/              # Chứa các file hiệu ứng âm thanh (move.ogg, capture.ogg, check.ogg)
