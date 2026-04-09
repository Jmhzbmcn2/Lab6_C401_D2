# Vinmec AI Chatbot Flow (Kiến trúc LangGraph V2)

Dựa trên việc cập nhật mã nguồn theo chuẩn **Clean Architecture** tại thư mục `backend/app/graph/`, luồng hoạt động (flow) thực tế của hệ thống đã được thiết kế tinh vi hơn và hoạt động đúng chuẩn một trợ lý Triage (Sàng lọc y tế) với các thao tác như Phân loại khẩn cấp, So sánh giá, và Đặt câu hỏi làm rõ.

```mermaid
graph TD
    %% Khởi tạo
    START((Bắt đầu)) --> EMR[Emergency Check Node]

    %% 1. Khẩn cấp
    EMR -->|Kiểm tra từ khóa khẩn cấp| CondEmr{Là cấp cứu?}
    CondEmr -->|Có| END((Kết thúc))
    CondEmr -->|Không| QU[Query Understanding Node]

    %% 2. Hiểu mục đích (Intent Parsing)
    QU -->|LLM Structured JSON<br/>Trích xuất: action_type, normalized_query, branch| CondAction{Loại hành động<br/>action_type?}
    
    CondAction -->|compare_price| COMP[Compare Price Node]
    COMP -->|Lập bảng so sánh đa chi nhánh| END

    CondAction -->|triage / general| RET[Retrieval Node]

    %% 3. Tìm kiếm Semantic
    RET -->|Vector Search qua ChromaDB| CondRet{Có ID dịch vụ?}
    CondRet -->|Thất bại| FB[Fallback Node]
    CondRet -->|Thành công| TOOL[Tool Execution Node]

    %% 4. Trích xuất DB & Chấm điểm Tự tin
    TOOL --> Filter[Tra cứu Database SQLite chính thức<br/>Bật tự động Keyword Fuzzy Search nếu cần]
    Filter --> Eval[Chấm điểm Confidence Score<br/>Vector Similarity + Mật độ kết quả + Rõ ràng chi nhánh]
    
    Eval --> CondTool{Đánh giá kết quả}
    
    CondTool -->|Không có kết quả DB| FB
    CondTool -->|Có kết quả NHƯNG rủi ro sai sót cao<br/>Confidence < 25%| CLAR[Clarification Node]
    CondTool -->|Kết quả chuẩn xác & Tự tin tốt| SYN[LLM Synthesis Node]

    %% 5. Terminal (Các ngã rẽ cuối)
    CLAR -->|Yêu cầu người dùng diễn đạt thêm| END
    SYN -->|LLM viết văn bản chốt giá (Markdown)| END
    FB -->|Câu trả lời đệm (xin lỗi mặc định)| END
```

## Các Bước Tiến Lớn Ở Bản V2:
1. **Có Luồng Khẩn Cấp Chặn Đầu (`emergeny_check`):** Nếu khách gõ các câu từ "chảy máu", "cấp cứu", luồng đi thẳng vào **END** với số 115 mà không mất tiền chạy LLM phân tích nhảm.
2. **Khả Năng So Sánh Chủ Động (`compare_price`):** Người dùng yêu cầu so sánh giá lập tức rẽ nhánh qua Node lập bảng đa chi nhánh.
3. **Cơ Chế Kháng Ảo Giác (`clarification`):** Tool Execution được bổ sung bộ quy tắc chấm điểm `confidence_score`. Nếu dưới mức ranh giới 25%, AI sẽ chủ động rẽ sang nhánh `Clarification` nhún nhường hỏi thêm thông tin (VD: "bạn muốn siêu âm thái 4D hay 2D") thay vì trả lời bừa gây ảnh hưởng thương hiệu y tế. 
4. **Clean Architecture Isolation:** Thay vì cuộn một cục lớn thì biểu đồ đồ thị (`builder.py`) được map 1-1 với từng file thực thể trong `nodes/` riêng lẻ, giúp tách rời các lớp giao tiếp Service và Database.
