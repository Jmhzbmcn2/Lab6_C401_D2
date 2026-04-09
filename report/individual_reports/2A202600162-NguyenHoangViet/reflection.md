# Individual reflection — Nguyễn Văn A (AI20K001)

## 1. Role
Graph Orchestrator & Backend Developer. Thiết kế kiến trúc hệ thống và điều phối luồng xử lý Agentic Workflow.

## 2. Đóng góp cụ thể
- Xây dựng StateGraph: Sử dụng LangGraph phân tách logic thành các Node độc lập (Emergency, Retrieval, Clarification...).
- Backend: Phát triển hệ thống API với FastAPI

## 3. SPEC mạnh/yếu
- **Mạnh**: Kiểm soát luồng (Flow Control) — Logic chuyển hướng chính xác giữa các Node, đặc biệt là chặn cấp cứu và kháng ảo giác.
- **Yếu**: Chưa xử lý được một số edge case phức tạp — ví dụ khi bệnh nhân có triệu chứng mơ hồ, cần thêm logic để đánh giá nguy cơ.

## 4. Đóng góp khác
- Test prompt với 10 triệu chứng khác nhau, ghi log kết quả vào prompt-tests.md


## 5. Điều học được
- Thay vì để AI tự quyết định, việc xây dựng Agentic Workflow qua LangGraph giúp mình hiểu rằng: Trong y tế, kiểm soát luồng quan trọng hơn sự sáng tạo của AI.

## 6. Nếu làm lại
Sẽ test prompt sớm hơn — ngày đầu chỉ viết SPEC, đến trưa D6 mới bắt đầu test prompt.
Nếu test sớm từ tối D5 thì có thể iterate thêm 2-3 vòng, prompt sẽ tốt hơn nhiều.

## 7. AI giúp gì / AI sai gì
- **Giúp:** dùng Gemini để brainstorm failure modes — nó gợi ý được "bệnh nhân cần cấp cứu"
  mà nhóm không nghĩ ra. 
- **Sai/mislead:** Gợi ý thêm feature chẩn đoán bệnh qua triệu chứng — điều này không thực tế vì cần xét nghiệm, hình ảnh y học mới chẩn đoán được.