package com.huahetai.arithmetic;

import java.util.Objects;

public final class BinaryExpression implements Expression {
    private final Expression left;
    private final Operator operator;
    private final Expression right;
    private final Rational value;
    private final int operatorCount;
    private final String canonicalKey;

    public BinaryExpression(Expression left, Operator operator, Expression right) {
        this.left = Objects.requireNonNull(left, "left");
        this.operator = Objects.requireNonNull(operator, "operator");
        this.right = Objects.requireNonNull(right, "right");
        this.value = switch (operator) {
            case ADD -> left.value().add(right.value());
            case SUBTRACT -> left.value().subtract(right.value());
            case MULTIPLY -> left.value().multiply(right.value());
            case DIVIDE -> left.value().divide(right.value());
        };
        this.operatorCount = left.operatorCount() + right.operatorCount() + 1;
        String leftKey = left.canonicalKey();
        String rightKey = right.canonicalKey();
        if (operator.commutative() && leftKey.compareTo(rightKey) > 0) {
            String temporary = leftKey; leftKey = rightKey; rightKey = temporary;
        }
        this.canonicalKey = operator.name() + "(" + leftKey + "," + rightKey + ")";
    }

    public Expression left() { return left; }
    public Operator operator() { return operator; }
    public Expression right() { return right; }
    @Override public Rational value() { return value; }
    @Override public int operatorCount() { return operatorCount; }
    @Override public int precedence() { return operator.precedence(); }
    @Override public String canonicalKey() { return canonicalKey; }

    @Override public String render() {
        return renderChild(left, false) + " " + operator.symbol() + " " + renderChild(right, true);
    }

    private String renderChild(Expression child, boolean rightChild) {
        String rendered = child.render();
        boolean parentheses = child.precedence() < precedence() || (rightChild && child.precedence() == precedence());
        return parentheses ? "(" + rendered + ")" : rendered;
    }
}
