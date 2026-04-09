# BÁO CÁO CÁ NHÂN & REFLECTION (HACKATHON DAY 6)

## 1. Thông Tin Cá Nhân
- **Họ và tên:** Nguyễn Anh Đức
- **Mã số sinh viên:** 2A202600387
- **Nhóm:** Vũ Duy Linh, Đậu Văn Quyền, Hoàng Ngọc Anh, Nguyễn Hoàng Việt, Nguyễn Anh Đức
- **Vai trò trong nhóm:** Data & SQL Ops
- **Trách nhiệm chính:** Tiền xử lý Data y tế, nạp vào SQLite, viết Tool Execution để load chuẩn xác dữ liệu DB vào Context và cấu trúc thuật toán Confidence Score.

---

## 2. Các Đóng Góp Kỹ Thuật (Technical Contributions)

Trong luồng Agentic Workflow của hệ thống AI Triage (Vinmec), tôi chịu trách nhiệm chính ở khâu đảm bảo dữ liệu đầu ra "Zero Price Hallucination" tức là chống ảo giác hoàn toàn tuyệt đối về giá cả và thông tin chuyên khoa. Cụ thể tôi đã phụ trách các khối công việc sau:

### 2.1. Thiết kế và nạp dữ liệu (Data Ingestion) vào SQLite
- Nắm giữ toàn bộ dữ liệu bảng giá chuẩn yết y tế đa bộ môn của các cơ sở Vinmec.
- Build kiến trúc Relational Database (bảng `services`). Lưu trữ đầy đủ định danh (ID), Chi nhánh trực thuộc (Times City / Smart City), Nhóm dịch vụ và Giá. Dữ liệu này đóng vai trò như "Ground Truth" (Chân lý) không thể sai lệch ở tầng Backend.

### 2.2. Viết Core SQL & Hàm Tool Execution
- Tôi lập trình thư viện truy vấn `backend/app/database/sqlite_db.py`, cung cấp 3 bộ luồng tra cứu SQL logic khắt khe xử lý dựa trên Intent (Phân tích từ LLM):
  1. **Flow mặc định (`query_services_by_ids`)**: Hứng danh sách ID từ lưới Vector ChromaDB và ép logic bộ lọc cứng băng lệnh SQL `AND branch = '...'` vào WHERE clause. Nhờ thế, nếu LLM nhận diện được intent chi nhánh (Time City vs Smart City), tôi sẽ chặn hoàn toàn việc nhầm lẫn giá giữa 2 cơ sở.
  2. **Flow Fallback Dự phòng (`fallback_fuzzy_search`)**: Nếu luồng chạy qua Vector DB tìm không ra kết quả (hoặc distance quá thấp làm đứt gãy luồng), Tool Execution sẽ tự động bật chế độ truy xuất SQL thuần `LIKE` theo các keywords tách nhỏ để cứu cánh.
  3. **Flow So Sánh Giá (`compare_services_across_branches`)**: Thiết kế kỹ thuật dùng `ORDER BY service_name_vn, branch` cho phép lấy ra song song 2 mảng thông tin ở 2 chi nhánh khác nhau. Điều này giúp bước LLM Synthesis tạo HTML Bảng (Table UI) cho khách hàng so sánh một cách logic, dễ hiểu.

### 2.3. Tích hợp Tool Execution vào LangGraph
- Đưa logic SQL thành các tool gọi được ở node `tool_execution_node` (`backend/app/graph/nodes.py`). 
- Hỗ trợ xây dựng công thức toán học đo độ tin cậy kết hợp (Confidence Score):
  `0.5 * Vector_Similarity + 0.3 * Symptom_Match_Score + 0.2 * Intent_Clarity_Score`
  Thao tác này đóng vai trò quyết định, nếu điểm cực thấp sẽ chốt lật luồng qua node `Clarification` (Xác thực lại, chống ảo giác) thay vì ráng trả lời láo rồi gây rủi ro Legal Risk cho bệnh viện.

---

## 3. Tư Duy Sản Phẩm (Product Thinking) & Sự Phối Hợp

- **Tư duy Deterministic:** Nhận thức rõ bản chất y tế cần tính an toàn (Safety-First), tôi hiểu rằng mô hình AI (Probalistic) không được quyền báo giá. Do đó, vai trò SQL Ops của tôi chặn lại bước đó. AI chỉ việc lấy ID và Intent, tôi sẽ truy vấn Data cứng -> Việc trả lời là hoàn toàn Deterministic (Tin cậy 100%).
- **Sự phối hợp mượt mà:** Khối công việc của tôi nằm giữa "Vector Specialist" (người lấy ID tài liệu) và "Prompt Engineer" (người viết text báo cáo cho khách). Tôi đã chuẩn hóa dữ liệu List of Dictionaries `[{"branch": "...", "service_name_vn": "...", "price": "..."}]` sang cấu trúc Markdown thuần túy để người thứ 2 dễ dàng bỏ vào biến Prompt. Tôi cũng test cẩn thận các edge cases khi SQL tìm được 0 record với bạn làm ngã rẽ hiểm (Triage & Edge Cases).

---

## 4. Tự Phản Tĩnh (Self-Reflection)

### 4.1. Điều làm tốt
- Phát huy tốt tư duy Data Pipeline. Mọi dòng dữ liệu nạp vào DB và trích xuất qua Tool đều đảm bảo tính sạch (Clean).
- Thiết kế ra các flow Fallback bảo toàn luồng (Graceful Degradation): khi tool không hứng được mảng ID từ Chroma thì DB vẫn tự bớt thông minh, chạy SQL text search để bám luồng.
- Hỗ trợ tạo nền tảng vững chắc để LangGraph hoạt động hiệu quả.

### 4.2. Khó khăn gặp phải & Cách vượt qua
- Thách thức lớn nhất là làm thế nào để đồng bộ giữa vector search (trả về JSON) và relaltional search (trả về Database Row objects) và trộn sao cho logic không bị gãy khi filter branch.
- Cách xử lý: Góp phần tạo ra Pipeline `ID-Based Hybrid Search` (Vector chỉ lo lấy ID, SQL cầm ID cộng với quy tắc Filter chọc thẳng vào SQLite lấy dữ liệu cuối). Điều này giúp code tách bạch.

### 4.3. BÀI HỌC ÁP DỤNG THỰC TẾ
Hackathon mang lại cho tôi góc nhìn cực kỳ "thực chiến". Tôi nhận ra một hệ thống AI giỏi không phải là một hệ thống 100% vứt hết mọi thứ cho gpt-4 sinh chữ. Giá trị nằm ở cách ứng dụng **Tool Calling**, sử dụng LLM như bộ não "Đọc (Routing)" và đưa tay ra lệnh cho Core Code (Python/SQL) xử lý những số liệu đòi tính minh bạch. Trong y tế, "Augmentation" (Hỗ trợ) và "Escalation" (Chuyển tiếp cho người) không phải là dấu hiệu của việc thất bại kỹ thuật, mà đó là hành vi quản trị rủi ro đúng đắn.
