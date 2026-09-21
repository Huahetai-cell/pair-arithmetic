package com.huahetai.arithmetic;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

public final class ExerciseGenerator {
    @FunctionalInterface
    public interface KeyStrategy { String key(Expression expression); }

    public GenerationResult generate(int count, int range, long seed) {
        return generate(count, range, seed, Expression::canonicalKey);
    }

    /** Public overload used by the reproducible performance harness. */
    public GenerationResult generate(int count, int range, long seed, KeyStrategy keyStrategy) {
        if (count <= 0) throw new IllegalArgumentException("exercise count must be positive");
        if (range <= 0) throw new IllegalArgumentException("range must be positive");
        Random random = new Random(seed);
        GenerationStats stats = new GenerationStats();
        List<Expression> exercises = new ArrayList<>(count);
        Set<String> seen = new HashSet<>(Math.max(16, count * 2));
        long maximumAttempts = Math.max(20_000L, count * 2_000L);
        while (exercises.size() < count && stats.candidateCount() < maximumAttempts) {
            stats.candidate();
            Expression candidate = build(random, range, 1 + random.nextInt(3), stats);
            if (candidate == null) continue;
            if (seen.add(keyStrategy.key(candidate))) exercises.add(candidate);
            else stats.duplicate();
        }
        if (exercises.size() != count) {
            throw new IllegalStateException("could generate only " + exercises.size() + " unique exercises after "
                    + maximumAttempts + " attempts; increase -r or reduce -n");
        }
        return new GenerationResult(exercises, stats);
    }

    private Expression build(Random random, int range, int operators, GenerationStats stats) {
        if (operators == 0) return atom(random, range);
        int leftOperators = random.nextInt(operators);
        Expression left = build(random, range, leftOperators, stats);
        Expression right = build(random, range, operators - 1 - leftOperators, stats);
        Operator operator = Operator.values()[random.nextInt(Operator.values().length)];
        if (operator == Operator.SUBTRACT && left.value().compareTo(right.value()) < 0) {
            stats.constraintReject();
            return null;
        }
        if (operator == Operator.DIVIDE && (left.value().isZero() || left.value().compareTo(right.value()) >= 0)) {
            stats.constraintReject();
            return null;
        }
        try {
            BinaryExpression expression = new BinaryExpression(left, operator, right);
            if (operator == Operator.DIVIDE && !expression.value().isProperPositiveFraction()) {
                stats.constraintReject();
                return null;
            }
            return expression;
        } catch (ArithmeticException exception) {
            stats.constraintReject();
            return null;
        }
    }

    private Expression atom(Random random, int range) {
        if (range < 3 || random.nextBoolean()) return new NumberExpression(Rational.of(random.nextInt(range)));
        int denominator = 2 + random.nextInt(range - 2); // denominator is strictly below range
        long bound = (long) range * denominator;
        long numerator = 1 + random.nextLong(bound - 1);
        return new NumberExpression(new Rational(BigInteger.valueOf(numerator), BigInteger.valueOf(denominator)));
    }
}

