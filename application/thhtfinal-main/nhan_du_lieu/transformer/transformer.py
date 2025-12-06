import logging
from utils.date_utils import normalize_date

logging.basicConfig(filename="transform_errors.log", level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def transform_data(data: dict) -> dict:
    source = data.get("source")

    # ============================================
    # SQLITE → NHÂN VIÊN (CÓ DANH SÁCH NGÀY NGHỈ)
    # ============================================
    if source == "sqlite":
        ten = (data.get("ten") or "").strip()
        chuc_vu = (data.get("chuc_vu") or "").strip()
        luong = data.get("luong_co_ban")

        # normalize tình trạng
        tinh_raw = str(data.get("tinh_trang") or "").strip().lower()
        if tinh_raw in ("1", "lam"):
            tinh_trang = "1"
        elif tinh_raw in ("0", "nghi"):
            tinh_trang = "0"
        else:
            tinh_trang = "1"  # default (validator sẽ reject nếu sai)

        ten_khu_vuc = (data.get("ten_khu_vuc") or "").strip() or None
        ten_mat_hang = (data.get("ten_mat_hang") or "").strip() or None

        # Chuẩn hóa danh sách ngày nghỉ
        raw_nghi = data.get("ngay_nghi", [])
        normalized_nghi = []
        for item in raw_nghi:
            raw_day = item.get("ngay_nghi")
            normalized_day = normalize_date(raw_day)
            normalized_nghi.append({"ngay_nghi": normalized_day})

        return {
            "cccd": data.get("cccd"),
            "ten": ten,
            "chuc_vu": chuc_vu,
            "luong_co_ban": luong,
            "tinh_trang": tinh_trang,
            "ten_khu_vuc": ten_khu_vuc,
            "ten_mat_hang": ten_mat_hang,
            "ngay_nghi": normalized_nghi,
            "status": "PROCESSED_OK",
        }

    # ============================================
    # CSV → DOANH THU
    # ============================================
    khu_vuc = (data.get("Khu_vuc") or "").strip()
    ten_sp = (data.get("Ten_SP") or data.get("Tên SP") or "").strip()
    gia = data.get("Gia_SP")
    so_luong = data.get("So_Luong_ban") or data.get("SL bán")

    ngay_ban_raw = data.get("Ngay_ban")
    ngay_ban = normalize_date(ngay_ban_raw)

    return {
        "khu_vuc": khu_vuc,
        "ten_san_pham": ten_sp,
        "gia": gia,
        "so_luong": so_luong,
        "ngay_ban": ngay_ban,
        "status": "PROCESSED_OK",
    }
