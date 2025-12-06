import sqlite3
import pandas as pd
import os
import random

# ================================================================
# CẤU HÌNH ĐƯỜNG DẪN
# ================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "database_nhanvien.db")
CSV_PATH = os.path.join(DATA_DIR, "doanhthu.csv")

# =============================
# 1️⃣ TẠO DATABASE NHÂN VIÊN (GIỮ NGUYÊN CODE CỦA BẠN)
# =============================

print(f"🔨 Đang khởi tạo Database tại: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Xóa bảng cũ
cursor.execute("DROP TABLE IF EXISTS ttNghi")
cursor.execute("DROP TABLE IF EXISTS ttNhanVien")
cursor.execute("DROP TABLE IF EXISTS khu_vuc")
cursor.execute("DROP TABLE IF EXISTS mat_hang")

# =============================
# KHU VỰC
# =============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS khu_vuc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_khu_vuc TEXT
)
""")

cursor.executemany("""
INSERT INTO khu_vuc (ten_khu_vuc) VALUES (?)
""", [
    ("Hải Châu",), ("Thanh Bình",), ("Thuận Phước",), ("Phước Ninh",), ("Bình Thuận",),
    ("Hòa Thuận Tây",), ("Hòa Thuận Đông",), ("Nại Hiên Đông",), ("An Hải Bắc",),
    ("",), (None,), ("   ",), ("12345",), ("@@@###$$$",), ("Hải Châu 1",),
    ("A" * 300,), ("\n\n",), ("DROP TABLE khu_vuc;--",),
])

# =============================
# MẶT HÀNG
# =============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS mat_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_hang TEXT
)
""")

cursor.executemany("""
INSERT INTO mat_hang (ten_hang) VALUES (?)
""", [
    ("Bóng Đá",), ("Áo đấu",), ("Giày thể thao",), ("Găng Tay",), ("Balo thể thao",),
    ("",), (None,), ("   ",), ("@@@###$$$",), ("123456",), ("Bóng đá",),
])

# =============================
# NHÂN VIÊN
# =============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ttNhanVien (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cccd TEXT,
    ten TEXT,
    chuc_vu TEXT,
    luong_co_ban REAL,
    id_khu_vuc INTEGER,
    id_mat_hang INTEGER,
    tinh_trang TEXT,
    FOREIGN KEY (id_khu_vuc) REFERENCES khu_vuc(id),
    FOREIGN KEY (id_mat_hang) REFERENCES mat_hang(id)
)
""")

cursor.executemany("""
INSERT INTO ttNhanVien (cccd, ten, chuc_vu, luong_co_ban, id_khu_vuc, id_mat_hang, tinh_trang)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    ("048201000001", "Võ Quốc Triều", "Quản lý", 18000000, 1, None, "0"),
    ("048201000002", "Võ Quốc Triệu", "Quản lý", 18000000, 1, None, "1"),
    ("048201000003", "Lê Khả Tuấn Linh", "Quản lý", 18000000, 2, None, "1"),
    ("048201000004", "Thái Văn Giác", "Quản lý", 18000000, 3, None, "1"),
    ("048201000005", "Phạm Minh Hòa", "Quản lý", 18000000, 4, None, "1"),
    ("048201000006", "Phạm an Bình", "Quản lý", 18000000, 6, None, "1"),
    ("048201000007", "Lê Khả Tuấn ", "Quản lý", 18000000, 2, 1, "1"),

    ("048201010001", "Nguyễn Văn An", "Nhân viên bán hàng", 9500000, 1, 1, "1"),
    ("048201010002", "Trần Thị Bình", "Nhân viên bán hàng", 9500000, 1, 2, "2"),
    ("048201010003", "Lê Minh Châu", "Nhân viên bán hàng", 9500000, 1, 3, "1"),
    ("048201010004", "Phạm Thị Dung", "Nhân viên bán hàng", 9500000, 1, 4, "1"),
    ("048201010005", "Hoàng Văn Dương", "Nhân viên bán hàng", 9500000, 1, 5, "1"),

    ("048201020001", "Phan Thị Giang", "Nhân viên bán hàng", 9500000, 2, 1, "1"),
    ("048201020002", "Vũ Minh Hiếu", "Nhân viên bán hàng", 9500000, 2, 2, "1"),
    ("048201020003", "Đỗ Thị Hạnh", "Nhân viên bán hàng", 9500000, 2, 3, "1"),
    ("048201020004", "Bùi Văn Hòa", "Nhân viên bán hàng", 9500000, 2, 4, "1"),
    ("048201020005", "Đặng Thị Hoa", "Nhân viên bán hàng", 9500000, 2, 5, "1"),

    ("048201030001", "Nguyễn Thị Hương", "Nhân viên bán hàng", 9500000, 3, 1, "2"),
    ("048201030002", "Trần Văn Hùng", "Nhân viên bán hàng", 9500000, 3, 2, "1"),
    ("048201030003", "Lê Thị Khánh", "Nhân viên bán hàng", 9500000, 3, 3, "1"),
    ("048201030004", "Phạm Minh Khôi", "Nhân viên bán hàng", 9500000, 3, 4, "1"),
    ("048201030111", "Hoàng Thị Lan", "Nhân viên bán hàng", 9500000, 3, 5, "1"),
    ("048201030222", "Hoàng Thị Cúc", "Nhân viên bán hàng", 9500000, 6, 5, "1"),
    ("048201030333", "Hoàng Thị Vàng", "Nhân viên bán hàng", 9500000, 7, 5, "1"),
    ("048201030444", "Hoàng Thị Tím", "Nhân viên bán hàng", 9500000, 8, 5, "1"),
    ("048201030455", "Hoàng Thị Hồng", "Nhân viên bán hàng", 9500000, 9, 5, "1"),
    ("048201030666", "Hoàng Thị Đỏ", "Nhân viên bán hàng", 9500000, 10, 5, "1"),

    ("048201040001", "Phan Văn Long", "Nhân viên bán hàng", 9500000, 4, 1, "1"),
    ("048201040002", "Vũ Thị Mai", "Nhân viên bán hàng", 9500000, 4, 2, "1"),
    ("048201040003", "Đỗ Minh Nam", "Nhân viên bán hàng", 9500000, 4, 3, "1"),
    ("048201040004", "Bùi Thị Nga", "Nhân viên bán hàng", 9500000, 4, 4, "1"),
    ("048201040005", "Đặng Văn Nghĩa", "Nhân viên bán hàng", 9500000, 4, 5, "1"),

    ("048201040001", "Phan Văn Long", "Nhân viên bán hàng", 9500000, 5, 1, "1"),
    ("048201040002", "Vũ Thị Mai", "Nhân viên bán hàng", 9500000, 6, 2, "1"),
    ("048201040003", "Đỗ Minh Nam", "Nhân viên bán hàng", 9500000, 7, 3, "1"),
    ("048201040004", "Bùi Thị Nga", "Nhân viên bán hàng", 9500000, 8, 4, "1"),
    ("048201040005", "Đặng Văn Nghĩa", "Nhân viên bán hàng", 9500000, 9, 5, "1"),
    ("048201040005", "Đặng Văn Nghĩa", "Nhân viên bán hàng", 9500000, 10, 5, "1"),

    ("048201050001", "Phạm Thị Phúc", "Nhân viên bán hàng", 9500000, 5, 1, "1"),
    ("048201050002", "Trần Thị Phương", "Nhân viên bán hàng", 9500000, 5, 2, "1"),

    ("", "", "Quản lý", 18000000, 5, None, "1"),
    (None, None, "Nhân viên", 5000000, 1, 1, "1"),
    ("   ", "   ", "Nhân viên", 5000000, 1, 1, "1"),
    ("123", "@@@###$$$", "Nhân viên", 5000000, 1, 1, "1"),
    ("abcdef123456", "123456", "Nhân viên", 5000000, 1, 1, "1"),
    ("99999999999999999999", "A" * 500, "Nhân viên", 5000000, 1, 1, "1"),
    ("000000000000", "Tên\0lỗi", "Nhân viên", 5000000, 1, 1, "1"),
    ("222222222222", "Robert'); DROP TABLE ttNhanVien;--", "Nhân viên", 5000000, 1, 1, "1"),

    ("048201060001", "Phạm anh Khoa", "", 2000000, 4, None, "1"),
    ("048201060002", "Nguyễn Thị Trinh", None, 5000000, 1, 1, "1"),
    ("048201060003", "Hoàng Thị Vy", "Quản lý", -10, 4, None, "1"),
    ("048201060004", "Phan Minh Ánh", "Quản lý", None, 4, None, "1"),
    ("048201060005", "Đặng Minh Đức", "Nhân viên", "abc", 1, 1, "1"),
    ("048201060006", "Trần Văn Khoa", "Quản lý", 2000000, None, None, "1"),

    ("999999999990", "Phạm Thị Quỳnh", "Nhân viên bán hàng", 9500000, 5, 4, "1"),
    ("999999999991", "Đỗ Minh Nam", "Nhân viên bán hàng", 9500000, 4, 3, "1"),
    ("999999999992", "Đỗ Thị Hạnh", "Nhân viên bán hàng", 9500000, 2, 3, "1"),
    ("048201000003", "Lê Khả Tuấn Linh", "Quản lý", 18000000, 2, None, "1"),
])

# =============================
# NGÀY NGHỈ
# =============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ttNghi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_nhan_vien INTEGER,
    ngay_nghi DATE,
    FOREIGN KEY (id_nhan_vien) REFERENCES ttNhanVien(id)
)
""")

cursor.executemany("""
INSERT INTO ttNghi (id_nhan_vien, ngay_nghi)
VALUES (?, ?)
""", [
    (9, "2025-10-02"), (18, "2025-10-01"), (30, "2025-10-03"), (31, "2025-10-01"),
    (35, "2025-10-01"), (68, "2025-10-01"), (27, "2025-10-01"),
    (None, "2025-10-05"), (9999, "2025-10-06"), (-5, "2025-10-07"),
    ("abc", "2025-10-08"), (10, None), (11, ""), (12, "2025/10/09"),
    (13, "10-10-2025"), (14, "2025-02-30"), (15, "2025-13-01"),
    (16, "abcd-ef-gh"), (100, "2025-10-08"),
])

conn.commit()
print("✅ Đã tạo database thành công!")

# ==============================================================================
# 2️⃣ TẠO FILE CSV (ĐÃ SỬA LẠI: CHỈ DÙNG HẢI CHÂU, KHÔNG DÙNG HẢI CHÂU 1/2)
# ==============================================================================

print(f"📝 Đang tạo CSV doanh thu tại: {CSV_PATH}")

# 1. Dữ liệu gốc (đã sửa Hải Châu 1/2 -> Hải Châu)
data = {
    "Khu_vuc": ["Hải Châu", "Hải Châu", "Thanh Bình", "Phước Ninh", "An Hải Bắc"],
    "Ten_SP": ["Bóng đá", "Áo đấu", "Giày thể thao", "Găng tay", "Balo thể thao"],
    "Gia_SP": [300000, 250000, 1200000, 150000, 350000],
    "So_Luong_ban": [50, 80, 40, 120, 60],
    "Ngay_ban": ["2025-10-01", "2025-10-02", "2025-10-03", "2025-10-04", "2025-10-40"]
}

# 2. Sinh thêm 30 dòng dữ liệu ngẫu nhiên (chỉ dùng danh sách chuẩn)
# Lưu ý: "Hải Châu 1" đã bị loại khỏi danh sách random này
sample_khu_vuc = ["Hải Châu", "Thanh Bình", "Thuận Phước", "Phước Ninh", "Bình Thuận", "Hòa Thuận Tây", "Hòa Thuận Đông", "An Hải Bắc"]

sample_san_pham = [
    ("Bóng đá", 300000), 
    ("Áo đấu", 250000), 
    ("Giày thể thao", 1200000), 
    ("Găng tay", 150000), 
    ("Balo thể thao", 350000)
]

for _ in range(300): # Tăng lên 300
    kv = random.choice(sample_khu_vuc)
    sp, gia = random.choice(sample_san_pham)
    sl = random.randint(1, 50)
    day = random.randint(1, 30)
    ngay = f"2025-10-{day:02d}"

    data["Khu_vuc"].append(kv)
    data["Ten_SP"].append(sp)
    data["Gia_SP"].append(gia)
    data["So_Luong_ban"].append(sl)
    data["Ngay_ban"].append(ngay)

df = pd.DataFrame(data)
df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

print(f"✅ CSV doanh thu đã tạo xong với {len(df)} dòng (Chỉ chứa tên khu vực chuẩn).")

conn.close()