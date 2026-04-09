# NHẬT KÝ NGHIÊN CỨU & THIẾT KẾ CƠ SỞ DỮ LIỆU
**Vai trò:** Data & SQL Ops
**Mô tả:** Tài liệu lưu trữ các notes trong quá trình thiết kế hệ thống SQLite fallback và cấu trúc truy xuất dữ liệu chống ảo giác (Hallucination).

## 1. Bài toán: Giải bài toán nhiễu giá (Price Hallucination)
- **Vấn đề ban đầu:** Khi dùng RAG (Vector Search) để tra cứu giá, do dữ liệu có cấu trúc từ ngữ giống hệt nhau (Ví dụ: "Xét nghiệm máu" gặp ở cả 2 cơ sở), Vector Similarity thường hay bốc nhầm tài liệu của Times City trả về cho khách hỏi Smart City vì khoảng cách véc-tơ quá gần nhau.
- **Quyết định (SQL Injection by Intent):** Sau khi Research, tôi chốt phương án không cho Vector DB quản lý mảng phân loại chi nhánh. Thay vào đó cấu trúc lại flow:
  `Vector Search (Lấy ra ID) -> SQL Tool Execution (Lọc Branch)`
  
  *Trích xuất code draft nháp ban đầu của tôi:*
  ```sql
  -- Truy vấn cứng chống nhiễu
  SELECT id, branch, service_name_vn, service_group, price 
  FROM services 
  WHERE id IN (?) AND branch = 'Smart City'
  ```

## 2. Research thuật toán Fallback
- Nếu Langchain/ChromaDB bị nghẽn hoặc kết quả Vector Distance xa (> 0.6), tool execution lấy rỗng. Bot sẽ trả lời "Không hiểu".
- Cần xây dựng thuật toán cứu cánh (Fuzzy match):
  - Chuyển `normalized_query` (VD: "siêu âm thai nhi") thành List keywords `["siêu", "âm", "thai", "nhi"]`
  - Sinh chuỗi truy vấn động trong Python SQLite:
  ```python
  query = "SELECT id, branch, service_name_vn, price FROM services WHERE "
  conditions = ["service_name_vn LIKE ?"] * len(keywords) # Mở rộng linh hoạt
  query += " AND ".join(conditions)
  ```
  -> **Kết quả test:** Xử lý cứu sống được ~30% lượng queries gõ sai chính tả nhẹ hoặc vector embedding không bắt được context.

## 3. Cấu trúc bảng (Schema Iteration V2)
Sẵn sàng cho việc tính toán dữ liệu lớn sau hackathon:
```python
# Bảng services chuẩn hóa
CREATE TABLE IF NOT EXISTS services (
    id TEXT PRIMARY KEY,
    hospital_code TEXT,
    branch TEXT, 
    department TEXT,
    service_group TEXT, 
    service_name_vn TEXT,
    service_name_en TEXT,
    price REAL
)
```
