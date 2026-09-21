from __future__ import annotations

from .expression import Binary, Expression, Number, Operator, parse_fraction


class ExpressionParser:
    def parse(self, source: str) -> Expression:
        self._text = source.strip()
        if self._text.endswith("="):
            self._text = self._text[:-1].rstrip()
        self._position = 0
        result = self._parse_additive()
        self._skip_spaces()
        if self._position != len(self._text):
            raise self._error(f"unexpected character {self._text[self._position]!r}")
        return result

    def _parse_additive(self) -> Expression:
        expression = self._parse_multiplicative()
        while True:
            self._skip_spaces()
            if self._take("+"):
                expression = Binary(expression, Operator.ADD, self._parse_multiplicative())
            elif self._take("-") or self._take("−"):
                expression = Binary(expression, Operator.SUBTRACT, self._parse_multiplicative())
            else:
                return expression

    def _parse_multiplicative(self) -> Expression:
        expression = self._parse_primary()
        while True:
            self._skip_spaces()
            if self._take("*") or self._take("×"):
                expression = Binary(expression, Operator.MULTIPLY, self._parse_primary())
            elif self._take("÷") or self._ascii_division_here():
                if self._text[self._position - 1] != "÷":
                    self._position += 1
                expression = Binary(expression, Operator.DIVIDE, self._parse_primary())
            else:
                return expression

    def _parse_primary(self) -> Expression:
        self._skip_spaces()
        if self._take("("):
            expression = self._parse_additive()
            self._skip_spaces()
            if not self._take(")"):
                raise self._error("missing ')'")
            return expression
        start = self._position
        self._read_digits()
        if self._peek() in ("'", "’"):
            self._position += 1
            self._read_digits()
            if not self._take("/"):
                raise self._error("'/' expected in mixed fraction")
            self._read_digits()
        elif self._peek() == "/" and self._peek(1).isdigit():
            self._position += 1
            self._read_digits()
        return Number(parse_fraction(self._text[start:self._position]))

    def _ascii_division_here(self) -> bool:
        return self._peek() == "/"

    def _read_digits(self) -> None:
        start = self._position
        while self._peek().isdigit():
            self._position += 1
        if start == self._position:
            raise self._error("number expected")

    def _peek(self, offset: int = 0) -> str:
        index = self._position + offset
        return self._text[index] if index < len(self._text) else ""

    def _take(self, value: str) -> bool:
        if self._peek() == value:
            self._position += 1
            return True
        return False

    def _skip_spaces(self) -> None:
        while self._peek().isspace():
            self._position += 1

    def _error(self, message: str) -> ValueError:
        return ValueError(f"{message} at position {self._position} in: {self._text}")
