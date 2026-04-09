import sqlite3
import os
import chromadb
from chromadb.utils import embedding_functions

# Đường dẫn tĩnh
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "hospital_services.db")
CHROMA_PATH = os.path.join(BASE_DIR, "database", "chroma_db")

def main():
    print("🚀 Bắt đầu khởi tạo Vector Database (ChromaDB)...")

    # 1. Khởi tạo Chroma Client và Collection
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Sử dụng Embedding Model hỗ trợ Tiếng Việt (Miễn phí, chạy local)
    print(">> Đang tải Embedding Model (paraphrase-multilingual-MiniLM-L12-v2)...")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # Xóa collection cũ nếu tồn tại để tạo lại (tránh trùng dữ liệu)
    try:
        client.delete_collection(name="medical_services")
        print(">> Đã xóa Collection cũ.")
    except Exception:
        pass
        
    collection = client.create_collection(
        name="medical_services",
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"} # Sử dụng khoảng cách Cosine
    )

    # 2. Đọc dữ liệu từ SQLite
    print(">> Đang đọc dữ liệu từ SQLite...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, branch, service_code, service_name_vn, service_group FROM services")
    rows = cursor.fetchall()
    conn.close()

    total_rows = len(rows)
    print(f">> Tổng cộng tìm thấy {total_rows} dịch vụ.")

    # 3. Chuẩn bị dữ liệu để đưa vào ChromaDB
    ids = []
    documents = [] # Dữ liệu văn bản dùng để nhúng
    metadatas = [] # Siêu dữ liệu dùng để Filter

    for row in rows:
        row_id = str(row[0]) # ChromaDB yêu cầu ID phải là chuỗi
        branch = row[1]
        code = row[2]
        name_vn = row[3]
        group = row[4]
        
        ids.append(row_id)
        # Văn bản dùng để semantic search chính là Tên Tiếng Việt
        documents.append(name_vn) 
        
        # Metadata chứa branch để có thể pre-filter
        metadatas.append({
            "branch": branch,
            "service_code": code,
            "group": group
        })

    # 4. Lưu từng batch vào ChromaDB để tránh quá tải RAM (Batch 500)
    print(f">> Bắt đầu Embedding và nạp vào DB (Quá trình này tùy thuộc vào CPU)...")
    batch_size = 500
    for i in range(0, total_rows, batch_size):
        end = min(i + batch_size, total_rows)
        batch_ids = ids[i:end]
        batch_documents = documents[i:end]
        batch_metadatas = metadatas[i:end]
        
        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        print(f"   + Đã nạp batch [{i} - {end}]")

    print(f"\n✅ HOÀN TẤT! Vector DB đã được lưu tại {CHROMA_PATH}")
    print(f"Collection 'medical_services' hiện chứa {collection.count()} vectors.")

if __name__ == "__main__":
    main()
