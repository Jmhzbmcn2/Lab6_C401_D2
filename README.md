# Vinmec Healthcare Assistant (LangGraph RAG System)

Hệ thống tư vấn giá dịch vụ y tế tự động (RAG) được xây dựng dành cho bệnh viện Vinmec, sử dụng kiến trúc hoàn toàn dựa trên sự phát triển theo mô hình LangGraph phân tách thay vì dùng LangChain ReAct Agents ẩn.
Dự án được chia làm Frontend độc lập và Backend API.

## Cấu Trúc Thư Mục Mới (Clean Architecture)

```text
Lab06/
├── backend/                  # Chứa toàn bộ API và LangGraph Logic
│   ├── .env                  # Cấu hình biến môi trường (ví dụ API key)
│   ├── requirements.txt      # Thư viện Python yêu cầu
│   └── app/
│       ├── main.py           # Khởi chạy server FastAPI
│       ├── api/              # Định nghĩa router (POST /chat)
│       ├── graph/            # Định nghĩa luồng LangGraph (.state, .nodes, .builder)
│       ├── services/         # Tương tác với LLM API (như Cloudflare)
│       ├── database/         # Kết nối CSDL (SQLite, ChromaDB)
│       └── utils/            # Thư viện dùng chung, Loguru Logging
├── frontend/                 # Giao diện người dùng (Vue 3 + Vite)
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.vue           # Header và Layout chính
│       └── components/       # Giao diện Chat, xử lý Markdown và Debug Log
├── data/                     # Thư mục lưu bảng Excel gốc (nếu có)
├── database/                 # Thư mục chứa file SQLite (.db) và ChromaDB
└── data_pipeline/            # Kịch bản nạp và thiết lập dữ liệu (Chuyển từ src/ cũ)
    ├── data_ingestion.py     # Đọc dữ liệu từ file dữ liệu Excel (.xlsx) để nạp vào DB SQLite
    └── vector_indexer.py     # Sinh các vectors bằng mô hình Sentence-Transformers nạp vào Chroma
```

## Hướng Dẫn Sử Dụng

### 1. Chuẩn Bị Dữ Liệu Ban Đầu
Bạn chỉ cần thao tác bước này nếu database (SQLite / Chroma) chưa có sẵn hoặc có cập nhật bảng giá.
- Chạy cập nhật SQLite: `python data_pipeline/data_ingestion.py`
- Chạy cập nhật ChromaDB: `python data_pipeline/vector_indexer.py`

### 2. Khởi Động Backend API
Mở terminal và trỏ về thư mục `backend/`:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Server sẽ chạy ở `http://localhost:8000`.

### 3. Khởi Động Frontend Chat
Mở terminal mới và trỏ về thư mục `frontend/`:
```bash
cd frontend
npm install
npm run dev
```
Trình duyệt sẽ hiển thị ở `http://localhost:5173`. Bạn có thể tương tác, xem lịch sử và dễ dàng mở "Debug Trace Tracker" dành cho Dev ở mỗi câu trả lời của Trợ lý.
