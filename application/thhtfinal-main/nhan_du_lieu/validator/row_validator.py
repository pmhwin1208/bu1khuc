from rules.rule_not_empty import rule_not_empty
from rules.rule_max_length import rule_max_length
from rules.rule_helpers import check_name, check_area, check_cccd, check_quan_ly_logic
from rules.rule_date import rule_date_range


# =========================================
#  CẤU HÌNH RULE THEO CỘT – NHÂN VIÊN (SQLITE)
# =========================================
def _column_rules_sqlite():
    """
    Trả về dict: field -> list rule cho field đó.
    Mỗi rule: (data) -> (ok: bool, reason: str)
    """
    return {
        # CCCD
        "cccd": [
            rule_not_empty("cccd", "CCCD"),
            lambda d: check_cccd(d.get("cccd", "")),
        ],

        # TÊN NHÂN VIÊN
        "ten": [
            rule_not_empty("ten", "Tên nhân viên"),
            rule_max_length("ten", 40, "Tên nhân viên"),
            lambda d: check_name(d.get("ten", "")),
        ],

        # CHỨC VỤ
        "chuc_vu": [
            rule_not_empty("chuc_vu", "Chức vụ"),
            rule_max_length("chuc_vu", 50, "Chức vụ"),
            check_quan_ly_logic,
        ],

        # LƯƠNG CƠ BẢN
        "luong_co_ban": [
            lambda d: (
                d.get("luong_co_ban") is not None
                and isinstance(d.get("luong_co_ban"), (int, float))
                and d["luong_co_ban"] >= 0,
                "Lương cơ bản phải là số và ≥ 0",
            ),
        ],

        # TÌNH TRẠNG
        "tinh_trang": [
            lambda d: (
                d.get("tinh_trang") in ("0", "1"),
                "Tình trạng phải là '0' hoặc '1'",
            ),
        ],

        # TÊN KHU VỰC
        "ten_khu_vuc": [
            rule_not_empty("ten_khu_vuc", "Tên khu vực"),
            rule_max_length("ten_khu_vuc", 30, "Tên khu vực"),
            lambda d: check_area(d.get("ten_khu_vuc", "")),
        ],

        # TÊN MẶT HÀNG
        "ten_mat_hang": [
            # Quản lý: cho phép rỗng
            lambda d: (
                True,
                "",
            )
            if d.get("chuc_vu", "").lower() == "quản lý"
            else (
                bool(str(d.get("ten_mat_hang") or "").strip()),
                "Tên mặt hàng không được để trống với Nhân viên bán hàng",
            ),
            rule_max_length("ten_mat_hang", 50, "Tên mặt hàng"),
        ],
    }
# Rule kiểm tra giá sản phẩm, vẫn nhận string
def rule_gia(d):
    val = d.get("gia")
    try:
        num = float(str(val).replace(",", "").strip())  # convert tạm thời
        return num > 0, "Giá sản phẩm phải là số > 0"
    except:
        return False, "Giá sản phẩm phải là số > 0"

# Rule kiểm tra số lượng bán
def rule_so_luong(d):
    val = d.get("so_luong")
    try:
        num = float(str(val).replace(",", "").strip())
        return num >= 0, "Số lượng bán phải là số ≥ 0"
    except:
        return False, "Số lượng bán phải là số ≥ 0"



# =========================================
#  CẤU HÌNH RULE THEO CỘT – DOANH THU (CSV)
# =========================================
def _column_rules_csv():
    return {
        "khu_vuc": [
            rule_not_empty("khu_vuc", "Khu vực"),
            rule_max_length("khu_vuc", 30, "Khu vực"),
        ],
        "ten_san_pham": [
            rule_not_empty("ten_san_pham", "Tên sản phẩm"),
            rule_max_length("ten_san_pham", 50, "Tên sản phẩm"),
        ],
        "gia": [rule_gia],
        "so_luong": [rule_so_luong],
        "ngay_ban": [
            rule_date_range(
                field="ngay_ban",
                min_date="2000-01-01",
                max_date="2100-12-31",
                label="Ngày bán",
            ),
        ],
    }



# =========================================
#  RAW VALIDATE – TRƯỚC TRANSFORM
# =========================================
def validate_raw_message(raw_data: dict):
    """
    Check nhanh ở tầng RAW (thiếu field quan trọng).
    """
    source = raw_data.get("source")

    if source == "sqlite":
        if not raw_data.get("cccd"):
            return False, "Thiếu CCCD (raw)"
        if not raw_data.get("ten"):
            return False, "Thiếu tên nhân viên (raw)"
        if not raw_data.get("chuc_vu"):
            return False, "Thiếu chức vụ nhân viên (raw)"
        return True, ""

    elif source == "csv":
        if not raw_data.get("Khu_vuc"):
            return False, "Thiếu Khu_vuc (raw)"
        if not (raw_data.get("Ten_SP") or raw_data.get("Tên SP")):
            return False, "Thiếu Ten_SP (raw)"
        if raw_data.get("Gia_SP") in (None, ""):
            return False, "Thiếu Gia_SP (raw)"
        if (
            raw_data.get("So_Luong_ban") in (None, "")
            and raw_data.get("SL bán") in (None, "")
        ):
            return False, "Thiếu So_Luong_ban (raw)"
        if not raw_data.get("Ngay_ban"):
            return False, "Thiếu Ngay_ban (raw)"
        return True, ""

    else:
        return False, "Không xác định được source (raw)"


# =========================================
#  HÀM CHUNG VALIDATE THEO CỘT
# =========================================
def _validate_by_column(data: dict, rules_by_col: dict):
    errors_by_col = {}

    for field, rules in rules_by_col.items():
        for rule in rules:
            ok, reason = rule(data)
            if not ok:
                errors_by_col.setdefault(field, []).append(reason)

    if not errors_by_col:
        return True, ""

    messages = []
    for field, errs in errors_by_col.items():
        msg = f"{field}: " + "; ".join(errs)
        messages.append(msg)

    full_reason = " | ".join(messages)
    return False, full_reason


# =========================================
#  VALIDATE SAU TRANSFORM: NHÂN VIÊN / CSV
# =========================================
def validate_transformed(data: dict, source: str):
    """
    - sqlite: validate nhân viên sau transform
    - csv: validate dòng doanh thu sau transform
    """
    if source == "sqlite":
        return _validate_by_column(data, _column_rules_sqlite())
    elif source == "csv":
        return _validate_by_column(data, _column_rules_csv())
    else:
        return False, "Không xác định được source (after transform)"


# =========================================
#  VALIDATE RIÊNG CHO BẢN GHI NGÀY NGHỈ
# =========================================
def validate_ngay_nghi_row(row: dict):
    """
    row: {"id_nhan_vien": int, "ngay_nghi": "YYYY-MM-DD"}
    Dùng cho bảng ttNghi (sạch).
    """
    # id_nhan_vien: bắt buộc, số dương
    emp_id = row.get("id_nhan_vien")
    if emp_id is None:
        return False, "id_nhan_vien không được để trống"

    try:
        emp_id_int = int(emp_id)
        if emp_id_int <= 0:
            return False, "id_nhan_vien phải > 0"
    except Exception:
        return False, "id_nhan_vien phải là số nguyên"

    # ngày nghỉ: dùng rule_date_range để check format + khoảng
    rule = rule_date_range(
        field="ngay_nghi",
        min_date="2000-01-01",
        max_date="2100-12-31",
        label="Ngày nghỉ",
    )
    ok, reason = rule(row)
    if not ok:
        return False, reason

    return True, ""
