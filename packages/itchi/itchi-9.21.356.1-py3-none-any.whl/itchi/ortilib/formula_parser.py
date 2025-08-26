from .formula_scanner import Token, TokenType
from .formula_scanner import UNARY_OPERATORS, CONSTANTS
from typing import Optional
import logging


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def warning(self, message: str):
        token = self.peek()
        m = f"Token '{token.lexeme}' in col {token.column}: {message}"
        logging.warning(m)

    def error(self, message: str):
        token = self.peek()
        m = f"Token '{token.lexeme}' in col {token.column}: {message}"
        logging.error(m)
        raise SyntaxError(m)

    def check(self, token_type: TokenType) -> bool:
        return self.peek().type == token_type

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def peek_next(self) -> Token:
        return self.tokens[self.current + 1]

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

    def match_any(self, token_types: list[TokenType]) -> Optional[Token]:
        for token_type in token_types:
            if (m := self.match(token_type)) is not None:
                return m
        return None

    def consume(self, token_type: TokenType, message: str = "") -> Token:
        token = self.match(token_type)
        if token is None:
            m = message if message else f"Expected '{token_type}'."
            self.error(m)
        assert token is not None
        return token

    def parse(self) -> dict:
        return self.p_formula()

    def p_formula(self) -> dict:
        if self.match(TokenType.QUOTATION):
            result = self.p_expression()
            self.consume(TokenType.QUOTATION)
        else:
            result = self.p_expression()
        self.consume(TokenType.EOF)
        return result

    def p_expression(self) -> dict:
        exp1 = self.p_logical_or_expression()
        if self.match(TokenType.TERNARY):
            expression_true = self.p_expression()
            self.consume(TokenType.COLON, "Expected ':' for ternary expression.")
            expression_false = self.p_expression()
            return {
                "type": "ternary",
                "condition": exp1,
                "expression_true": expression_true,
                "expression_false": expression_false,
            }
        else:
            return exp1

    def create_binary_expression(self, exp1, token_type, exp2):
        return {
            "type": token_type,
            "expression_1": exp1,
            "expression_2": exp2,
        }

    def p_logical_or_expression(self):
        exp1 = self.p_logical_and_expression()
        if token := self.match(TokenType.LOR):
            exp2 = self.p_logical_or_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_logical_and_expression(self):
        exp1 = self.p_inclusive_or_expression()
        if token := self.match(TokenType.LAND):
            exp2 = self.p_logical_and_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_inclusive_or_expression(self):
        exp1 = self.p_exclusive_or_expression()
        if token := self.match(TokenType.OR):
            exp2 = self.p_inclusive_or_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_exclusive_or_expression(self):
        exp1 = self.p_and_expression()
        if token := self.match(TokenType.XOR):
            exp2 = self.p_exclusive_or_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_and_expression(self):
        exp1 = self.p_equality_expression()
        if token := self.match(TokenType.AND):
            exp2 = self.p_and_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_equality_expression(self):
        exp1 = self.p_relational_expression()
        if token := self.match_any([TokenType.EQ, TokenType.NE]):
            exp2 = self.p_equality_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_relational_expression(self):
        exp1 = self.p_shift_expression()
        if token := self.match_any([TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE]):
            exp2 = self.p_relational_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_shift_expression(self):
        exp1 = self.p_additive_expression()
        if token := self.match_any([TokenType.LSHIFT, TokenType.RSHIFT]):
            exp2 = self.p_shift_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_additive_expression(self):
        exp1 = self.p_multiplicative_expression()
        if token := self.match_any([TokenType.PLUS, TokenType.MINUS]):
            exp2 = self.p_additive_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_multiplicative_expression(self):
        exp1 = self.p_cast_expression()
        if token := self.match_any([TokenType.TIMES, TokenType.DIVIDE, TokenType.MODULO]):
            exp2 = self.p_multiplicative_expression()
            return self.create_binary_expression(exp1, token.lexeme, exp2)
        return exp1

    def p_cast_expression(self):
        if self.peek().type == TokenType.LPAREN and self.peek_next().type == TokenType.SPECIFIER:
            self.consume(TokenType.LPAREN)
            type_name = self.p_type_name()
            self.consume(TokenType.RPAREN, "Expected closing ')' for type cast.")
            exp = self.p_unary_expression()
            return {"type": "cast", "name": type_name, "expression": exp}
        return self.p_unary_expression()

    def p_type_name(self) -> str:
        type_specifiers = []
        while self.peek().type == TokenType.SPECIFIER:
            specifier = str(self.advance().literal)
            type_specifiers.append(specifier)
        if len(type_specifiers) == 0:
            self.warning("Expected at least one specifier.")
            type_specifiers.append("none")
        if token := self.match(TokenType.TIMES):
            type_specifiers.append(str(token.type))
        return " ".join(type_specifiers)

    def p_unary_expression(self):
        if self.match(TokenType.SIZEOF):
            if self.match(TokenType.LPAREN):
                type_name = self.p_type_name()
                self.consume(TokenType.RPAREN, "Expected ')' after sizeof type.")
                return f"sizeof({type_name})"
            else:
                expr = self.p_unary_expression()
                return f"sizeof({expr})"
        elif token := self.match_any(UNARY_OPERATORS):
            expr = self.p_cast_expression()
            if token.type == TokenType.MINUS:
                try:
                    return -expr
                except TypeError:
                    pass
            elif token.type == TokenType.PLUS:
                try:
                    return +expr
                except TypeError:
                    pass
            elif token.type == TokenType.NOT:
                try:
                    return ~expr
                except TypeError:
                    pass
            if not type(expr) is str:
                self.error("Unary operator not supported for non-basic expression.")
            return token.lexeme + expr
        return self.p_postfix_expression()

    def p_postfix_expression(self):
        expr = self.p_primary_expression()
        while token := self.match_any([TokenType.LBRACKET, TokenType.PERIOD, TokenType.ARROW]):
            if not type(expr) is str:
                self.error("Access not supported for complex expressions.")
            expr += token.lexeme
            match token.type:
                case TokenType.LBRACKET:
                    expr += str(
                        self.consume(
                            TokenType.INTEGER, "Expected integer for array access."
                        ).literal
                    )
                    expr += self.consume(TokenType.RBRACKET).lexeme
                case TokenType.PERIOD | TokenType.ARROW:
                    expr += self.consume(TokenType.ID).lexeme
        return expr

    def p_primary_expression(self):
        if token := self.match(TokenType.ID):
            return token.lexeme
        elif self.match(TokenType.LPAREN):
            expr = self.p_expression()
            self.consume(TokenType.RPAREN, "Expected ')' at end of expression.")
            return expr
        else:
            return self.p_constant()

    def p_constant(self):
        if token := self.match_any(CONSTANTS):
            return token.literal
        self.error("Expected a constant.")
