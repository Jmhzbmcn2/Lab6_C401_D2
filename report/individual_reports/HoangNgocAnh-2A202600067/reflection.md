
---

# BÁO CÁO CÁ NHÂN & REFLECTION (HACKATHON DAY 6)

## 1. Thông Tin Cá Nhân
- **Họ và tên:** Hoàng Ngọc Anh
- **Mã số sinh viên:** 2A202600067
- **Nhóm:** Vũ Duy Linh, Đậu Văn Quyền, Hoàng Ngọc Anh, Nguyễn Hoàng Việt, Nguyễn Anh Đức
- **Vai trò trong nhóm:** Logic & Safety Engineer (Triage & Edge Cases)
- **Trách nhiệm chính:** Xây dựng các node kiểm soát an toàn (Emergency Check), xử lý các ngã rẽ khi AI thiếu tự tin (Clarification), thiết kế luồng Fallback và quản lý hệ thống giám sát bước chạy (Debug Trace).

---

## 2. Các Đóng Góp Kỹ Thuật (Technical Contributions)

Trong hệ thống Vinmec AI Triage, em đóng vai trò là người thiết lập các "luật chơi" để đảm bảo AI hoạt động trong hành lang an toàn y tế. Em trực tiếp hiện thực hóa các Node quan trọng trong LangGraph:

### 2.1. Xây dựng Node Kiểm soát Cấp cứu (Emergency Check)
- Em đã lập trình `emergency_check_node` để quét toàn bộ `user_query` dựa trên bộ từ khóa khẩn cấp (`EMERGENCY_KEYWORDS`).
- **Tư duy kỹ thuật:** Em chọn phương án xử lý logic cứng (Deterministic) ngay tại Node đầu tiên. Nếu phát hiện dấu hiệu nguy kịch (khó thở, đau ngực...), hệ thống sẽ ngắt hoàn toàn việc gọi LLM để trả về `EMERGENCY_RESPONSE` (Hotline 115) ngay lập tức. Việc này giúp giảm latency và triệt tiêu rủi ro AI tư vấn sai trong lúc bệnh nhân cần cấp cứu.

### 2.2. Thiết kế Node Clarification & Xử lý độ tự tin (Confidence Logic)
- Em hiện thực hóa `clarification_node` để xử lý các tình huống khi hệ thống có `confidence_score` thấp (dưới ngưỡng an toàn).
- Thay vì để AI "đoán mò", em thiết kế phản hồi yêu cầu người dùng cung cấp thêm thông tin cụ thể (ví dụ: "Siêu âm thai 4D" thay vì "Siêu âm") và tích hợp sẵn `DISCLAIMER_TEXT` để đảm bảo tính pháp lý. Node này giúp hệ thống chuyển từ trạng thái "tự động" sang "hỗ trợ có tương tác", tăng sự tin tưởng của người dùng.

### 2.3. Quản lý Observability thông qua Debug Trace
- Em đã xây dựng cấu trúc `step_trace` trong từng Node để ghi lại: `input`, `output`, và các hành động (`action`) của Agent.
- Việc tích hợp `debug_trace` vào `AgentState` giúp nhóm em có thể quan sát trực quan từng bước rẽ nhánh của AI. Đây là phần đóng góp quan trọng để bạn Việt (Orchestrator) có thể debug luồng Graph và bạn Quyền (Prompt Engineer) biết được cần tối ưu câu chữ ở Node nào.

---

## 3. Tư Duy Sản Phẩm (Product Thinking) & Sự Phối Hợp

- **Tư duy An toàn là trên hết (Safety-First):** Em hiểu rằng trong y tế, một câu trả lời sai còn nguy hiểm hơn việc không trả lời. Do đó, em luôn ưu tiên thiết kế các luồng "Hỏi lại" hoặc "Kết nối nhân viên" (Escalation) như một tính năng bảo vệ người dùng, chứ không phải lỗi hệ thống.
- **Sự phối hợp chặt chẽ:** 
    - Em làm việc với **Đức (Data SQL)** để lấy `confidence_score` làm đầu vào cho việc rẽ nhánh luồng Clarification. 
    - Phối hợp với **Quyền (Prompt)** để chuẩn hóa các câu thông báo lỗi hoặc yêu cầu làm rõ sao cho giữ được giọng điệu chuyên nghiệp của Vinmec.
    - Làm việc với **Việt (Backend)** để thống nhất cấu trúc `AgentState`, đảm bảo dữ liệu log và trace không bị đứt đoạn khi đi qua các node logic phức tạp.

---

## 4. Tự Phản Tĩnh (Self-Reflection)

### 4.1. Điều làm tốt
- Xây dựng được cơ chế bảo vệ đa tầng: từ chặn từ khóa cấp cứu đến việc kiểm soát độ tự tin của phản hồi.
- Code được tổ chức sạch sẽ, có logger và debug trace rõ ràng, giúp việc demo hệ thống trở nên minh bạch và chuyên nghiệp.

### 4.2. Khó khăn gặp phải & Cách vượt qua
- Thách thức lớn nhất là xử lý các câu hỏi "mơ hồ". Ban đầu em định để AI tự giải quyết hết, nhưng sau khi thảo luận với nhóm về rủi ro Legal Risk, em đã quyết định chuyển sang giải pháp Hybrid: Kết hợp giữa gợi ý thông minh và các nút bấm MCQ (Multiple Choice Questions) để ép dữ liệu đầu vào chuẩn xác hơn.

### 4.3. BÀI HỌC ÁP DỤNG THỰC TẾ
Hackathon này dạy cho em rằng việc xây dựng AI cho doanh nghiệp (đặc biệt là y tế) khác xa với việc làm chatbot giải trí. Một hệ thống AI bền vững cần có các "xích sắt" logic bao quanh bộ não LLM. Em nhận ra rằng vai trò của Logic Engineer không phải là làm cho AI thông minh hơn bằng mọi giá, mà là làm cho nó trở nên **đáng tin cậy và có thể dự đoán được (Predictable)**. Việc chuyển hướng sang nhân viên tư vấn đúng lúc chính là đỉnh cao của một trải nghiệm khách hàng tinh tế trong ngành dịch vụ cao cấp như Vinmec.

---
