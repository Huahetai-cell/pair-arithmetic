package com.huahetai.arithmetic;

public sealed interface Expression permits NumberExpression, BinaryExpression {
    Rational value();
    int operatorCount();
    int precedence();
    String canonicalKey();
    String render();
}

