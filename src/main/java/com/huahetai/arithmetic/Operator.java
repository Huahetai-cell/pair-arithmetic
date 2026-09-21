package com.huahetai.arithmetic;

public enum Operator {
    ADD("+", 1), SUBTRACT("−", 1), MULTIPLY("×", 2), DIVIDE("÷", 2);
    private final String symbol;
    private final int precedence;
    Operator(String symbol, int precedence) { this.symbol = symbol; this.precedence = precedence; }
    public String symbol() { return symbol; }
    public int precedence() { return precedence; }
    public boolean commutative() { return this == ADD || this == MULTIPLY; }
}

