import re
from typing import Tuple
from datetime import datetime

# ------------ CHECK TÊN ------------
NAME_REGEX = re.compile(r"^[a-zA-ZÀ-ỹà-ỹ\s]+$")


def check_name(value: str) -> Tuple[bool, str]:
    if not value or not NAME_REGEX.match(value):
        return False, f"Tên nhân viên '{value}' không hợp lệ"
    return True, ""


# ------------ CHECK KHU VỰC ------------
AREA_REGEX = re.compile(r"^[a-zA-ZÀ-ỹà-ỹ0-9\s]+$")


def check_area(value: str) -> Tuple[bool, str]:
    if not value or not AREA_REGEX.match(value):
        return False, f"Tên khu vực '{value}' không hợp lệ"
    return True, ""


# ------------ CHECK CCCD 12 SỐ THEO QUY TẮC ------------
def check_cccd(value: str) -> Tuple[bool, str]:
    """
    Check CCCD theo cấu trúc:
    AAA B YY XXXXXX
    - AAA: mã tỉnh (001–096)
    - B: mã thế kỷ + giới tính (0–9)
    - YY: 2 số cuối năm sinh
    - XXXXXX: số ngẫu nhiên
    """
    if not value:
        return False, "CCCD không được để trống"

    value = value.strip()

    # Phải đúng 12 số
    if not re.fullmatch(r"\d{12}", value):
        return False, f"CCCD '{value}' phải gồm đúng 12 chữ số"

    # 3 số đầu: mã tỉnh 001–096
    province = int(value[0:3])
    if province < 1 or province > 96:
        return False, f"CCCD '{value}' có mã tỉnh không hợp lệ"

    # 1 số mã thế kỷ + giới tính (0–9 là hợp lệ về hình thức)
    century_gender = int(value[3])
    if century_gender < 0 or century_gender > 9:
        return False, f"CCCD '{value}' có mã giới tính/thế kỷ không hợp lệ"

    # 2 số năm sinh (00–99) + 6 số sau: về mặt format đã đúng
    return True, ""


# ------------ CHECK NGÀY YYYY-MM-DD ------------
def check_date(value: str, label: str = "Ngày") -> Tuple[bool, str]:
    """
    Kiểm tra:
    - Không rỗng
    - Đúng format YYYY-MM-DD
    - Ngày hợp lệ (không 30/02, không tháng 13,...)
    """
    if value is None:
        return False, f"{label} không được để trống"

    if not isinstance(value, str) or value.strip() == "":
        return False, f"{label} không được để trống"

    val = value.strip()
    try:
        datetime.strptime(val, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, f"{label} phải có dạng YYYY-MM-DD và là ngày hợp lệ"


# ------------ CHECK LOGIC QUẢN LÝ ------------
def check_quan_ly_logic(data: dict) -> Tuple[bool, str]:
    """
    Rule: Nếu chức vụ là 'Quản lý' thì không được bán hàng.
    Tức là: ten_mat_hang phải là None hoặc rỗng.
    """
    # Lấy giá trị chức vụ, chuẩn hóa về chữ thường để so sánh
    chuc_vu = str(data.get("chuc_vu", "")).strip().lower()
    
    # Lấy thông tin mặt hàng (sau khi transform, field này là ten_mat_hang)
    mat_hang = data.get("ten_mat_hang")

    # Kiểm tra logic
    if chuc_vu == "quản lý":
        # Nếu mặt hàng tồn tại và không phải chuỗi rỗng
        if mat_hang is not None and str(mat_hang).strip() != "":
            return False, "Chức vụ 'Quản lý' không được phép có id_mat_hang (không được bán hàng)"
            
    return True, ""