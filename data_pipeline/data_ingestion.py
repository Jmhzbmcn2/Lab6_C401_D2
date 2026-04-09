import pandas as pd
import sqlite3
import os

# Đường dẫn tuyệt đối cho an toàn
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "hospital_services.db")

# Đảm bảo thư mục database tồn tại
os.makedirs(DB_DIR, exist_ok=True)

def init_db(db_path):
    """Khởi tạo csdl SQLite và tạo bảng nếu chưa có."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch TEXT,
            service_code TEXT,
            service_name_vn TEXT,
            service_name_en TEXT,
            service_group TEXT,
            price REAL
        )
    ''')
    # Xoá dữ liệu cũ nếu chạy lại kịch bản nhiều lần
    cursor.execute('DELETE FROM services')
    
    # Đặt lại auto-increment
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="services"')
    conn.commit()
    return conn

def clean_price(val):
    """Xóa bỏ các ký tự đặc biệt, dấu phẩy, khoảng trắng khỏi giá, chuyển sang số."""
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace(',', '').replace(' ', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def ingest_smart_city(conn, file_path):
    """Xử lý dữ liệu từ file Smart City.xlsx"""
    print(f"Đang xử lý: {file_path}")
    # Bắt đầu đọc từ dòng thứ 3 (row index 2)
    df = pd.read_excel(file_path, skiprows=2)
    
    # Bỏ qua các dòng không có Mã Dịch vụ (dòng trống)
    df = df.dropna(subset=[df.columns[0]])
    
    cursor = conn.cursor()
    count = 0
    for idx, row in df.iterrows():
        try:
            val_code = str(row.iloc[0]).strip()
            val_name_vn = str(row.iloc[1]).strip()
            val_group = str(row.iloc[2]).strip()
            val_price = clean_price(row.iloc[3])
            
            # Chỉ nạp nếu có giá trị
            if not val_code or val_code == 'nan':
                continue
                
            cursor.execute('''
                INSERT INTO services (branch, service_code, service_name_vn, service_name_en, service_group, price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("Smart City", val_code, val_name_vn, None, val_group, val_price))
            count += 1
        except Exception as e:
            print(f"  [X] Bỏ qua dòng {idx} (Smart City) do lỗi: {e}")
            continue
            
    conn.commit()
    print(f"=> Đã lưu thành công {count} dịch vụ của Smart City.")

def ingest_times_city(conn, file_path):
    """Xử lý dữ liệu từ file Times_city.xlsx"""
    print(f"Đang xử lý: {file_path}")
    # Bắt đầu đọc từ dòng thứ 3 (row index 2)
    df = pd.read_excel(file_path, skiprows=2)
    
    # Bỏ qua các dòng không có Mã Dịch vụ
    df = df.dropna(subset=[df.columns[0]])
    
    cursor = conn.cursor()
    count = 0
    for idx, row in df.iterrows():
        try:
            val_code = str(row.iloc[0]).strip()
            val_name_vn = str(row.iloc[1]).strip()
            
            # Cột 3 có thể là nan nếu không có tiếng Anh
            val_name_en = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None
            val_group = str(row.iloc[3]).strip()
            val_price = clean_price(row.iloc[5])
            
            if not val_code or val_code == 'nan':
                continue
                
            cursor.execute('''
                INSERT INTO services (branch, service_code, service_name_vn, service_name_en, service_group, price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("Times City", val_code, val_name_vn, val_name_en, val_group, val_price))
            count += 1
        except Exception as e:
            print(f"  [X] Bỏ qua dòng {idx} (Times City) do lỗi: {e}")
            continue
            
    conn.commit()
    print(f"=> Đã lưu thành công {count} dịch vụ của Times City.")

def main():
    smart_city_file = os.path.join(DATA_DIR, "Smart City.xlsx")
    times_city_file = os.path.join(DATA_DIR, "Times_city.xlsx")
    
    if not os.path.exists(smart_city_file) or not os.path.exists(times_city_file):
        print("[!] Không tìm thấy dữ liệu mẫu trong thư mục data.")
        return

    print("--- KHỞI TẠO CƠ SỞ DỮ LIỆU ---")
    conn = init_db(DB_PATH)
    
    ingest_smart_city(conn, smart_city_file)
    ingest_times_city(conn, times_city_file)
    
    # Hiển thị số liệu chốt
    cursor = conn.cursor()
    cursor.execute("SELECT branch, COUNT(*) FROM services GROUP BY branch")
    rows = cursor.fetchall()
    print("\n--- THỐNG KÊ DATA LOG ---")
    for row in rows:
        print(f"Cơ sở: {row[0]} - Số lượng dịch vụ: {row[1]}")
    
    print("\n[OK] Quá trình Data Ingestion hoàn tất. DB được lưu tại:", DB_PATH)
    conn.close()

if __name__ == "__main__":
    main()
