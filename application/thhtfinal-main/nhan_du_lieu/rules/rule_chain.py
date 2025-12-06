class RuleChain:
    def __init__(self, rules):
        self.rules = rules or []

    def validate(self, data: dict):
        for rule in self.rules:
            ok, reason = rule(data)
            if not ok:
                return False, reason
        return True, ""
