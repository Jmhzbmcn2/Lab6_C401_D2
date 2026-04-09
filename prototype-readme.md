# Dự Án AI Trợ Lý Y Tế Vinmec (Medical RAG Agent - Lab 06)

## Mô tả ngắn
Hệ thống giúp người dùng tra cứu giá các dịch vụ y tế, y khoa và hỗ trợ sàng lọc y tế (triage). Khác với các chatbot truyền thống, hệ thống này được thiết kế theo tư duy **Agentic Workflow**, có khả năng kiểm soát các tình huống khẩn cấp, chủ động yêu cầu cung cấp thêm thông tin từ người dùng (Clarification) nếu mức độ tự tin thấp, và hỗ trợ so sánh giá giữa các chi nhánh.

## Status: Đã Hoàn Thiện
- **Kiến trúc luồng xử lý**: Sử dụng LangGraph phân tách chi tiết các tác vụ thành Node độc lập (Emergency Check, Query Understanding, Compare Price, Retrieval, Tool Execution, LLM Synthesis, Clarification, Fallback) thay vì sử dụng ReAct Agent "hộp đen".
- **Backend API**: Web socket API xây dựng với FastAPI hiệu năng cao.
- **Frontend**: Ứng dụng Vue.js 3 + Vite, có giao diện khung chat hiện đại, hỗ trợ render Markdown và quan sát Debug Trace trực quan thời gian thực.
- **Database (Hybrid Search)**: Tích hợp linh hoạt Vector DB (ChromaDB + SBERT tiếng Việt) và Relational DB (SQLite).
- **Core AI**: Tích hợp Google Gemini 2.5 Flash-lite qua API.

## Các Tính Năng Nổi Bật
1. **Emergency Check (Cấp cứu)**: Có luồng chặn chốt đầu với các từ khóa khẩn cấp -> Điều hướng ngay vào nhánh xử lý cấp cứu, không qua gọi LLM vô ích.
2. **Intention Parsing**: Bóc tách chính xác ý định (Hỏi giá, So sánh giá, Hỏi chung...) và chuẩn hóa câu truy vấn.
3. **Compare Price Agent**: Cho phép so sánh song song giá của một dịch vụ giữa nhiều chi nhánh.
4. **Hybrid Retrieval**: Vector semantic search trích xuất `ID dịch vụ` trên ChromaDB -> Tra cứu xác thực thông tin tại SQLite thông qua chuyên gia `Tool Execution`.
5. **Anti-Hallucination & Clarification**: Chơi theo cơ chế `confidence_score`. Nếu kết quả tìm kiếm có độ tự tin < 25%, Agent lật sang Node `Clarification` chủ động yêu cầu bệnh nhân cung cấp thêm thông tin minh bạch, loại bỏ ảo giác (Hallucination).

## Thông Tin Công Nghệ & Prompt Engineering
- **Giao diện (UI)**: Xây dựng và tinh chỉnh nhanh qua tài nguyên Claude Artifacts.
- **Lõi AI**: Tích hợp Google Gemini 2.0 Flash thông qua Google AI Studio API cho tốc độ phản hồi cực nhanh.
- **Kỹ thuật Prompt & Triage**: Sử dụng `system_prompt` kết hợp **Few-shot Prompting** để huấn luyện LLM bóc tách ý định (Query Understanding). Đặc biệt, cấu hình cung cấp 10 few-shot examples cho các **triệu chứng phổ biến** để tự động định hướng (triage) người bệnh đến đúng khoa lâm sàng:
  1. *Đau đầu, chóng mặt kéo dài* ➔ Khám nội thần kinh
  2. *Đau dạ dày, ợ hơi, ợ chua* ➔ Khám nội tiêu hóa
  3. *Ho khan, tức ngực, khó thở nhẹ* ➔ Khám hô hấp
  4. *Nhói tim, hồi hộp, tim đập nhanh* ➔ Khám tim mạch

*(Luồng dữ liệu này giúp cho Agent đưa ra gợi ý dịch vụ giá tiền chuẩn xác nhất dựa theo triệu chứng, thay vì yêu cầu người dùng phải gõ chính xác tên gói khám)*.

## Bảng Phân Công Nhóm
| Thành viên | Vai trò | Trách nhiệm chính | Mảng Code đảm nhận |
|-----------|---------|------------------|---------------|
| **Nguyễn Hoàng Việt** | Graph Orchestrator | Dịch chuyển Clean Architecture, nối các Node, xây dựng `StateGraph` v2 điều phối luồng quy định Agent, Backend FastAPI. | `backend/app/graph/builder.py`, `edges.py`, `state.py`, `main.py` |
| **Đậu Văn Quyền** | Prompt Engineer | Mài dũa prompt chuẩn giọng điệu y khoa tiếng Việt, tinh chỉnh System prompts bóc tách JSON và Sinh câu trả lời chuẩn xác. | Toàn bộ `backend/app/prompts/` |
| **Hoàng Ngọc Anh** | Triage & Edge Cases | Viết thuật toán và logic xử lý ngã rẽ hiểm như: cấp cứu, đòi hỏi làm rõ (clarification) để kháng ảo giác, fallback. | `backend/app/graph/nodes/clarification.py`, `emergency_check.py`, `fallback.py` |
| **Vũ Duy Linh** | Vector Specialist | Thiết lập mô hình Vector Embedding (`keepitreal/vietnamese-sbert`), index toàn bộ Data vào ChromaDB, xây nghiệp vụ kết nối Retrieval Node. | `data_pipeline/vector_indexer.py`, `backend/app/services/retrieval_service.py` |
| **Nguyễn Anh Đức** | Data & SQL Ops | Tiền xử lý Data y tế, nạp vào SQLite, viết Tool Execution để extract chuẩn xác dữ liệu DB vào Context và hỗ trợ tính toán Confidence Score. | `data_pipeline/data_ingestion.py`, `backend/app/database/`, `backend/app/graph/nodes/tool_execution.py`|

## Hướng Dẫn Vận Hành Hệ Thống
Xem chi tiết hướng dẫn tại `README.md` hoặc `PROJECT_DESCRIPTION.md`.
- **Bước 1**: Chạy DB Pipeline nạp liệu vào SQLite và ChromaDB (`data_pipeline/` folder).
- **Bước 2**: Khởi động FastAPI Backend (`cd backend/ && python -m uvicorn app.main:app --reload`).
- **Bước 3**: Khởi động Vue.js Frontend (`cd frontend/ && npm install && npm run dev`).