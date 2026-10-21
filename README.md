# Music Demo

Web app demo nghe nhạc kiểu Spotify, có mục **gợi ý bài hát**. Khách vẫn nghe được nhạc; đăng nhập để có yêu thích, lịch sử nghe và gợi ý riêng.

- **Backend:** FastAPI + SQLite (Python)
- **Frontend:** React + Vite
- **Dữ liệu:** Spotify Tracks Dataset (Kaggle)

## Yêu cầu

- Python 3.11
- Node.js 18 trở lên
- File `dataset.csv` (Spotify Tracks Dataset, tải trên Kaggle)

## Cấu trúc

```
music-demo/
├─ backend/    # API, DB, recommender
└─ frontend/   # giao diện web
```

## 1. Chạy backend

Mở terminal tại thư mục `backend`:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Đặt file `dataset.csv` vào thư mục `backend`, rồi nạp dữ liệu (chỉ làm một lần):

```powershell
python -m scripts.seed_db --spotify dataset.csv --per-genre 40
```

Chạy server:

```powershell
uvicorn app.main:app --reload
```

Backend chạy ở http://localhost:8000. Xem và thử API tại http://localhost:8000/docs.

> Chưa có `dataset.csv`? Chạy `python -m scripts.seed_db` (không kèm tham số) để tạo 240 bài hát giả.

## 2. Chạy frontend

Mở **terminal thứ hai** tại thư mục `frontend`:

```powershell
npm install
npm run dev
```

Mở http://localhost:5173 trên trình duyệt. Cần bật backend trước.

Nếu backend chạy ở địa chỉ khác, copy `.env.example` thành `.env` rồi sửa `VITE_API_URL`.

## 3. Dùng thử

1. Vào trang chủ, bấm một bài để nghe. Chưa đăng nhập vẫn nghe được, mục gợi ý hiển thị "Đang thịnh hành".
2. Bấm **Đăng nhập** > **Đăng ký** để tạo tài khoản.
3. Thả ♡ vài bài cùng thể loại và nghe vài bài (bấm **x5** ở thanh phát để tua nhanh thời gian mô phỏng).
4. Về trang chủ: mục **★ Gợi ý cho bạn** sẽ nghiêng theo gu của bạn. **Yêu thích** và **Lịch sử nghe** nằm ở thanh bên.

> Trình phát là **mô phỏng**: tiến độ và việc tự chuyển bài do app tự chạy. Dataset Spotify không có file nhạc nên không có âm thanh thật.

## Ghép recommender thật

Đặt file `recommender.py` cạnh thư mục `backend/app/`, có 2 hàm:

```python
def recommend(user_id: int, k: int = 20) -> list[dict]: ...
def similar(song_id: int, k: int = 10) -> list[dict]: ...
# mỗi phần tử: {"song_id": int, "score": float, "reason": str}
```

- `song_id` là `songs.id` trong DB (không phải `track_id` của Spotify, cái đó nằm ở cột `spotify_id`).
- Dữ liệu đọc từ `backend/music.db`: bảng `songs` (cột `features` là JSON gồm danceability, energy, valence, tempo...), `favorites`, `listen_history`.
- Không có file này thì app tự dùng recommender giả (mock) và hiện nhãn "(mock)" ở trang chủ.

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `no such column: songs.spotify_id` | DB cũ. Tắt uvicorn, xóa `music.db`, seed lại. |
| Trang chủ báo "Không kết nối được backend" | Chưa chạy uvicorn, hoặc sai `VITE_API_URL`. |
| Muốn nạp lại dữ liệu từ đầu | Tắt uvicorn, xóa `music.db`, chạy lại `seed_db`. Tài khoản và yêu thích cũng mất. |
| Lỗi cú pháp khi chạy backend | Venv đang dùng Python cũ. Kiểm tra `python --version` phải là 3.11. |