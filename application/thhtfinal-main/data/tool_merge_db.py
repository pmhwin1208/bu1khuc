import sqlite3
import os
import csv
import sys

# ================================================================
# CẤU HÌNH ĐƯỜNG DẪN
# ================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR) 
if os.path.basename(CURRENT_DIR) == 'data': 
    BASE_DIR = CURRENT_DIR

DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    DATA_DIR = CURRENT_DIR

CLEAN_DB = os.path.join(DATA_DIR, "database_nhanvien_clean.db")
CLEAN_CSV = os.path.join(DATA_DIR, "doanhthu_clean.csv")
TARGET_DB = os.path.join(DATA_DIR, "data_tong.db")
ERROR_LOG_PATH = os.path.join(DATA_DIR, "loi_mapping.txt")

def get_connection(db_path):
    return sqlite3.connect(db_path)

def main():
    print("🚀 BẮT ĐẦU QUY TRÌNH MERGE DỮ LIỆU (CẤU TRÚC ĐỒNG BỘ)")
    print("="*60)

    if not os.path.exists(CLEAN_DB):
        print(f"❌ Lỗi: Không tìm thấy DB sạch: {CLEAN_DB}")
        return

    conn_clean = get_connection(CLEAN_DB)
    conn_clean.row_factory = sqlite3.Row
    cur_clean = conn_clean.cursor()

    if os.path.exists(TARGET_DB):
        try: os.remove(TARGET_DB)
        except: pass
    
    conn_target = get_connection(TARGET_DB)
    cur_target = conn_target.cursor()

    try:
        # ================================================================
        # BƯỚC 0: TẠO KHUNG SƯỜN
        # ================================================================
        print("\n🛠️  BƯỚC 0: TẠO CẤU TRÚC BẢNG")
        cur_target.executescript("""
            CREATE TABLE IF NOT EXISTS khu_vuc (id INTEGER PRIMARY KEY, ten_khu_vuc TEXT);
            CREATE TABLE IF NOT EXISTS mat_hang (id INTEGER PRIMARY KEY, ten_hang TEXT);
            
            CREATE TABLE IF NOT EXISTS ttNhanVien (
                id INTEGER PRIMARY KEY, 
                cccd TEXT UNIQUE, 
                Ten TEXT, Chuc_vu TEXT, 
                Luong_co_ban INTEGER, id_khu_vuc INTEGER, id_mat_hang INTEGER, tinh_trang TEXT
            );

            CREATE TABLE IF NOT EXISTS ttNghi (
                id INTEGER PRIMARY KEY, id_nhan_vien INTEGER, Ngay_nghi TEXT
            );
            
            CREATE TABLE IF NOT EXISTS hoa_don (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_nv INTEGER, 
                So_Luong_ban INTEGER, Gia_SP INTEGER, Ngay_ban TEXT
            );

            CREATE TABLE IF NOT EXISTS luong (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_nv INTEGER,
                chuc_vu TEXT,
                Luong_co_ban INTEGER,
                chuyen_can INTEGER,        
                thuong_doanh_thu INTEGER,  
                tong_luong INTEGER
            );

            CREATE TABLE IF NOT EXISTS doanh_thu_ca_nhan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_hoa_don INTEGER,
                id_nv INTEGER,
                tong_doanh_thu INTEGER,
                thang_nam TEXT
            );
        """)

        # ================================================================
        # BƯỚC 1 & 2: COPY DATA NỀN
        # ================================================================
        print("\n1️⃣  IMPORT DỮ LIỆU NỀN...")
        
        cur_clean.execute("SELECT id, ten_khu_vuc FROM khu_vuc")
        cur_target.executemany("INSERT INTO khu_vuc VALUES (?,?)", 
                               [(r["id"], r["ten_khu_vuc"]) for r in cur_clean.fetchall()])

        cur_clean.execute("SELECT id, ten_hang FROM mat_hang")
        cur_target.executemany("INSERT INTO mat_hang VALUES (?,?)", 
                               [(r["id"], r["ten_hang"]) for r in cur_clean.fetchall()])

        cur_clean.execute("SELECT * FROM ttNhanVien")
        rows_nv = cur_clean.fetchall()
        cur_target.executemany("""
            INSERT INTO ttNhanVien (id, cccd, Ten, Chuc_vu, Luong_co_ban, id_khu_vuc, id_mat_hang, tinh_trang)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(r["id"], r["cccd"], r["ten"], r["chuc_vu"], r["luong_co_ban"], 
               r["id_khu_vuc"], r["id_mat_hang"], r["tinh_trang"]) for r in rows_nv])
        
        cur_clean.execute("SELECT id_nhan_vien, ngay_nghi FROM ttNghi")
        cur_target.executemany("INSERT INTO ttNghi (id_nhan_vien, Ngay_nghi) VALUES (?, ?)", 
                               [(r["id_nhan_vien"], r["ngay_nghi"]) for r in cur_clean.fetchall()])

        print(f"   -> Đã import xong dữ liệu nền.")

        # ================================================================
        # BƯỚC 3: IMPORT HÓA ĐƠN
        # ================================================================
        print("\n2️⃣  IMPORT HÓA ĐƠN...")
        
        if not os.path.exists(CLEAN_CSV):
            print("   ⚠️  Không tìm thấy file CSV doanh thu.")
        else:
            cnt_success = 0
            cnt_fail = 0
            error_logs = [] 

            with open(CLEAN_CSV, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows_hd = []
                
                for i, row in enumerate(reader):
                    kv_name = row.get("khu_vuc", "").strip()
                    sp_name = row.get("ten_san_pham", "").strip()
                    
                    cur_target.execute("""
                        SELECT nv.id FROM ttNhanVien nv
                        JOIN khu_vuc kv ON nv.id_khu_vuc = kv.id
                        JOIN mat_hang mh ON nv.id_mat_hang = mh.id
                        WHERE LOWER(kv.ten_khu_vuc) = LOWER(?) 
                          AND LOWER(mh.ten_hang) = LOWER(?)
                        LIMIT 1
                    """, (kv_name, sp_name))
                    
                    found = cur_target.fetchone()
                    
                    if found:
                        id_nv = found[0]
                        rows_hd.append((
                            id_nv, 
                            row.get("so_luong", 1), 
                            row.get("gia", 0), 
                            row.get("ngay_ban")
                        ))
                        cnt_success += 1
                    else:
                        cnt_fail += 1
                        error_logs.append(f"Dòng {i+2}: Không tìm thấy NV tại '{kv_name}' bán '{sp_name}'")

                if rows_hd:
                    cur_target.executemany("""
                        INSERT INTO hoa_don (id_nv, So_Luong_ban, Gia_SP, Ngay_ban)
                        VALUES (?, ?, ?, ?)
                    """, rows_hd)
            
            if error_logs:
                with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f_log:
                    f_log.write("\n".join(error_logs))
                print(f"   ⚠️  Có {cnt_fail} lỗi mapping. Xem tại: {ERROR_LOG_PATH}")
            
            print(f"   ✅ Đã import {cnt_success} hóa đơn.")

        # ================================================================
        # BƯỚC 4: TÍNH TOÁN (ĐÃ ĐỒNG BỘ CÔNG THỨC)
        # ================================================================
        print("\n3️⃣  TÍNH TOÁN LƯƠNG & DOANH THU...")

        # --- 4.1 Bảng Doanh thu cá nhân ---
        cur_target.execute("""
            INSERT INTO doanh_thu_ca_nhan (id_hoa_don, id_nv, tong_doanh_thu, thang_nam)
            SELECT 
                id, id_nv, (So_Luong_ban * Gia_SP), strftime('%Y-%m', Ngay_ban)
            FROM hoa_don
        """)
        print("   ✅ Đã tạo: doanh_thu_ca_nhan")

        # --- 4.2 Bảng Lương (Chi tiết) ---
        cur_target.execute("""
            INSERT INTO luong (id_nv, chuc_vu, Luong_co_ban, chuyen_can, thuong_doanh_thu, tong_luong)
            SELECT 
                nv.id,
                nv.Chuc_vu,
                nv.Luong_co_ban,
                -- Chuyên cần: Nghỉ = 0 thì được 500k
                CASE WHEN (SELECT COUNT(*) FROM ttNghi WHERE id_nhan_vien = nv.id) = 0 THEN 500000 ELSE 0 END,
                -- Hoa hồng: 5%
                COALESCE(SUM(hd.So_Luong_ban * hd.Gia_SP) * 0.05, 0),
                -- Tổng = Lương + Chuyên Cần + Hoa Hồng
                nv.Luong_co_ban 
                + (CASE WHEN (SELECT COUNT(*) FROM ttNghi WHERE id_nhan_vien = nv.id) = 0 THEN 500000 ELSE 0 END)
                + COALESCE(SUM(hd.So_Luong_ban * hd.Gia_SP) * 0.05, 0)
            FROM ttNhanVien nv
            LEFT JOIN hoa_don hd ON nv.id = hd.id_nv
            GROUP BY nv.id, nv.Chuc_vu, nv.Luong_co_ban
        """)
        print("   ✅ Đã tạo: luong")

        # --- 4.3 Bảng data_tong (ĐÃ CẬP NHẬT ĐỂ KHỚP VỚI BẢNG LUONG) ---
        cur_target.execute("DROP TABLE IF EXISTS data_tong")
        cur_target.execute("""
        CREATE TABLE data_tong AS
        SELECT
            nv.id AS id_nv,
            nv.Ten,
            nv.Chuc_vu,
            nv.Luong_co_ban,
            kv.ten_khu_vuc,
            COALESCE(SUM(hd.So_Luong_ban * hd.Gia_SP), 0) AS tong_doanh_thu,
            -- CÔNG THỨC MỚI: CỘNG THÊM CẢ TIỀN CHUYÊN CẦN
            (
                nv.Luong_co_ban 
                + (CASE WHEN (SELECT COUNT(*) FROM ttNghi WHERE id_nhan_vien = nv.id) = 0 THEN 500000 ELSE 0 END)
                + COALESCE(SUM(hd.So_Luong_ban * hd.Gia_SP) * 0.05, 0)
            ) AS tong_luong
        FROM ttNhanVien nv
        LEFT JOIN khu_vuc kv ON nv.id_khu_vuc = kv.id
        LEFT JOIN hoa_don hd ON nv.id = hd.id_nv
        GROUP BY nv.id, nv.Ten, nv.Chuc_vu, nv.Luong_co_ban, kv.ten_khu_vuc;
        """)
        print("   ✅ Đã tạo: data_tong (Đã đồng bộ công thức tính lương)")

        conn_target.commit()

    except Exception as e:
        print(f"\n❌ CÓ LỖI: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn_clean.close()
        conn_target.close()
        print("\n" + "="*60)
        print("🎉 HOÀN TẤT! Dữ liệu 2 bảng đã khớp nhau.")

if __name__ == "__main__":
    main()