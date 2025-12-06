import json
import os

LOG_FILE = "/app/data/loi_du_lieu.txt"


def record_error(raw_data: dict, reason: str):
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("---- LỖI ----\n")
            f.write(f"Lý do: {reason}\n")
            f.write(json.dumps(raw_data, ensure_ascii=False))
            f.write("\n\n")
        print(f"[LOGGER] 📝 Ghi lỗi: {reason}")
    except Exception as e:
        print(f"[LOGGER] ❌ Không ghi được log lỗi: {e}")
