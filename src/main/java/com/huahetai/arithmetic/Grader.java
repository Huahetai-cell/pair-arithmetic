package com.huahetai.arithmetic;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class Grader {
    private static final Pattern EXERCISE = Pattern.compile("^\\s*(\\d+)\\.\\s*(.*?)\\s*=\\s*$");
    private static final Pattern ANSWER = Pattern.compile("^\\s*(\\d+)\\)\\s*(.*?)\\s*$");
    private final ExpressionParser parser = new ExpressionParser();

    public GradeResult grade(Path exerciseFile, Path answerFile) throws IOException {
        Map<Integer, String> answers = parseNumberedLines(answerFile, ANSWER);
        List<Integer> correct = new ArrayList<>();
        List<Integer> wrong = new ArrayList<>();
        for (String line : Files.readAllLines(exerciseFile, StandardCharsets.UTF_8)) {
            if (line.isBlank()) continue;
            Matcher matcher = EXERCISE.matcher(line);
            if (!matcher.matches()) throw new IllegalArgumentException("invalid exercise line: " + line);
            int number = Integer.parseInt(matcher.group(1));
            String supplied = answers.get(number);
            try {
                Rational expected = parser.parse(matcher.group(2)).value();
                if (supplied != null && expected.equals(Rational.parse(supplied))) correct.add(number);
                else wrong.add(number);
            } catch (RuntimeException exception) {
                wrong.add(number);
            }
        }
        return new GradeResult(correct, wrong);
    }

    private Map<Integer, String> parseNumberedLines(Path file, Pattern pattern) throws IOException {
        Map<Integer, String> result = new HashMap<>();
        for (String line : Files.readAllLines(file, StandardCharsets.UTF_8)) {
            if (line.isBlank()) continue;
            Matcher matcher = pattern.matcher(line);
            if (matcher.matches()) result.put(Integer.parseInt(matcher.group(1)), matcher.group(2).trim());
        }
        return result;
    }
}
