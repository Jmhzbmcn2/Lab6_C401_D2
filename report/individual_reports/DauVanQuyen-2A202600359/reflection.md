# BÁO CÁO CÁ NHÂN & REFLECTION (HACKATHON DAY 6)

## 1. Thông Tin Cá Nhân
- **Họ và tên:** Đậu Văn Quyền
- **Mã số sinh viên:** 2A202600359
- **Nhóm:** Vũ Duy Linh, Đậu Văn Quyền, Hoàng Ngọc Anh, Nguyễn Hoàng Việt, Nguyễn Anh Đức
- **Vai trò trong nhóm:** Prompt Engineer
- **Trách nhiệm chính:** Xây dựng và tối ưu hóa hệ thống Prompt (System Instruction) cho các Node trong LangGraph; Huấn luyện LLM khả năng đọc hiểu triệu chứng và điều hướng dịch vụ y tế chính xác; Đảm bảo văn phong chuyên nghiệp và chống ảo giác (Hallucination).

---

## 2. Các Đóng Góp Kỹ Thuật (Technical Contributions)

Trong luồng Agentic Workflow của hệ thống AI Triage (Vinmec), tôi chịu trách nhiệm chính ở khâu "Bộ não định hướng" – tức là biến LLM từ một chatbot thông thường thành một chuyên gia y tế thấu cảm và chính xác. Cụ thể:

### 2.1. Thiết kế và Tối ưu hóa System Prompts (`backend/app/prompts/`)
- Mài dũa các Prompt cốt lõi: `QUERY_UNDERSTANDING_PROMPT`, `SYNTHESIS_PROMPT` và `COMPARE_PRICE_PROMPT`.
- Áp dụng kỹ thuật **Few-shot Prompting** và **Chain-of-Thought** để ép LLM phải suy luận logic trước khi đưa ra kết luận về khoa phòng hoặc giá cả.
- Rèn luyện khả năng đọc/viết tiếng Việt chuyên ngành y tế cho model, giúp câu trả lời không bị "nói nhảm" hoặc sử dụng từ ngữ thiếu tự nhiên, đảm bảo đúng tinh thần phục vụ tận tâm của Vinmec.

### 2.2. Xây dựng Logic Tư vấn Triệu chứng & Gợi ý Dịch vụ
- Thay vì chỉ là một bộ máy tra cứu giá khô khan, tôi đã nâng cấp Prompt để chatbot có khả năng:
    - **Phân tích triệu chứng:** Đọc các mô tả của người dùng (ví dụ: "đau bụng âm ỉ vùng thượng vị", "ho có đờm") để đánh giá sơ bộ nhu cầu.
    - **Gợi ý dịch vụ hợp lý:** Tự động map từ triệu chứng sang các gói khám/dịch vụ liên quan trong Database (ví dụ: gợi ý "Nội soi dạ dày" khi khách nói đau bụng kèm ợ chua).
    - **Cá nhân hóa tư vấn:** Đặt câu hỏi ngược lại để làm rõ tình trạng khách hàng trước khi đưa ra gợi ý cuối cùng.

### 2.3. Kiểm soát Hallucination & Triage Logic
- Thiết lập các "vùng an toàn" (Guardrails) trong prompt: Tuyệt đối không được phép bịa đặt giá tiền nếu database không trả về kết quả. 
- Xây dựng cơ chế **Emergency Detection**: Đưa danh sách từ khóa cấp cứu vào prompt hệ thống để ngay lập tức chuyển hướng khách hàng sang gọi Hotline cấp cứu 115 khi phát hiện dấu hiệu nguy kịch, đảm bảo an toàn tính mạng là ưu tiên số 1.
- Phối hợp với team backend để chuẩn hóa format Output (Markdown Table) sao cho model luôn render ra giao diện dễ đọc nhất trên Mobile/Web.

---

## 3. Tư Duy Sản Phẩm (Product Thinking) & Sự Phối Hợp

- **Tư duy Thấu cảm (Empathy):** Người đi tìm dịch vụ y tế thường đang lo lắng. Tôi thiết kế Prompt để LLM luôn có câu chào/câu dẫn cảm thông (Empathy statement) trước khi đưa ra những con số khô khan.
- **Tăng giá trị chuyển đổi:** Bằng cách gợi ý đúng dịch vụ dựa trên triệu chứng, tôi đã biến chatbot từ một công cụ tra cứu bị động thành một người tư vấn chủ động, giúp khách hàng tiết kiệm thời gian chọn khoa phòng và tăng hiệu quả vận hành cho bệnh viện.
- **Sự phối hợp:** Tôi làm việc chặt chẽ với bạn làm Data/SQL để hiểu cấu trúc dữ liệu trả về, từ đó viết Prompt "hứng" dữ liệu đó vào Context một cách mượt mà, giúp LLM không bị nhầm lẫn giữa giá của các chi nhánh.

---

## 4. Tự Phản Tĩnh (Self-Reflection)

### 4.1. Điều làm tốt
- Tối ưu hóa được khả năng ngôn ngữ của model, giúp chatbot giao tiếp như một nhân viên tư vấn thực thụ của Vinmec.
- Thành công trong việc tích hợp khả năng "Tư vấn dựa trên nhu cầu/triệu chứng" vào luồng tra cứu giá truyền thống.
- Xử lý tốt các tình huống Edge Case (khi khách hỏi lan man hoặc thông tin thiếu).

### 4.2. Khó khăn gặp phải & Cách vượt qua
- **Khó khăn:** Model đôi khi vẫn gợi ý thừa một số dịch vụ không đúng trọng tâm khi người dùng mô tả triệu chứng quá mơ hồ hoặc chung chung (ví dụ: chỉ nói "thấy hơi mệt").
- **Cách xử lý:** Tôi đã tinh chỉnh lại Prompt để yêu cầu LLM phải "thẩm định" độ liên quan trước khi liệt kê dịch vụ. Nếu thông tin khách hàng đưa ra quá ít, AI sẽ chủ động đặt câu hỏi gợi mở để làm rõ tình trạng bệnh thay vì ráng đưa ra một danh sách dài các dịch vụ không sát thực tế.

### 4.3. BÀI HỌC ÁP DỤNG THỰC TẾ
Qua Hackathon, tôi nhận ra Prompt Engineering không chỉ là "viết vài câu lệnh". Đó là nghệ thuật truyền tải logic kinh doanh (Business Logic) và giá trị thương hiệu (Brand Value) vào một hệ thống Probabilistic. Trải nghiệm này dạy tôi cách định hướng AI để nó thực sự tạo ra giá trị thực tế cho doanh nghiệp (tăng tỉ lệ tư vấn thành công) thay vì chỉ là một món đồ chơi công nghệ.

