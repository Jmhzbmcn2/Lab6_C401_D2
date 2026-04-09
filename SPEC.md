# SPEC — AI Product Hackathon

**Nhóm:** Vũ Duy Linh, Đậu Văn Quyền, Hoàng Ngọc Anh, Nguyễn Hoàng Việt, Nguyễn Anh Đức
**Track:** ☐ VinFast · ☑ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☐ Open

**Problem statement (1 câu):** *Người bệnh thiếu chuyên môn y khoa để chọn dịch vụ và gặp khó khi tra cứu bảng giá phức tạp, trong khi tổng đài thường quá tải; AI Chatbot đóng vai trò "Tư vấn viên Y tế ảo" phân tích triệu chứng để trích xuất nhu cầu, lấy thông tin từ Backend (Deterministic) để gợi ý đúng gói khám và báo giá minh bạch 24/7.*

🔥 **Strategic Edge (Why Now? / Lợi thế cạnh tranh):**
*Nhu cầu chăm sóc sức khỏe cá nhân hóa đang tăng vọt. Vinmec sở hữu lợi thế tuyệt đối (Data Advantage) là kho dữ liệu dịch vụ và bảng giá y tế nội bộ khổng lồ. Hiện tại, chưa có đối thủ bệnh viện nào trên thị trường Việt Nam làm tốt AI Triage (Hệ thống định tuyến thông minh). Đây là thời điểm vàng để Vinmec vươn lên dẫn đầu về chuyển đổi số UX người bệnh.*

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | *Bệnh nhân/Người nhà. Pain: Không có chuyên môn chọn dịch vụ; tra giá khó. AI giải quyết: LLM map triệu chứng thành Service_ID, Backend lấy giá từ DB chuẩn xác.* | *AI gợi ý sai chuyên khoa. Hệ thống có Disclaimer rõ ràng và UX có nút "Gọi nhân viên tư vấn" (Escalation là một feature an toàn, không phải failure).* | *Cost bao gồm LLM API + Vector DB Infra + Human QA. Latency < 3s. Risk: Legal (AI bị hiểu là khám bệnh), Giá niêm yết lệch giá trả vì bảo hiểm BHYT.* |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation
Justify: *Augmentation — Trợ năng định tuyến ban đầu. Việc escalate (chuyển máy) sang bác sĩ/nhân viên CSKH là luồng thiết kế chủ đích của y tế để đảm bảo an toàn, AI không độc lập đưa ra quyết định chẩn đoán lâm sàng.*

**Learning signal:**

1. User correction đi vào đâu? *Thông qua Structured Feedback (Nút đánh giá nhanh: Sai khoa? Phức tạp? Sai giá?) và Log ghi nhận. Auto-clustering sẽ nhóm các lỗi mapping triệu chứng.*
2. Product thu signal gì để biết tốt lên hay tệ đi? *Resolution rate (Tỉ lệ giải quyết dứt điểm không cần NV) và Correct Routing Rate (Khách đến khám đúng khoa được gợi ý).*
3. Data thuộc loại nào? ☐ User-specific · ☑ Domain-specific · ☐ Real-time · ☑ Human-judgment · ☐ Khác: *Evaluation Dataset (Golden set).*
   Có marginal value không? (Model đã biết cái này chưa?) *Có. Cần xây dựng Golden Dataset riêng với Vinmec (Test case Input -> Expected Service) để chạy regression test tự động mỗi lần update.*

---

## 2. User Stories — 4 paths

### Feature: *Chatbot Tư vấn Gói khám & Tra cứu giá*

**Trigger:** *Khách hàng nhập triệu chứng hoặc ấn vào các Quick-buttons gợi ý đầu vào.*

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | *Chatbot hiển thị Hybrid UX (Văn bản + Quick action). LLM trích xuất đúng ý, gọi Backend Lookup DB ra chính xác giá gói khám → Trả kết quả mượt mà. User hài lòng.* |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | *Confidence score thấp đo lường qua công thức: `0.5*Vector_Similarity + 0.3*Symptom_Match_Score + 0.2*Intent_Clarity_Score`. Chatbot nhảy vào Clarification step, đặt MCQ hỏi làm rõ hoặc fallback gọi nhân viên.* |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | *AI phân tích triệu chứng A lệch sang khoa B. User tự sửa sai thông qua Structured feedback UI (Bấm "Sai khoa") -> Handoff mượt sang nhân viên gọi lại hỗ trợ.* |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | *Lỗi được Auto-clustering phân tích. Data Engineer bổ sung case này vào Evaluation Dataset (Golden Set) để train lại prompt, đảm bảo "miễn nhiễm" với ca này ở phiên bản sau.* |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall
Tại sao? *Domain y tế kiêng kị việc gợi ý lan man (Recall) gây nhiễu thông tin. Cần định tuyến chính xác (Precision) thay vì nhắm mắt đoán bừa gây hậu quả Legal Risk.*

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| *Resolution Rate (Tỷ lệ tự giải quyết)* | *Target: 50% - 60% (Safe-first)* | *< 40% (Quá tệ) hoặc > 75% (Có dấu hiệu Over-trust AI, rất thiếu an toàn y tế)* |
| *Correct Routing (Định tuyến đúng khoa)* | *≥ 85%* | *< 70% trong vòng 3 ngày* |
| *User CSAT (Độ hài lòng UX/CX)* | *≥ 4.0/5.0* | *< 3.0* |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | *Legal Risk: Hệ thống diễn đạt giống như chẩn đoán thay vì gợi ý.* | *Bệnh nhân tin sái cổ, tự đi mua thuốc hoặc bắt đền bệnh viện nếu bệnh nặng thêm.* | *Phrasing control: Prompt chặt chẽ bắt buộc dùng cụm từ "Thông tin tham khảo", "Gợi ý". Luôn kèm Disclaimer to rõ.* |
| 2 | *Multi-condition: Nhập "Đau mắt", "Tức ngực", "Mỏi khớp" cùng lúc.* | *Confidence score tổng hợp bị loãng, AI không biết map vào `Service_ID` của khoa nào.* | *Tách Intent: Phát hiện >2 intent xa nhau -> Mở Clarification step yêu cầu chọn triệu chứng ưu tiên hoặc Gọi NV.* |
| 3 | *Emergency Risk: Nhập mô tả khẩn cấp (khó thở, chảy máu não).* | *Hệ thống tốn thời gian parse dữ liệu, bỏ lỡ thời gian vàng sơ cứu tính mạng người bệnh.* | *Thiết lập kiến trúc chạy song song Async: Một Lightweight Classifier liên tục nghe lén + Hybrid Keyword fallback. Phát hiện cấp cứu -> Cướp luồng đẩy ngay Hotline 115 không trễ (latency < 100ms).* |

---

## 5. ROI 3 kịch bản & Business Impact

|   | Conservative (Base) | Realistic | Optimistic (Best) |
|---|-------------|-----------|------------|
| **Assumption** | *Chatbot xử lý an toàn 40%, 60% handoff sang NS.* | *Chatbot đạt độ chín Resolution Rate ~ 60%.* | *Người dùng quen thuộc Hybrid UX, hệ thống định tuyến mượt 75% flow.* |
| **Cost** | *$30/ngày (LLM: 10 + Infra: 10 + QA: 10)* | *$40/ngày* | *$75/ngày cao điểm* |
| **Cost Saving Benefit** | *Giảm thời gian xử lý thủ công 5 phút/ticket.* | *Giảm 2 FTEs chăm sóc khách hàng trực chat vòng ngoài ban đêm.* | *Tự động hóa hoàn toàn quy trình phân luồng khám, cắt OT toàn diện.* |
| **Revenue Impact (Đích đến)** | *Bảo vệ thương hiệu, tránh mất khách do bỏ lỡ tin nhắn.* | *Tăng 10% Booking Conversion Rate -> Booking Uplift mang lại doanh thu tăng thêm ~5 tỷ VNĐ/năm.* | *Tăng mức chuyển đổi lên 20% do được cung cấp giá minh bạch -> Đột phá doanh thu nội trú.* |

**Kill criteria:** *User đánh giá CSAT < 3.0 và tỷ lệ người dùng phải escalate duy trì > 80% (Hệ thống không chạy đúng thiết kế phân luồng).*

---

## 6. Mini AI spec (1 trang)

**Vinmec AI Symptom Triage** là giải pháp định tuyến thông minh hoạt động theo cơ chế **Augmentation (Trợ năng)**. Người dùng không còn bị "ngợp" trước danh sách ma trận dịch vụ của bệnh viện thông qua thiết kế giao diện **Hybrid UX (Nhập văn bản + Quick buttons lựa chọn)**.

Về **Kiến trúc hệ thống (System Architecture)**, quy trình (Flow) chạy tuyệt đối theo khung RAG mở rộng để đảm bảo tính an toàn y khoa (Zero Price Hallucination): 
Mô tả người dùng ➡️ `LLM Intent Extraction Classifier` ➡️ Trích xuất `Structured Query`. 
Tiếp đó, `Vector Search RAG` tìm kiếm thông tin chuyên khoa tương ứng, trải qua bước `Re-rank` và tính toán `Confidence Scoring Engineer-ready` (Công thức: 0.5 * Vector_similarity + 0.3 * Symptom_match_score + 0.2 * Intent_clarity_score). Tùy vào độ tự tin mà AI quyết định hỏi làm rõ (Clarification) hoặc tiến tục đi qua `Deterministic Lookup Backend DB` để trích xuất Data Schema chuẩn đã được định trước:
```json
{
  "service_id": "OB_POSTPARTUM_01",
  "department": "Sản Phụ Khoa",
  "symptoms": ["sau sinh", "vết mổ", "rỉ dịch"],
  "price_range": [500000, 1200000],
  "insurance_applicable": true
}
```
Nhờ cơ sở dữ liệu cứng này, **Quality (Chất lượng)** mảng báo giá là 100% chuẩn yết trên viện. Về phần nhận diện intent, chúng tôi hướng đến **Precision > Recall**, kết hợp cơ chế kiểm soát rủi ro **Phrasing Control** (cảnh báo nguy hiểm) và một **Lightweight LLM Classifier chạy Async song song** chỉ trực chờ phát hiện khẩn cấp để bắn Hotline 115. 

Việc chuyển máy (Escalate CSKH) là **tính năng (Feature), không phải lỗi**, qua đó tạo đòn bẩy cho lõi **Learning Pipeline vòng lặp**: Thu thập "Structured Feedback" ➡️ Clustering các triệu chứng bị gọi sai khoa ➡️ Cập nhật "Golden Dataset" ➡️ Automated Evaluation. Qua thời gian, Data Flywheel tự hoàn thiện kho từ điển tiếng lóng y khoa dành riêng cho Vinmec.

🎬 **Demo Scenario (Kịch bản thực tế)**
- **User:** *"Tôi đẻ mổ được 6 tuần, vết mổ đang hơi rỉ dịch vàng và đau"* (Intent: Khám hậu sản - có triệu chứng).
- **Bot:** Hệ thống tiếp nhận, Intent extraction nhận dạng "Phụ sản", Symptom matching phân tích từ khóa "rỉ dịch". Chạy song song Classifier khẩn cấp (Không tìm thấy cảnh báo nguy kịch). Lookup Service DB.
- **Bot:** *"Chào chị, với tình trạng vết mổ rỉ dịch, chị nên thăm khám chuyên khoa Sản gấ. Đây là thông tin tham khảo: **Khám vết thương hậu sản (Mã: OB_POSTPARTUM_01)**. Khoảng giá: 500k - 1tr2.*
*(Phía dưới tự động hiện sẵn tùy chọn: Nút [Đặt khám ngay] | Nút [Gọi NV hỗ trợ BHYT])*