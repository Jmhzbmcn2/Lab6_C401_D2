# Individual reflection — Vũ Duy Linh (2A202600460)

## 1. Role
Vector Specialist. Phụ trách thiết lập mô hình Vector Embedding (`keepitreal/vietnamese-sbert`), index toàn bộ Data vào ChromaDB, xây nghiệp vụ kết nối Retrieval Node và module tìm kiếm của kiến trúc RAG. File đảm nhận: `data_pipeline/vector_indexer.py`, `backend/app/services/retrieval_service.py`.

## 2. Đóng góp cụ thể
- Cấu hình và thiết lập mô hình Vector Embedding `keepitreal/vietnamese-sbert` tối ưu cho xử lý tiếng Việt y khoa.
- Xây dựng luồng dữ liệu (pipeline), thực hiện index toàn bộ thông tin gói khám, giá dịch vụ của Vinmec vào database ChromaDB.
- Xây dựng nghiệp vụ tìm kiếm trong `retrieval_service.py`, đóng góp thẳng vào công thức tính Confidence Score (`0.5*Vector_similarity + ...`) áp dụng ở bước Re-rank để Quyết định luồng (Clarification/Lookup/Fallback).

## 3. SPEC mạnh/yếu
- Mạnh nhất: Kiến trúc hệ thống — Thiết kế việc tách biệt Vector Search RAG (để tìm Service_ID) và Deterministic Lookup DB (để xuất giá chuẩn) là giải pháp thông minh giải quyết triệt để rủi ro Price Hallucination trong lĩnh vực y tế.
- Yếu nhất: Các con số giả định doanh thu trong ROI (tăng cường 10-20% Booking Conversion Rate) mang tính khá chủ quan. Cần định hướng rõ cấu trúc Funnel để lý giải tại sao User lấy được báo giá lại có khả năng chuyển đổi chốt đơn cao hơn.

## 4. Đóng góp khác
- Tham gia phản biện khi xây dựng các Failure modes, gợi ý trường hợp multi-condition (nhập nhiều triệu chứng) gây loãng Vector Similarity.
- Viết kịch bản test để kiểm thử sự khác biệt giữa các độ dài của Symptom khi được vectorize so với bộ từ điển.

## 5. Điều học được
Trước hackathon, tôi cho rằng hệ thống RAG chỉ bao gồm việc similarity search để lấy context đưa cho LLM. Qua dự án, tôi học được sự phân biệt giữa Semantic Vector Search (mở rộng khả năng map bệnh lý) và Deterministic DB (đảm bảo tính chuẩn xác và y đức). Trong domain rủi ro cao như y tế, kiểm soát LLM không trả lời trực tiếp là bắt buộc (Precision over Recall).

## 6. Nếu làm lại
Nếu có thêm thời gian, tôi sẽ triển khai Hybrid Search thực sự (kết hợp BM25 Keyword Search cùng với Vector Search) để bắt những từ khoá chuyên ngành viết tắt, vì Vector Embeddings hiện tại vẫn thỉnh thoảng bỏ sát các Keyword cứng (Exact Match) quan trọng. Đồng thời dành thời gian tinh chỉnh Chunking rules và overlap tốt hơn.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI (Copilot/Gemini) giúp viết các snippet boilerplate thao tác với cơ sở dữ liệu vector ChromaDB và FastAPI nhanh chóng; đóng vai trò lớn vào việc debug các dimension mismatch của model SBERT.
- **Sai/mislead:** Đôi lúc AI gợi ý việc "sinh" (generate) luôn câu trả lời chứa giá tiền từ Vector Context - điều này đi ngược lại hoàn toàn với chiến lược Architecture (Deterministic Backend) của team, có thể dẫn đến Price Hallucination nguy hiểm. Phải cẩn trọng bám sát thiết kế, không tự ý copy-paste logic sinh chữ của AI vào.