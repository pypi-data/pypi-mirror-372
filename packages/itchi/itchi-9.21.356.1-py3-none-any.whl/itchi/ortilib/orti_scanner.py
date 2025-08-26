from dataclasses import dataclass
from typing import Any, Optional, List
from enum import Enum, auto

class TokenType(Enum):
    ID = auto()
    INTEGER = auto() 
    INTEGER_HEX = auto()
    INTEGER_OCT = auto()
    STRING = auto()
    CHARACTER = auto()
    EQUALS = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMI = auto()
    COLON = auto()
    EOF = auto()

    # koil_identifiers
    VERSION = auto()
    KOIL = auto()
    OSSEMANTICS = auto()
    IMPLEMENTATION = auto()
    TOTRACE = auto()
    CTYPE_ID = auto()
    ENUM_ID = auto() 
    STRING_ID = auto()
    
KOIL_IDENTIFIERS = {
    'VERSION': TokenType.VERSION,
    'KOIL': TokenType.KOIL,
    'OSSEMANTICS': TokenType.OSSEMANTICS,
    'IMPLEMENTATION': TokenType.IMPLEMENTATION,
    'TOTRACE': TokenType.TOTRACE,
    'CTYPE': TokenType.CTYPE_ID,
    'ENUM': TokenType.ENUM_ID,
    'STRING': TokenType.STRING_ID,
}

ESCAPE_PAIRS = {"\\\\": "\\",
                "\\\"": '"'}

@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Optional[Any]
    line: int

    def __str__(self) -> str:
        literal = self.literal if self.literal is not None else ""
        return f"{self.type} {self.lexeme} {literal}"
    
    def literal_as_str(self) -> str:
        if type(self.literal) is str:
            return self.literal
        return str(self.type)
    
    def literal_as_int(self) -> int:
        if type(self.literal) is int:
            return self.literal
        return 0

class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.has_error = False
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        
    def at_end(self) -> bool:
        return self.current >= len(self.source)
        
    def scan_tokens(self) -> List[Token]:
        while not self.at_end():
            self.start = self.current
            self.scan_token()
        last_token = Token(TokenType.EOF, "", None, self.line)
        self.tokens.append(last_token)
        return self.tokens
    
    def scan_token(self):
        c = self.advance()
        match c:
            case '[': self.add_token(TokenType.LBRACKET)
            case ']': self.add_token(TokenType.RBRACKET)
            case '{': self.add_token(TokenType.LBRACE)
            case '}': self.add_token(TokenType.RBRACE)
            case ',': self.add_token(TokenType.COMMA)
            case ';': self.add_token(TokenType.SEMI)
            case ':': self.add_token(TokenType.COLON)
            case '=': self.add_token(TokenType.EQUALS)
            case '\n': self.new_line()
            case ' ' | '\r' | '\t': pass  # Ignore whitespace
            case '0':
                if self.match('x'):
                    self.scan_integer_hex()
                elif self.peek().isdigit():
                    self.scan_integer_oct()
                else:
                    self.scan_integer_dec()
            case "L" if self.peek() == "'":
                assert self.advance() == "'"
                self.scan_character()
            case _ if c.isdigit():
                self.scan_integer_dec()
            case _ if c.isalpha() or c == "_":
                self.scan_id()
            case '"':
                self.scan_string()
            case "'":
                self.scan_character()
            case '/' if self.match('/'):
                self.skip_cpp_style_comment()
            case '/' if self.match('*'):
                self.skip_c_style_comment()
            case _:
                self.error(f"Unexpected character: {c}")
            
    def skip_cpp_style_comment(self):
        while self.peek() != '\n' and not self.at_end():
            self.advance()

    def skip_c_style_comment(self):
        nesting_level = 0
        while not self.at_end():
            c = self.advance()
            match c:
                case '/' if self.match("*"):
                        nesting_level += 1
                case '*' if self.match("/"):
                    if nesting_level == 0:
                        return
                    nesting_level -= 1
                case '\n':
                    self.new_line()
        self.error("Unterminated C-style comment")
                    
    def new_line(self):
        self.line += 1
        self.column = 1
                    
    def scan_id(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        text = self.source[self.start:self.current]
        token_type = KOIL_IDENTIFIERS.get(text, TokenType.ID)
        self.add_token(token_type, text)

    def is_hex_digit(self, c: str) -> bool:
        return c.isdigit() or 'a' <= c.lower() <= 'f'

    def scan_integer_hex(self):
        while self.is_hex_digit(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        try:
            value = int(text[2:], 16)
            self.add_token(TokenType.INTEGER_HEX, value)
        except ValueError:
            self.error(f"Invalid hex literal: {text}")
        
    def is_oct_digit(self, c: str) -> bool:
        return '0' <= c <= '7'

    def scan_integer_oct(self):
        while self.is_oct_digit(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        try:
            value = int(text[1:], 8)
            self.add_token(TokenType.INTEGER_OCT, value)
        except ValueError:
            self.error(f"Invalid octal literal: {text}")

    def scan_integer_dec(self):
        while self.peek().isdigit():
            self.advance()

        INTEGER_SUFFIXES = "uUlL"
        while self.peek() in INTEGER_SUFFIXES:
            self.advance()

        text = self.source[self.start:self.current]
        try:
            value = int(text.rstrip(INTEGER_SUFFIXES))
            self.add_token(TokenType.INTEGER, value)
        except ValueError:
            self.error(f"Invalid integer literal: {text}")
                
    def scan_string(self):
        while self.peek() != '"' and not self.at_end():
            c = self.advance()
            if c == "\n":
                self.new_line()
            if c == "\\":
                if not self.at_end():
                    escape_sequence = c + self.advance()
                    if not escape_sequence in ESCAPE_PAIRS:
                        self.error(f"Unexpected escape sequence '{escape_sequence}'.")
                        return
                else:
                    self.error("Unfinished escape sequence.")
                    return

        if self.at_end():
            self.error("Unterminated string.")
            return

        assert self.advance() == '"'
        text = self.source[self.start + 1:self.current - 1]
        for old, new in ESCAPE_PAIRS.items():
            text = text.replace(old, new)
        self.add_token(TokenType.STRING, text)

    def scan_character(self):
        if self.peek() == "\\":
            c = self.advance()
            if not self.at_end():
                escape_sequence = c + self.advance()
                if not escape_sequence in ESCAPE_PAIRS:
                    self.error(f"Unexpected escape sequence '{escape_sequence}'.")
                    return
            else:
                self.error("Unfinished escape sequence.")
                return
        elif self.peek() != "'":
            self.advance()
        else:
            self.advance()
            self.error("Empty character sequence.")
            return
        
        if not self.peek() == "'":
            self.error("Unterminated character sequence.")
            return
            
        assert self.advance() == "'"
        text = self.source[self.start:self.current].replace("L'", "'")[1:-1]
        for old, new in ESCAPE_PAIRS.items():
            text = text.replace(old, new)
        self.add_token(TokenType.CHARACTER, text)

    def advance(self) -> str:
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]
    
    def peek(self) -> str:
        if self.at_end():
            return '\0'
        return self.source[self.current]
    
    def match(self, expected: str) -> bool:
        if self.at_end() or self.source[self.current] != expected:
            return False
        self.advance()
        return True

    def add_token(self, type: TokenType, literal: Any = None):
        text = self.source[self.start:self.current]
        token = Token(type, text, literal, self.line)
        self.tokens.append(token)

    def error(self, message: str):
        print(f"Line {self.line} col {self.column - 1}: {message}")
        self.has_error = True
