from datetime import datetime

def normalize_date(value: str):
    """
    Chuẩn hóa ngày về dạng YYYY-MM-DD.
    Nếu không convert được → trả về giá trị gốc để validator bắt lỗi.
    """
    if not value or not isinstance(value, str):
        return value

    value = value.strip()

    # Các kiểu ngày thường gặp sai
    possible_formats = [
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
        "%Y %m %d",
        "%d %m %Y",
    ]

    # Thử convert
    for fmt in possible_formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except:
            pass

    # Nếu đã đúng dạng YYYY-MM-DD thì giữ nguyên
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except:
        return value   # để validator bắt lỗi
