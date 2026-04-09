# Individual reflection — Nguyễn Anh Đức (2A202600387)

## 1. Role
Data & SQL Ops. Tiền xử lý Data y tế, nạp vào SQLite, viết Tool Execution để extract chuẩn xác dữ liệu DB vào Context và hỗ trợ tính toán Confidence Score.

## 2. Đóng góp cụ thể
- Thiết kế Data Ingestion pipeline nạp dữ liệu bảng giá chuẩn y tế của Vinmec (Times City/Smart City) vào Relational Database (SQLite bảng `services`).
- Viết 3 bộ Tool Execution (truy vấn SQL) gồm: Flow mặc định lọc `branch` trực tiếp chặn ảo giác giá, Flow Fallback (Fuzzy Search bằng `LIKE`) cứu luồng khi Vector DB thất bại, và Flow So sánh giá (`ORDER BY branch`).
- Hỗ trợ xây dựng thuật toán đo lường Confidence Score dựa trên 3 trọng số: Vector Similarity (0.5), Symptom Match (0.3), và Intent Clarity (0.2) làm mốc cho LangGraph định tuyến.

## 3. SPEC mạnh/yếu
- Mạnh nhất: phần Failure Modes. Cả nhóm đã liệt kê được case "Legal Risk" (Bệnh nhân hiểu lầm AI đang chẩn đoán bệnh) và thiết lập cơ chế Mitigation cực kỳ thực tế qua Phrasing Control. Tránh được rủi ro pháp lý.
- Yếu nhất: Cost / Latency (Tính khả thi). Chưa đo lường cụ thể được chi phí Infra lưu trữ Vector DB khi scale lên lượng dữ liệu toàn bộ gói khám bệnh khổng lồ. Assumption trong bảng ROI vẫn còn khá chủ quan.

## 4. Đóng góp khác
- Tham gia debug luồng LangGraph ở phần `tool_execution_node`, đảm bảo khi Vector tìm kiếm không trả về kết quả hợp lệ (`distance > 0.6`), hệ thống không "sập" mà mượt mà chuyển sang truy xuất DB thuần (Graceful Degradation).
- Đóng góp bộ tài liệu Bonus ở thư mục `extras` (Nhật ký nghiên cứu bảo mật SQL, log test mô phỏng Vector vs Fuzzy, và thiết kế toán học Confidence Score) để giám khảo có cái nhìn sâu hơn về System Thinking của nhóm.

## 5. Điều học được
Trước hackathon, tôi thường quen với việc giao toàn bộ dữ liệu vào tay LLM (dạng ReAct agent) phó mặc cho nó.
Nhưng sau khi build một Medical AI Triage, tôi nhận ra: LLM chỉ nên đóng vai trò là "Bộ não nội suy ý định (Intent)". Mọi truy xuất liên quan đến Tiền Bạc & Quy trình y tế phải được kéo qua Tool Execution bằng "Hard query" (như câu lệnh SQL lọc chuẩn Branch của tôi). Chắn lỗi bằng Prompt là rủi ro, nhưng chặn ngay bằng Logic SQL Database ở Backend là Safety-First tuyệt đối (Deterministic). Thêm nữa, tính năng Escalation (Bấm gọi nhân viên y tế thật) là luồng thiết kế hoàn hảo chứ không phải là AI thất bại.

## 6. Nếu làm lại
Sẽ đầu tư tích hợp Database nhạy bén hơn. Thay vì chạy Vector lấy ID xong mới đập vào SQL truy xuất, tôi sẽ tìm tòi xây dựng một kiến trúc "Hybrid Search Engine" xịn xò hơn, để SQL filter được ưu tiên dập xuống từ đầu nhằm tăng tốc tối đa Latency.

## 7. AI giúp gì / AI sai gì
- **Giúp:** dùng Claude 3.5 Sonnet để thiết kế bảng Data Schema chuẩn logic y tế và code thuật toán sinh chuỗi Fuzzy Match SQL linh động theo từ khóa Python rất nhanh. Dùng Gemini để review hệ số toán học cho điểm tự tin.
- **Sai/mislead:** ChatGPT ban đầu cứ khăng khăng "xúi" nhồi toàn bộ thông tin về rổ rá giá cả vào Vector DB (Chroma) chung với text. Khi đưa vào chạy, mô hình nhúng tiếng Việt bắt khoảng cách sai bét nên lấy giá chi nhánh nọ lộn sang chi nhánh kia. Suýt thì gây Price Hallucination do tôi quá tin tool. Bài học: RAG (Vector) sinh ra là để tìm Semantic, muốn filter Exact Match (chuẩn giá, chuẩn cơ sở) thì phải nhường "sân khấu" cho Relational Database (SQL).
