package com.huahetai.arithmetic;

import java.util.Objects;

public record NumberExpression(Rational value) implements Expression {
    public NumberExpression { Objects.requireNonNull(value, "value"); }
    @Override public int operatorCount() { return 0; }
    @Override public int precedence() { return 3; }
    @Override public String canonicalKey() { return "N[" + value.numerator() + "/" + value.denominator() + "]"; }
    @Override public String render() { return value.toString(); }
}

