from dataclasses import dataclass
from typing import Any, Optional, List
from enum import Enum, auto


class TokenType(Enum):
    # Identifiers and literals
    ID = auto()
    INTEGER = auto()
    INTEGER_HEX = auto()
    INTEGER_OCT = auto()
    FLOAT = auto()
    CHARACTER = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    MODULO = auto()
    OR = auto()
    AND = auto()
    NOT = auto()
    XOR = auto()
    LSHIFT = auto()
    RSHIFT = auto()
    LOR = auto()
    LAND = auto()
    LNOT = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    EQ = auto()
    NE = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    PERIOD = auto()
    COLON = auto()
    QUOTATION = auto()

    SPECIFIER = auto()
    SIZEOF = auto()
    ARROW = auto()
    TERNARY = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Optional[Any]
    column: int

    def __str__(self) -> str:
        literal = self.literal if self.literal is not None else ""
        return f"{self.type} {self.lexeme} {literal}"


KEYWORDS = {
    "sizeof": TokenType.SIZEOF,
}

SPECIFIERS = {"void", "char", "short", "int", "long", "float", "double", "signed", "unsigned"}


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.has_error = False
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def scan_tokens(self) -> List[Token]:
        while not self.at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, len(self.source)))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        match c:
            case "(":
                self.add_token(TokenType.LPAREN)
            case ")":
                self.add_token(TokenType.RPAREN)
            case "[":
                self.add_token(TokenType.LBRACKET)
            case "]":
                self.add_token(TokenType.RBRACKET)
            case ".":
                self.add_token(TokenType.PERIOD)
            case ":":
                self.add_token(TokenType.COLON)
            case '"':
                self.add_token(TokenType.QUOTATION)
            case "?":
                self.add_token(TokenType.TERNARY)
            case "+":
                self.add_token(TokenType.PLUS)
            case "-":
                if self.match(">"):
                    self.add_token(TokenType.ARROW)
                else:
                    self.add_token(TokenType.MINUS)
            case "*":
                self.add_token(TokenType.TIMES)
            case "/":
                self.add_token(TokenType.DIVIDE)
            case "%":
                self.add_token(TokenType.MODULO)
            case "~":
                self.add_token(TokenType.NOT)
            case "^":
                self.add_token(TokenType.XOR)

            # Two-character operators
            case "<":
                if self.match("="):
                    self.add_token(TokenType.LE)
                elif self.match("<"):
                    self.add_token(TokenType.LSHIFT)
                else:
                    self.add_token(TokenType.LT)
            case ">":
                if self.match("="):
                    self.add_token(TokenType.GE)
                elif self.match(">"):
                    self.add_token(TokenType.RSHIFT)
                else:
                    self.add_token(TokenType.GT)
            case "=" if self.match("="):
                self.add_token(TokenType.EQ)
            case "!" if self.match("="):
                self.add_token(TokenType.NE)
            case "|":
                if self.match("|"):
                    self.add_token(TokenType.LOR)
                else:
                    self.add_token(TokenType.OR)
            case "&":
                if self.match("&"):
                    self.add_token(TokenType.LAND)
                else:
                    self.add_token(TokenType.AND)

            case "L" if self.match("'"):
                self.scan_character()
            case "'":
                self.scan_character()

            # Whitespaces
            case "\n":
                self.new_line()
            case " " | "\r" | "\t":
                pass  # ignore

            # Numbers
            case "0":
                if self.match("x"):
                    self.scan_integer_hex()
                elif self.peek().isdigit():
                    self.scan_integer_oct()
                else:
                    self.scan_number()
            case c if c.isdigit():
                self.scan_number()
            case c if c.isalpha() or c == "_":
                self.scan_id()
            case _:
                self.error(f"Unexpected character: {c}")

    def scan_id(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        text = self.source[self.start : self.current]
        if text in SPECIFIERS:
            self.add_token(TokenType.SPECIFIER, text)
        else:
            token_type = KEYWORDS.get(text, TokenType.ID)
            self.add_token(token_type, text)

    def scan_character(self):
        value = ""
        while self.peek() != "'" and not self.at_end():
            if self.peek() == "\\":
                self.advance()  # Skip backslash
                value += self.handle_escape()
            else:
                value += self.advance()

        if self.at_end():
            self.error("Unterminated character literal")
            return

        self.advance()  # Skip closing quote
        if len(value) != 1:
            self.error("Invalid character literal")
            return

        self.add_token(TokenType.CHARACTER, ord(value))

    def handle_escape(self) -> str:
        c = self.advance()
        match c:
            case "\\":
                return "\\"
            case "'":
                return "'"
            case '"':
                return '"'
            case _:
                self.error(f"Invalid escape sequence: \\{c}")
                return ""

    def scan_float(self):
        if self.match("."):
            while self.peek().isdigit():
                self.advance()

        if self.match("e"):
            if self.peek() in "+-":
                self.advance()
            while self.peek().isdigit():
                self.advance()

        FLOAT_SUFFIXES = "fFlL"
        if self.peek() in FLOAT_SUFFIXES:
            self.advance()

        text = self.source[self.start : self.current]
        try:
            value = float(text.rstrip(FLOAT_SUFFIXES))
            self.add_token(TokenType.FLOAT, value)
        except ValueError:
            self.error(f"Invalid float literal: {text}")
        return

    def scan_integer_dec(self):
        while self.peek().isdigit():
            self.advance()

        INTEGER_SUFFIXES = "uUlL"
        while self.peek() in INTEGER_SUFFIXES:
            self.advance()

        text = self.source[self.start : self.current]
        if self.peek() == "]":
            # This is a workaround to maintain compatibility with the previous PLY-based
            # ORTI parser. ETAS uses type specifier suffixes for array indices. Stripping
            # these suffixes prevents the Inspectors logic from matching the running task
            # variable. An alternative would be to parse the running task variable as a
            # formula before providing it to FormulaResolver. This workaround can be
            # removed once `inspectors` has been removed.
            self.add_token(TokenType.INTEGER, text)
        else:
            try:
                value = int(text.rstrip(INTEGER_SUFFIXES))
                self.add_token(TokenType.INTEGER, value)
            except ValueError:
                self.error(f"Invalid integer literal: {text}")

    def scan_number(self):
        # Get integer part.
        while self.peek().isdigit():
            self.advance()

        # If the number has a fractional or exponential part,
        # parse it as a float. Otherwise, as an integer.
        if self.peek() == "." and self.peek_next().isdigit():
            self.scan_float()
        elif self.peek() == "e":
            self.scan_float()
        else:
            self.scan_integer_dec()

    def is_hex_digit(self, c: str) -> bool:
        return c.isdigit() or "a" <= c.lower() <= "f"

    def scan_integer_hex(self):
        while self.is_hex_digit(self.peek()):
            self.advance()

        text = self.source[self.start : self.current]
        try:
            value = int(text[2:], 16)
            self.add_token(TokenType.INTEGER_HEX, value)
        except ValueError:
            self.error(f"Invalid hex literal: {text}")

    def is_oct_digit(self, c: str) -> bool:
        return "0" <= c <= "7"

    def scan_integer_oct(self):
        while self.is_oct_digit(self.peek()):
            self.advance()

        text = self.source[self.start : self.current]
        try:
            value = int(text[1:], 8)
            self.add_token(TokenType.INTEGER_OCT, value)
        except ValueError:
            self.error(f"Invalid octal literal: {text}")

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]

    def peek(self) -> str:
        if self.at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.at_end() or self.source[self.current] != expected:
            return False
        self.advance()
        return True

    def new_line(self):
        self.line += 1
        self.column = 1

    def add_token(self, type: TokenType, literal: Any = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.start))

    def error(self, message: str):
        print(f"Line {self.line} col {self.column}: {message}")
        self.has_error = True


UNARY_OPERATORS = [
    TokenType.AND,
    TokenType.TIMES,
    TokenType.PLUS,
    TokenType.MINUS,
    TokenType.NOT,
    TokenType.LNOT,
]

CONSTANTS = [
    TokenType.INTEGER,
    TokenType.INTEGER_HEX,
    TokenType.INTEGER_OCT,
    TokenType.FLOAT,
    TokenType.CHARACTER,
]
