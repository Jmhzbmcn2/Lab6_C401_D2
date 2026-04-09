# THIẾT KẾ TOÁN HỌC CHO ĐIỂM SỐ TỰ TIN (CONFIDENCE SCORE)

Trong quá trình thi công luồng Triage (phân loại) của Hackathon Day 6. Tôi (Vai trò Data & SQL Ops) đã phối hợp với các thành viên làm Mảng LangGraph để lên công thức đánh giá độ tin cậy của bộ dữ liệu Database.

Kết quả trả về không được mù quáng đẩy thẳng cho LLM mà phải lượng hóa xem: Bot tự tin bao nhiêu %. Dưới bảng thiết kế mà tôi đã đề xuất code cho hàm `tool_execution_node`:

## Công thức chung:
`Score = (0.5 * Vector_Similarity) + (0.3 * Symptom_Match_Score) + (0.2 * Intent_Clarity_Score)`

### Giải nghĩa các tham số:
**1. Vector_Similarity (Trọng số 0.5 - Yếu tố quyết định nhất)**
- Chroma DB sử dụng `l2` distance (0 -> 2).
- Vector Similarity được tôi quy đổi bằng `max(0, 1 - Khoảng cách L2 trung bình)`.
- Khoảng cách càng về 0, độ tiệm cận hình thái ngôn ngữ càng tuyệt đối.

**2. Symptom_Match_Score (Trọng số 0.3)**
- Đếm số lượng kết quả nằm trong "Vùng an toàn kỹ thuật" (khoảng cách `< 0.4`).
- Tỷ lệ này là số kết quả cực chắc chắn / Tổng dòng tài liệu lôi ra.
- Ví dụ lấy 5 dòng mà cả 5 dòng đều có khoảng cách `< 0.4` thì hệ số này đạt mức 1.0 tối đa. Mật độ kết quả chuẩn càng nhiều, tỷ lệ chống nhiễu càng cao.

**3. Intent_Clarity_Score (Trọng số 0.2)**
- Độ trong sáng của ý định (Nhờ LLM trích xuất đầu vào).
- Nếu khách nói rõ: "Cho anh xin giá ở **Times City**" -> Có Intent `branch_filter = 'Times City'` -> Điểm = 1.0 (Bởi vì truy xuất được 100% bằng câu lệnh SQL màng lọc cứng).
- Nếu khách lửng lơ: "Cho xin giá đẻ" -> Không rõ chi nhánh -> Rủi ro trả báo sai cao -> Điểm = 0.5.

## Quyết định hành động trên đồ thị mạng (LangGraph Route):
Nhờ bộ công thức này, Graph có khả năng:
- Nếu Score `< 0.25`: Không trả lời, điều chuyển cưỡng bức vào Router Gọi 115 hoặc Trả lời Fallback.
- Nếu `0.25 < Score < 0.45`: Chuyển sang Node **Clarification**. Yêu cầu người dùng (VD: "Bác muốn hỏi ở chi nhánh nào?").
- Nếu `Score >= 0.45`: Cho qua, bơm thẳng dữ liệu nhúng Tool Execution vào LLM sinh câu tư vấn thuần.
