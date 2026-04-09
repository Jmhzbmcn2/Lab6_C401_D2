import sqlite3
import os

# Đường dẫn lên gốc Lab06: app/database -> app -> backend -> Lab06
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
DB_PATH = os.path.join(BASE_DIR, "database", "hospital_services.db")

def query_services_by_ids(ids: list, branch_filter: str = None) -> list:
    """Truy vấn giá chính xác từ SQLite dựa trên list ID từ Chroma."""
    if not ids:
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    placeholders = ','.join('?' for _ in ids)
    params = list(ids)
    
    sql = f"SELECT id, branch, service_name_vn, service_group, price FROM services WHERE id IN ({placeholders})"
    
    # Pre-filter theo SQLite (có thể tuỳ intent)
    if branch_filter and "smart city" in branch_filter.lower():
        sql += " AND branch = 'Smart City'"
    elif branch_filter and "times city" in branch_filter.lower():
        sql += " AND branch = 'Times City'"
        
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "branch": row[1],
            "service_name_vn": row[2],
            "service_group": row[3],
            "price": row[4]
        })
    return results

def fallback_fuzzy_search(normalized_query: str, branch_filter: str = None) -> list:
    """Tìm kiếm fuzzy (keyword matching) khi Vector DB không khả dụng."""
    if not normalized_query:
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    keywords = normalized_query.split()
    query = "SELECT id, branch, service_name_vn, service_group, price FROM services WHERE "
    conditions = ["service_name_vn LIKE ?"] * len(keywords)
    query += " AND ".join(conditions)
    
    params = [f"%{k}%" for k in keywords]
    if branch_filter and "smart city" in branch_filter.lower():
        query += " AND branch = 'Smart City'"
    elif branch_filter and "times city" in branch_filter.lower():
        query += " AND branch = 'Times City'"
        
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()[:10]  # LIMIT 10
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "branch": row[1],
            "service_name_vn": row[2],
            "service_group": row[3],
            "price": row[4]
        })
    return results
