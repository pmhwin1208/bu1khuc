import sqlite3
import sys
import json
from datetime import datetime


class DataAccessObject:
    def __init__(self, db_file: str):
        self.db_file = db_file
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()

            # ====== BẢNG STAGING RAW (sau MQ) ======
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS staging_raw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                received_at TEXT,
                raw_json TEXT,
                status TEXT,          -- RECEIVED / SUCCESS / FAILED
                error_message TEXT,
                output_table TEXT,
                output_id INTEGER
            )
            """)

            # ====== DIM KHU VỰC (SẠCH) ======
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS khu_vuc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_khu_vuc TEXT NOT NULL UNIQUE
            )
            """)

            # ====== DIM MẶT HÀNG (SẠCH) ======
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mat_hang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_hang TEXT NOT NULL UNIQUE
            )
            """)

            # ====== NHÂN VIÊN SẠCH (DÙNG CCCD LÀM BUSINESS KEY) ======
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ttNhanVien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cccd TEXT NOT NULL UNIQUE,
                ten TEXT NOT NULL,
                chuc_vu TEXT NOT NULL,
                luong_co_ban REAL NOT NULL CHECK (luong_co_ban >= 0),
                id_khu_vuc INTEGER,
                id_mat_hang INTEGER,
                tinh_trang TEXT NOT NULL CHECK (tinh_trang IN ('1','0')),
                FOREIGN KEY (id_khu_vuc) REFERENCES khu_vuc(id),
                FOREIGN KEY (id_mat_hang) REFERENCES mat_hang(id)
            )
            """)

            # ====== NGÀY NGHỈ SẠCH ======
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ttNghi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_nhan_vien INTEGER NOT NULL,
                ngay_nghi DATE NOT NULL,
                FOREIGN KEY (id_nhan_vien) REFERENCES ttNhanVien(id)
            )
            """)

            self.conn.commit()
            print("[DAO] ✅ DB sạch + STAGING đã sẵn sàng.")
        except Exception as e:
            print(f"[DAO] ❌ Lỗi kết nối / khởi tạo DB: {e}")
            sys.exit(1)

    # ========= STAGING =========

    def save_raw_message(self, raw_data: dict):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO staging_raw (source, received_at, raw_json, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                raw_data.get("source"),
                datetime.utcnow().isoformat(),
                json.dumps(raw_data, ensure_ascii=False),
                "RECEIVED",
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_staging_status(
        self,
        staging_id: int,
        status: str,
        error_message: str = None,
        output_table: str = None,
        output_id: int = None,
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE staging_raw
            SET status = ?, error_message = ?, output_table = ?, output_id = ?
            WHERE id = ?
            """,
            (status, error_message, output_table, output_id, staging_id),
        )
        self.conn.commit()

    # ========= DIM HELPERS =========

    def _get_or_create_khu_vuc(self, ten_khu_vuc: str):
        if not ten_khu_vuc:
            return None
        ten_khu_vuc = ten_khu_vuc.strip()
        if not ten_khu_vuc:
            return None

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM khu_vuc WHERE ten_khu_vuc = ?",
            (ten_khu_vuc,),
        )
        row = cursor.fetchone()
        if row:
            return row["id"]

        cursor.execute(
            "INSERT INTO khu_vuc (ten_khu_vuc) VALUES (?)",
            (ten_khu_vuc,),
        )
        self.conn.commit()
        return cursor.lastrowid

    def _get_or_create_mat_hang(self, ten_hang: str):
        if not ten_hang:
            return None
        ten_hang = ten_hang.strip()
        if not ten_hang:
            return None

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM mat_hang WHERE ten_hang = ?",
            (ten_hang,),
        )
        row = cursor.fetchone()
        if row:
            return row["id"]

        cursor.execute(
            "INSERT INTO mat_hang (ten_hang) VALUES (?)",
            (ten_hang,),
        )
        self.conn.commit()
        return cursor.lastrowid

    # ========= API CHÍNH =========

    def save_data(self, table: str, data: dict):
        cursor = self.conn.cursor()
        try:
            if table == "ttNhanVien":
                # chuẩn bị id_khu_vuc
                id_khu_vuc = data.get("id_khu_vuc")
                if not id_khu_vuc:
                    ten_kv = data.get("ten_khu_vuc") or data.get("khu_vuc")
                    if ten_kv:
                        id_khu_vuc = self._get_or_create_khu_vuc(ten_kv)

                # chuẩn bị id_mat_hang
                id_mat_hang = data.get("id_mat_hang")
                if not id_mat_hang:
                    ten_hang = (
                        data.get("ten_mat_hang")
                        or data.get("ten_hang")
                        or data.get("Ten_SP")
                    )
                    if ten_hang:
                        id_mat_hang = self._get_or_create_mat_hang(ten_hang)

                tinh_trang = data.get("tinh_trang") or "1"

                cursor.execute(
                    """
                    INSERT INTO ttNhanVien
                        (cccd, ten, chuc_vu, luong_co_ban, id_khu_vuc, id_mat_hang, tinh_trang)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["cccd"],
                        data["ten"],
                        data["chuc_vu"],
                        data["luong_co_ban"],
                        id_khu_vuc,
                        id_mat_hang,
                        tinh_trang,
                    ),
                )
                self.conn.commit()
                return cursor.lastrowid

            elif table == "ttNghi":
                cursor.execute(
                    """
                    INSERT INTO ttNghi (id_nhan_vien, ngay_nghi)
                    VALUES (?, ?)
                    """,
                    (
                        data["id_nhan_vien"],
                        data["ngay_nghi"],
                    ),
                )
                self.conn.commit()
                return cursor.lastrowid

            else:
                raise ValueError(f"Table không hỗ trợ: {table}")

        except Exception as e:
            print(f"[DAO] ❌ Lỗi lưu {table}: {e}")
            raise
            
    # ========= QUERY HỖ TRỢ =========

    def get_employee_by_cccd(self, cccd: str):
        if not cccd:
            return None
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM ttNhanVien WHERE cccd = ?",
            (cccd,),
        )
        row = cursor.fetchone()
        return row["id"] if row else None
