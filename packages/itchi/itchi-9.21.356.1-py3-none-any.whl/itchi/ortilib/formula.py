from .formula_scanner import Scanner
from .formula_parser import Parser


class Formula(dict):
    def __init__(self, formular_string):
        scanner = Scanner(formular_string)
        tokens = scanner.scan_tokens()
        assert not scanner.has_error, "Failed to scan formula."
        parser = Parser(tokens)
        self.formula = parser.parse()
        self["formula"] = self.formula
