# Prototype — AI triage Vinmec

## Mô tả
Hệ thống chatbot giúp tư vấn tự động cho bệnh nhân Vinmec về giá các dịch vụ y tế và hỗ trợ định tuyến (triage). Được thiết kế theo tư duy Agentic Workflow, chatbot có khả năng kiểm soát tình huống khẩn cấp, chủ động hỏi làm rõ (Clarification) khi độ tự tin thấp để chống ảo giác (Hallucination) và hỗ trợ so sánh giá khám liên viện với dữ liệu cứng đáng tin cậy.

## Level: C. Working code (Agent end-to-end)
- Backend API build bằng FastAPI phối hợp luồng StateGraph phân mảnh của LangGraph.
- Cơ sở dữ liệu: Nối ghép giữa Data Relational (SQLite) với Vector DB (ChromaDB).
- Frontend Web UI xây dựng bằng Vue.js 3 + Vite render Markdown xịn xò.
- Luồng Agent tự động End-to-end thực tế theo kịch bản: Kiểm tra khẩn cấp → Bóc tách Intent → Nhúng Vector/SQL → Trả lời/Làm rõ.

## Links
- Mã nguồn Code: https://github.com/Jmhzbmcn2/Lab6_C401_D2 (Nhánh main)
- Hướng dẫn vận hành: xem `PROJECT_DESCRIPTION.md` / `README.md`
- Luồng thuật toán AI: xem `chatbot_flow.md`

## Tools
- Khung sườn: FastAPI (Backend), LangGraph V2, Vue.js 3 + Vite (Frontend)
- Database: ChromaDB (Vector Semantic) + SQLite (Deterministic Lookup)
- AI Core: Google Gemini 2.5 Flash-lite (via API SDK)
- Khác: Mô hình Embedding `keepitreal/vietnamese-sbert`

## Phân công
| Thành viên | Phần | Mảng Code đảm nhận |
|-----------|------|--------------------|
| Nguyễn Hoàng Việt | Graph Orchestrator (Xây trúc StateGraph) | `backend/app/graph/builder.py`, `edges.py`, `state.py`, `main.py` |
| Đậu Văn Quyền | Prompt Engineer (Tone y tế, tách JSON) | Toàn bộ `backend/app/prompts/` |
| Hoàng Ngọc Anh | Triage & Edge Cases (Cấp cứu, Clarification) | `backend/app/graph/nodes/clarification.py`, `emergency_check.py`, `fallback.py` |
| Vũ Duy Linh | Vector Specialist (Index ChromaDB, Embedding) | `data_pipeline/vector_indexer.py`, `backend/app/services/retrieval_service.py` |
| Nguyễn Anh Đức | Data & SQL Ops (Chiết xuất JSON SQLite Tool) | `data_pipeline/data_ingestion.py`, `backend/app/database/`, `backend/app/graph/nodes/tool_execution.py`|