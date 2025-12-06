import re


def rule_regex(field: str, pattern: str, label: str = None, allow_empty: bool = False):
    if label is None:
        label = field
    regex = re.compile(pattern)

    def _rule(data: dict):
        val = data.get(field)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            if allow_empty:
                return True, ""
            return False, f"{label} không được để trống"
        if not isinstance(val, str):
            val_str = str(val)
        else:
            val_str = val
        if not regex.fullmatch(val_str.strip()):
            return False, f"{label} không đúng định dạng"
        return True, ""

    return _rule
