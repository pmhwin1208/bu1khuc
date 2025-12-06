import sqlite3
from random import randint, choice
from datetime import datetime, timedelta

# Kết nối DB

conn = sqlite3.connect("data_tong.db")
cur = conn.cursor()

# =====================

# Tạo bảng

# =====================

cur.executescript("""
CREATE TABLE IF NOT EXISTS khu_vuc (
id INTEGER PRIMARY KEY,
ten_khu_vuc TEXT
);

CREATE TABLE IF NOT EXISTS ttNhanVien (
id INTEGER PRIMARY KEY,
cccd TEXT UNIQUE,  -- Thêm dòng này vào
Ten TEXT,
Chuc_vu TEXT,
Luong_co_ban INTEGER,
id_khu_vuc INTEGER,
id_mat_hang INTEGER,
tinh_trang TEXT
);

CREATE TABLE IF NOT EXISTS ttnghi (
id INTEGER PRIMARY KEY,
id_nhan_vien INTEGER,
Ngay_nghi TEXT
);

CREATE TABLE IF NOT EXISTS mat_hang (
id INTEGER PRIMARY KEY,
ten_hang TEXT
);

CREATE TABLE IF NOT EXISTS hoa_don (
id INTEGER PRIMARY KEY,
id_nv INTEGER,
So_Luong_ban INTEGER,
Gia_SP INTEGER,
Ngay_ban TEXT
);

CREATE TABLE IF NOT EXISTS luong (
id INTEGER PRIMARY KEY,
id_nv INTEGER,
chuc_vu TEXT,
Luong_co_ban INTEGER,
chuyen_can INTEGER,
thuong_doanh_thu INTEGER,
tong_luong INTEGER
);

CREATE TABLE IF NOT EXISTS doanh_thu_ca_nhan (
id INTEGER PRIMARY KEY,
id_hoa_don INTEGER,
id_nv INTEGER,
tong_doanh_thu INTEGER,
thang_nam TEXT
);
""")
# =====================

# Tạo data_tong

# =====================

cur.execute("""
CREATE TABLE IF NOT EXISTS data_tong AS
SELECT
nv.id AS id_nv,
nv.Ten,
nv.Chuc_vu,
nv.Luong_co_ban,
kv.ten_khu_vuc,
COALESCE(SUM(hd.So_Luong_ban * hd.Gia_SP),0) AS tong_doanh_thu,
(nv.Luong_co_ban + COALESCE(SUM(hd.So_Luong_ban * hd.Gia_SP)*0.05,0)) AS tong_luong
FROM ttNhanVien nv
LEFT JOIN khu_vuc kv ON nv.id_khu_vuc = kv.id
LEFT JOIN hoa_don hd ON nv.id = hd.id_nv
GROUP BY nv.id
""")

conn.commit()
conn.close()

print("Đã tạo database và bảng data_tong thành công!")
