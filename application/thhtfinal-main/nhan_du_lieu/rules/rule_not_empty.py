def rule_not_empty(field: str, label: str = None):
    if label is None:
        label = field

    def _rule(data: dict):
        val = data.get(field)
        if val is None:
            return False, f"{label} không được để trống"
        if isinstance(val, str) and val.strip() == "":
            return False, f"{label} không được để trống"
        return True, ""

    return _rule
