from datetime import datetime
from typing import Tuple


def check_date_str(value: str, label: str = "Ngày") -> Tuple[bool, str]:
    """
    Kiểm tra:
    - Không rỗng
    - Đúng format YYYY-MM-DD
    - Là ngày hợp lệ (không 30/02, không tháng 13,...)
    """
    if value is None:
        return False, f"{label} không được để trống"

    if not isinstance(value, str):
        value = str(value)

    v = value.strip()
    if v == "":
        return False, f"{label} không được để trống"

    try:
        datetime.strptime(v, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, f"{label} phải có dạng YYYY-MM-DD và là ngày hợp lệ"


def rule_date(field: str, label: str = None, allow_empty: bool = False):
    """
    Rule cho 1 cột ngày:
    - (tuỳ chọn) không được để trống
    - Đúng format + hợp lệ (dùng check_date_str)
    """

    if label is None:
        label = field

    def _rule(data: dict):
        val = data.get(field)

        if val is None or (isinstance(val, str) and val.strip() == ""):
            if allow_empty:
                return True, ""
            return False, f"{label} không được để trống"

        ok, reason = check_date_str(val, label)
        return ok, reason

    return _rule


def rule_date_range(
    field: str,
    min_date: str = None,
    max_date: str = None,
    label: str = None,
    allow_empty: bool = False,
):
    """
    Rule ngày + range:
    - (tuỳ chọn) không được để trống
    - Đúng format + hợp lệ
    - Nếu min_date: date >= min_date
    - Nếu max_date: date <= max_date

    min_date, max_date: 'YYYY-MM-DD' hoặc None.
    """
    if label is None:
        label = field

    min_dt = datetime.strptime(min_date, "%Y-%m-%d") if min_date else None
    max_dt = datetime.strptime(max_date, "%Y-%m-%d") if max_date else None

    def _rule(data: dict):
        val = data.get(field)

        if val is None or (isinstance(val, str) and val.strip() == ""):
            if allow_empty:
                return True, ""
            return False, f"{label} không được để trống"

        ok, reason = check_date_str(val, label)
        if not ok:
            return False, reason

        dt = datetime.strptime(str(val).strip(), "%Y-%m-%d")

        if min_dt and dt < min_dt:
            return False, f"{label} phải >= {min_date}"
        if max_dt and dt > max_dt:
            return False, f"{label} phải <= {max_date}"

        return True, ""

    return _rule
