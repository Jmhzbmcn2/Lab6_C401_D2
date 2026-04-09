# Mô Tả Dự Án: Trợ Lý Y Tế Vinmec (Medical RAG Agent)

## 1. Giới Thiệu Chung
Dự án là một **Hệ thống chuyên gia nội bộ (RAG System)** dành cho bệnh viện Vinmec, chuyên hỗ trợ giải đáp tự động và tra cứu nhanh giá các dịch vụ y tế, chi nhánh áp dụng và các thông tin liên quan. 

Hệ thống được thiết kế theo tư duy **Agentic Workflow** hiện đại nhất hiện nay. Thay vì sử dụng mô hình ReAct Agent "hộp đen" truyền thống dễ dẫn đến ảo giác (hallucination), dự án được xây dựng toàn bộ trên framework **LangGraph** giúp kiểm soát trạng thái (state) một cách minh bạch, tách bạch tuyệt đối giữa logic suy luận của LLM và logic nghiệp vụ.

## 2. Công Nghệ Sự Dụng
- **Core AI**: Google Gemini API (model `gemini-2.5-flash-lite`).
- **Orchestration**: LangGraph (Quản lý các state và luồng thực thi đồ thị).
- **Backend API**: FastAPI (Đảm bảo tốc độ cao, hỗ trợ Async).
- **Frontend**: Vue.js 3 + Vite, giao diện mô phỏng khung chat hiện đại, hỗ trợ render Markdown.
- **Database (Hybrid Search)**:
  - **Vector DB**: ChromaDB (Sử dụng Embedding `keepitreal/vietnamese-sbert` để tìm kiếm ngữ nghĩa).
  - **Relational DB**: SQLite (Lưu trữ bảng giá thực, tra cứu bằng ID, keyword fallback).
- **Observability**: Loguru (Ghi log chi tiết từng Node) & Tracing trả về Frontend.

## 3. Kiến Trúc "Clean Architecture"
Hệ thống Backend được thiết kế theo chuẩn **Clean Architecture**, tách biệt hoàn toàn các lớp trách nhiệm:
- **`app/prompts/`**: Tách toàn bộ các câu lệnh điều hướng LLM (System Prompts) ra thành cấu hình tĩnh, không lẫn vào file code xử lý.
- **`app/tools/`**: Chứa "Pure business logic" - các nghiệp vụ lõi như gọi vào DB, đối chiếu chi nhánh. Lớp này không gọi LLM để có thể dễ dàng Unit Test.
- **`app/services/`**: Các adapter giao tiếp với bên ngoài:
  - `llm_service.py`: Chuyên gọi qua Google Gemini.
  - `retrieval_service.py`: Chuyên gọi qua ChromaDB.
- **`app/graph/nodes/`**: Mỗi Node LangGraph là một file riêng biệt độc lập (`query_understanding.py`, `retrieval.py`...). Trách nhiệm duy nhất của chúng là điều phối lấy state cũ, gọi service/tool tương ứng và cập nhật state mới.
- **`app/api/`**: Nơi phơi bày (expose) API cho Client (Frontend).

## 4. Luồng Xử Lý Của Agent (Agentic Workflow)
Mỗi câu hỏi của User sẽ được đưa qua một đồ thị chuỗi trạng thái (StateGraph) bao gồm các bước sau:

1. **`query_understanding`**: 
   - Gọi trực tiếp LLM với chế độ "Structured Output". LLM sẽ parse câu hỏi của khách thành 1 cục JSON bóc tách `normalized_query` (tên dịch vụ lõi) và `intent_branch` (ý định chi nhánh).
2. **`retrieval`**:
   - Dùng `normalized_query` tạo vector để search trên ChromaDB. Trả về một tập các ID dịch vụ tiềm năng.
3. **`tool_execution`**:
   - Nhận danh sách ID từ ChromaDB, truy vấn trực tiếp vào SQLite để lấy "Sự Thật" (bảng giá, nhóm dịch vụ).
   - *Logic Fallback*: Nếu khoảng cách vector DB quá lớn hoặc không trúng, lập tức fallback dùng Keyword Search của SQLite.
4. **Conditional Routing (`edges`)**: 
   - Nếu Data Tool trả về rỗng -> Điều hướng sang `fallback`.
   - Nếu có Data -> Điều hướng sang `synthesis`.
5. **`synthesis` / `fallback`**:
   - `Synthesis`: Trộn câu hỏi và Context bảng giá chuẩn từ file tool_execution vào 1 prompt cuối, gọi LLM thế hệ văn bản để sinh ra câu trả lời gọn gàng, markdown tự nhiên nhất.

## 5. Hướng Dẫn Vận Hành Môi Trường Local

**Bước 1: Chạy DB Pipeline (Nạp dữ liệu)**
```bash
python data_pipeline/data_ingestion.py     # Nạp data sạch vào SQLite
python data_pipeline/vector_indexer.py     # Embed data vào ChromaDB
```

**Bước 2: Chạy Backend (FastAPI)**
```bash
cd backend
python -m uvicorn app.main:app --reload
```
API sẽ lắng nghe tại `http://127.0.0.1:8000`.

**Bước 3: Chạy Frontend (Vue.js)**
```bash
cd frontend
npm install
npm run dev
```
Giao diện Chatbot sẽ hiển thị trực quan tại `http://localhost:3000`. Cung cấp công cụ Debug trace real-time chi tiết từng bước mà LangGraph chạy ở Backend.
