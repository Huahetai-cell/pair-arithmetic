package com.huahetai.arithmetic;

import java.util.List;

public record GradeResult(List<Integer> correct, List<Integer> wrong) {
    public GradeResult { correct = List.copyOf(correct); wrong = List.copyOf(wrong); }
    public String format() {
        return line("Correct", correct) + System.lineSeparator() + line("Wrong", wrong) + System.lineSeparator();
    }
    private static String line(String label, List<Integer> numbers) {
        return label + ": " + numbers.size() + " (" + numbers.stream().map(String::valueOf)
                .reduce((a, b) -> a + ", " + b).orElse("") + ")";
    }
}

