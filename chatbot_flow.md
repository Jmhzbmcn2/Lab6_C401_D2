# Vinmec AI Chatbot Flow (Dựa trên Code thực tế)

Dựa trên việc đọc mã nguồn trong thư mục `backend/app/graph` (`builder.py`, `nodes.py`), luồng hoạt động (flow) **thực tế hiện tại** của hệ thống được lập trình bằng LangGraph như sau:

```mermaid
graph TD
    %% Khởi tạo
    START((Bắt đầu)) --> QU[Query Understanding Node]

    %% 1. Query Understanding
    QU -->|Sử dụng LLM Structured Output<br/>Trích xuất: normalized_query & intent_branch| RET[Retrieval Node]

    %% 2. Retrieval (Semantic Search)
    RET -->|Vector Search trong ChromaDB<br/>Tìm top 10 services| CondRet{Tìm thấy<br/>kết quả Chroma?}

    %% Rẽ nhánh từ Retrieval
    CondRet -->|Có| TOOL[Tool Execution Node]
    CondRet -->|Không| FB[Fallback Node]

    %% 3. Tool Execution & Data Lookup
    TOOL --> Filter[Lọc Chroma results<br/>giữ lại distance < 0.6]
    Filter --> SQLiteExact[Tra cứu thông tin chính xác<br/>bằng IDs trên bảng SQLite]
    
    SQLiteExact --> CheckSQLite{Có kết quả nào?}
    CheckSQLite -.->|Không có hoặc bị lọc hết| SQLiteFuzzy[Kích hoạt SQLite Fuzzy Fallback<br/>Bằng normalized_query]
    
    CheckSQLite -->|Có| CondTool
    SQLiteFuzzy -.-> CondTool{Chốt lại có<br/>tool_results > 0 ?}

    %% Rẽ nhánh từ Tool Execution
    CondTool -->|Có kết quả| SYN[LLM Synthesis Node]
    CondTool -->|Hoàn toàn trống| FB

    %% 4. Synthesis
    SYN -->|Đưa dữ liệu giá vào Context<br/>LLM sinh câu trả lời Markdown| END((Kết thúc))

    %% Fallback Node
    FB -->|Trả lời tĩnh ngầm định:<br/>'Không tìm thấy dịch vụ...'| END
```

## Nhận xét độ chênh lệch so với bản thiết kế (SPEC.md):
1. **Không có luồng Async cho Khẩn cấp:** Codebase hiện tại chưa có "nghe lén khẩn cấp" để đưa ra số 115. Chỉ là một pipeline tuần tự duy nhất.
2. **Không có bước "Clarification" (hỏi lại):** Đồ thị thay vì phân nhánh dựa trên Confidence Score thì phân nhánh hoàn toàn vào số lượng document lấy được (`retrieved_services > 0` và `tool_results > 0`). Nếu không thỏa mãn, nó sẽ đưa về một trạng thái Fallback nói câu xin lỗi cố định.
3. **Chưa có Feedback Loop ở Backend:** Vòng lặp nhận structured feedback và cập nhật Golden Dataset chưa xuất hiện trong định nghĩa biểu đồ hay State của LangGraph.
4. **Fallback Fuzzy Search:** Code thực tế có thêm một cơ chế dự phòng hay. Nếu ChromaDB trả về tàng hình hoặc bị lọc hết do distance quá xa (>0.6), hàm `fallback_fuzzy_search` bên SQLite sẽ được gọi tiếp để vớt vát kết quả.
