import logging
from .orti_scanner import Token, TokenType
from typing import Optional, Any, Union
from pydantic import BaseModel


class OrtiEnum(BaseModel):
    desc: str
    const: Union[int, str, None] = None
    formula: Optional[str] = None


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def warning(self, message: str):
        token = self.peek()
        m = f"Token '{token.lexeme}' in line {token.line}: {message}"
        logging.warning(m)

    def error(self, message: str):
        token = self.peek()
        m = f"Token '{token.lexeme}' in line {token.line}: {message}"
        logging.error(m)
        raise SyntaxError(m)

    def check(self, token_type: TokenType) -> bool:
        return self.peek().type == token_type

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def advance(self) -> Token:
        token = self.peek()
        if not self.at_end():
            self.current += 1
        return token

    def at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def match(self, token_type: TokenType) -> Optional[Token]:
        if self.peek().type == token_type:
            return self.advance()
        return None

    def consume(self, token_type: TokenType, message: str = "") -> Token:
        token = self.match(token_type)
        if token is None:
            m = message if message else f"Expected '{token_type}'."
            self.error(m)
        assert token is not None
        return token

    def parse(self) -> dict:
        return self.p_file()

    def p_file(self) -> dict:
        d = {
            "version_section": self.p_version_section(),
            "declaration_section": self.p_declaration_section(),
            "information_section": self.p_information_section(),
        }
        self.consume(TokenType.EOF, "Expected end of file.")
        return d

    def p_information_section(self) -> list[dict]:
        object_defs = []
        while True:
            if self.peek().type == TokenType.ID:
                object_defs.append(self.p_object_def())
            else:
                break
        return object_defs

    def p_version_section(self) -> dict:
        self.consume(TokenType.VERSION, "ORTI must start with VERSION.")
        self.consume(TokenType.LBRACE)
        d = {
            "koil_version": self.p_koil_version(),
            "kernel_version": self.p_kernel_version(),
        }
        self.consume(TokenType.RBRACE)
        self.consume(TokenType.SEMI)
        return d

    def p_koil_version(self) -> str:
        self.consume(TokenType.KOIL, "KOIL version must start with KOIL.")
        self.consume(TokenType.EQUALS)
        s = self.p_string("KOIL version must be string.")
        self.consume(TokenType.SEMI)
        return s

    def p_kernel_version(self) -> dict:
        self.consume(TokenType.OSSEMANTICS, "KERNEL version must start with OSSEMANTICS.")
        self.consume(TokenType.EQUALS)
        semantics_name = self.p_string("Semantics name must be a string.")
        self.consume(TokenType.COMMA, "Expected ',' after semantics name.")
        semantics_version = self.p_string("Semantics version must be a string.")
        self.consume(TokenType.SEMI)
        return {
            "semantics_name": semantics_name,
            "semantics_version": semantics_version,
        }

    def p_declaration_section(self) -> dict:
        self.consume(
            TokenType.IMPLEMENTATION,
            "Declaration section must start with IMPLEMENTATION.",
        )
        implementation_name = self.consume(
            TokenType.ID, "Implementation name must be an ID."
        ).literal
        self.consume(TokenType.LBRACE)
        declaration_specs = self.p_declaration_specs()
        self.consume(TokenType.RBRACE)
        self.consume(TokenType.SEMI)

        return {
            "implementation_name": implementation_name,
            "declaration_specs": declaration_specs,
        }

    def p_declaration_specs(self) -> list[dict]:
        declaration_specs = []
        while True:
            if self.peek().type == TokenType.RBRACE:
                break
            declaration_specs.append(self.p_declaration_spec())
        return declaration_specs

    def p_declaration_spec(self) -> dict:
        object_type = self.p_object_type()
        self.consume(TokenType.LBRACE)
        attribute_decls = self.p_attribute_decls()
        self.consume(TokenType.RBRACE)
        if self.match(TokenType.COMMA):
            type_description = self.p_string("Type description must be string.")
        else:
            type_description = ""
        self.consume(TokenType.SEMI)
        return {
            "object_type": object_type,
            "attribute_decls": attribute_decls,
            "type_description": type_description,
        }

    def p_object_type(self) -> str:
        s = self.consume(TokenType.ID).literal_as_str()
        return s

    def p_attribute_decls(self) -> list[dict]:
        attribute_decls = []
        while True:
            if self.peek().type == TokenType.RBRACE:
                break
            attribute_decls.append(self.p_attribute_decl())
        return attribute_decls

    def p_attribute_decl(self) -> dict:
        totrace = True if self.match(TokenType.TOTRACE) else False
        attribute_type = self.p_attribute_type()
        attribute_name = self.p_attribute_name()

        if self.match(TokenType.COMMA):
            attribute_description = self.p_string("Attribute description must be string.")
        else:
            attribute_description = ""
        self.consume(TokenType.SEMI)

        return {
            "totrace": totrace,
            "attribute_type": attribute_type,
            "attribute_name": attribute_name,
            "attribute_description": attribute_description,
        }

    def p_attribute_type(self) -> Any:
        if self.peek().type == TokenType.CTYPE_ID:
            return self.p_c_type()

        if self.peek().type == TokenType.ENUM_ID:
            return self.p_enum_type()

        if self.peek().type == TokenType.STRING_ID:
            return self.consume(TokenType.STRING_ID).literal_as_str()

        self.error("Expected CTYPE, ENUM, or STRING ID for attribute type.")
        return None

    def p_c_type(self) -> str:
        s = self.consume(TokenType.CTYPE_ID).literal_as_str()
        if self.peek().type == TokenType.STRING:
            s = self.p_string()
        return s

    def p_enum_type(self) -> dict:
        attribute_type = self.consume(TokenType.ENUM_ID).literal_as_str()
        if self.peek().type == TokenType.STRING:
            attribute_type += self.p_string()
        self.consume(TokenType.LBRACKET)
        enum_elements = self.p_enum_elements()
        self.consume(TokenType.RBRACKET)

        return {"type": attribute_type, "enum_elements": enum_elements}

    def p_enum_elements(self) -> list[OrtiEnum]:
        enum_elements = [self.p_enum_element()]
        while True:
            if self.match(TokenType.COMMA):
                if self.peek().type == TokenType.RBRACKET:
                    self.warning("Illegal trailing comma before this token.")
                    break
                enum_elements.append(self.p_enum_element())
            else:
                break
        return enum_elements

    def p_enum_element(self) -> OrtiEnum:
        desc = self.p_string()
        if self.match(TokenType.COLON):
            id = self.consume(TokenType.ID).literal_as_str()
            desc += f" (links to {id})"
        self.consume(TokenType.EQUALS)
        const = None
        formula = None
        match self.peek().type:
            case TokenType.STRING:
                formula = self.p_string()
            case TokenType.INTEGER:
                const = self.consume(TokenType.INTEGER).literal_as_int()
            case TokenType.INTEGER_HEX:
                const = self.consume(TokenType.INTEGER_HEX).literal_as_int()
            case TokenType.INTEGER_OCT:
                const = self.consume(TokenType.INTEGER_OCT).literal_as_int()
            case TokenType.CHARACTER:
                const = self.consume(TokenType.CHARACTER).literal
            case _:
                self.error("Enum must be a constant or formula.")

        return OrtiEnum(
            desc=desc,
            const=const,
            formula=formula,
        )

    def p_attribute_name(self) -> str:
        token = self.consume(TokenType.ID, "Attribute name must start with an ID.")
        s = token.literal
        assert type(s) is str
        if self.match(TokenType.LBRACKET):
            self.consume(TokenType.RBRACKET, "SMP section must be closed with ']'.")
            s += "[]"
        return s

    def p_object_def(self) -> dict:
        object_type = self.consume(TokenType.ID, "Object type must be an ID.").literal_as_str()
        object_name = self.consume(TokenType.ID, "Object name must be an ID.").literal_as_str()
        self.consume(TokenType.LBRACE)
        attributes = []
        while True:
            if self.match(TokenType.RBRACE):
                break
            attributes.append(self.p_attribute_def())
        self.consume(TokenType.SEMI)
        return {
            "object_type": object_type,
            "object_name": object_name,
            "attributes": attributes,
        }

    def p_attribute_def(self) -> dict:
        attribute_name = self.consume(
            TokenType.ID, "Attribute def must start with ID."
        ).literal_as_str()
        if self.match(TokenType.LBRACKET):
            value = self.consume(TokenType.INTEGER, "SMP ID must be integer.").literal_as_int()
            self.consume(TokenType.RBRACKET, "SMP section must close with ']'.")
            attribute_name += f"[{value}]"
        self.consume(TokenType.EQUALS)
        formula = self.p_string("Formula must be string.")
        self.consume(TokenType.SEMI)
        return {"attribute_name": attribute_name, "formula": formula}

    def p_string(self, message: str = "") -> str:
        s = self.consume(TokenType.STRING, message).literal_as_str()
        while self.peek().type == TokenType.STRING:
            s += self.consume(TokenType.STRING).literal_as_str()
        return s
