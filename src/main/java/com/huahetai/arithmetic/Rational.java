package com.huahetai.arithmetic;

import java.math.BigInteger;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** An immutable, always reduced, non-floating-point rational number. */
public final class Rational implements Comparable<Rational> {
    private static final Pattern TOKEN = Pattern.compile("(\\d+)(?:['’](\\d+)/(\\d+)|/(\\d+))?");
    public static final Rational ZERO = new Rational(BigInteger.ZERO, BigInteger.ONE);
    private final BigInteger numerator;
    private final BigInteger denominator;

    public Rational(BigInteger numerator, BigInteger denominator) {
        Objects.requireNonNull(numerator, "numerator");
        Objects.requireNonNull(denominator, "denominator");
        if (denominator.signum() == 0) throw new ArithmeticException("denominator must not be zero");
        if (denominator.signum() < 0) {
            numerator = numerator.negate();
            denominator = denominator.negate();
        }
        BigInteger gcd = numerator.gcd(denominator);
        this.numerator = numerator.divide(gcd);
        this.denominator = denominator.divide(gcd);
    }

    public static Rational of(long value) {
        return new Rational(BigInteger.valueOf(value), BigInteger.ONE);
    }

    public static Rational of(long numerator, long denominator) {
        return new Rational(BigInteger.valueOf(numerator), BigInteger.valueOf(denominator));
    }

    public static Rational parse(String text) {
        String value = text.trim();
        Matcher matcher = TOKEN.matcher(value);
        if (!matcher.matches()) throw new IllegalArgumentException("invalid number: " + text);
        BigInteger wholeOrNumerator = new BigInteger(matcher.group(1));
        if (matcher.group(2) != null) {
            BigInteger part = new BigInteger(matcher.group(2));
            BigInteger denominator = new BigInteger(matcher.group(3));
            if (part.signum() <= 0 || part.compareTo(denominator) >= 0) {
                throw new IllegalArgumentException("mixed fraction must have a proper fractional part: " + text);
            }
            return new Rational(wholeOrNumerator.multiply(denominator).add(part), denominator);
        }
        if (matcher.group(4) != null) {
            return new Rational(wholeOrNumerator, new BigInteger(matcher.group(4)));
        }
        return new Rational(wholeOrNumerator, BigInteger.ONE);
    }

    public Rational add(Rational other) {
        return new Rational(numerator.multiply(other.denominator).add(other.numerator.multiply(denominator)),
                denominator.multiply(other.denominator));
    }

    public Rational subtract(Rational other) {
        return new Rational(numerator.multiply(other.denominator).subtract(other.numerator.multiply(denominator)),
                denominator.multiply(other.denominator));
    }

    public Rational multiply(Rational other) {
        return new Rational(numerator.multiply(other.numerator), denominator.multiply(other.denominator));
    }

    public Rational divide(Rational other) {
        if (other.isZero()) throw new ArithmeticException("division by zero");
        return new Rational(numerator.multiply(other.denominator), denominator.multiply(other.numerator));
    }

    public boolean isZero() { return numerator.signum() == 0; }
    public boolean isProperPositiveFraction() {
        return numerator.signum() > 0 && numerator.compareTo(denominator) < 0;
    }
    public BigInteger numerator() { return numerator; }
    public BigInteger denominator() { return denominator; }

    @Override public int compareTo(Rational other) {
        return numerator.multiply(other.denominator).compareTo(other.numerator.multiply(denominator));
    }

    @Override public String toString() {
        BigInteger[] parts = numerator.divideAndRemainder(denominator);
        if (parts[1].signum() == 0) return parts[0].toString();
        if (parts[0].signum() == 0) return parts[1] + "/" + denominator;
        return parts[0] + "’" + parts[1].abs() + "/" + denominator;
    }

    @Override public boolean equals(Object object) {
        return object instanceof Rational other && numerator.equals(other.numerator) && denominator.equals(other.denominator);
    }
    @Override public int hashCode() { return Objects.hash(numerator, denominator); }
}

