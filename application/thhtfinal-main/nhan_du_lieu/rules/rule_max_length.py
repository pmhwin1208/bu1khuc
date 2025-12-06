def rule_max_length(field: str, max_len: int, label: str):
    """
    Kiểm tra độ dài tối đa của 1 field.
    """
    def _rule(data: dict):
        value = data.get(field, "")
        if value is None:
            return True, ""
        if len(value) <= max_len:
            return True, ""
        return False, f"{label} vượt quá độ dài cho phép ({max_len} ký tự)"
    return _rule
