package com.huahetai.arithmetic;

/** Recursive-descent parser for the exercise grammar. */
public final class ExpressionParser {
    private String input;
    private int position;

    public Expression parse(String source) {
        input = source.trim();
        if (input.endsWith("=")) input = input.substring(0, input.length() - 1).trim();
        position = 0;
        Expression result = parseAdditive();
        skipSpaces();
        if (position != input.length()) throw error("unexpected character '" + input.charAt(position) + "'");
        return result;
    }

    private Expression parseAdditive() {
        Expression expression = parseMultiplicative();
        while (true) {
            skipSpaces();
            if (take('+')) expression = new BinaryExpression(expression, Operator.ADD, parseMultiplicative());
            else if (take('-') || take('−')) expression = new BinaryExpression(expression, Operator.SUBTRACT, parseMultiplicative());
            else return expression;
        }
    }

    private Expression parseMultiplicative() {
        Expression expression = parsePrimary();
        while (true) {
            skipSpaces();
            if (take('*') || take('×')) expression = new BinaryExpression(expression, Operator.MULTIPLY, parsePrimary());
            else if (take('÷')) expression = new BinaryExpression(expression, Operator.DIVIDE, parsePrimary());
            else if (isAsciiDivision()) {
                position++;
                expression = new BinaryExpression(expression, Operator.DIVIDE, parsePrimary());
            } else return expression;
        }
    }

    private Expression parsePrimary() {
        skipSpaces();
        if (take('(')) {
            Expression expression = parseAdditive();
            skipSpaces();
            if (!take(')')) throw error("missing ')'");
            return expression;
        }
        int start = position;
        while (position < input.length() && Character.isDigit(input.charAt(position))) position++;
        if (start == position) throw error("number expected");
        if (position < input.length() && (input.charAt(position) == '\'' || input.charAt(position) == '’')) {
            position++;
            readDigits();
            if (!take('/')) throw error("'/' expected in mixed fraction");
            readDigits();
        } else if (position < input.length() && input.charAt(position) == '/' &&
                position + 1 < input.length() && Character.isDigit(input.charAt(position + 1))) {
            position++;
            readDigits();
        }
        return new NumberExpression(Rational.parse(input.substring(start, position)));
    }

    private void readDigits() {
        int start = position;
        while (position < input.length() && Character.isDigit(input.charAt(position))) position++;
        if (start == position) throw error("digits expected");
    }

    private boolean isAsciiDivision() {
        return position < input.length() && input.charAt(position) == '/';
    }

    private boolean take(char expected) {
        if (position < input.length() && input.charAt(position) == expected) {
            position++;
            return true;
        }
        return false;
    }

    private void skipSpaces() {
        while (position < input.length() && Character.isWhitespace(input.charAt(position))) position++;
    }

    private IllegalArgumentException error(String message) {
        return new IllegalArgumentException(message + " at position " + position + " in: " + input);
    }
}

