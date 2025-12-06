import csv
import os

CLEAN_CSV = "/app/data/doanhthu_clean.csv"


def save_clean_csv(row: dict):
    header = ["khu_vuc", "ten_san_pham", "gia", "so_luong", "ngay_ban", "status"]
    os.makedirs(os.path.dirname(CLEAN_CSV), exist_ok=True)
    file_exists = os.path.exists(CLEAN_CSV)

    with open(CLEAN_CSV, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow({h: row.get(h, "") for h in header})

    print(f"[CSV_WRITER] 💾 Đã ghi 1 dòng vào {CLEAN_CSV}")
