package com.huahetai.arithmetic;

import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class Application {
    private static final String HELP = """
            小学四则运算题目生成器

            用法:
              java -jar Myapp.jar -n <题目数> -r <数值范围>
              java -jar Myapp.jar -e <Exercises.txt> -a <Answers.txt>
              java -jar Myapp.jar -h | --help

            生成模式中的 -n 和 -r 均为必填正整数。
            输出文件写入当前目录：Exercises.txt、Answers.txt 或 Grade.txt。
            """;

    public int run(String[] args, Path workingDirectory, PrintStream out, PrintStream err) {
        try {
            if (args.length == 1 && (args[0].equals("-h") || args[0].equals("--help"))) {
                out.print(HELP);
                return 0;
            }
            Arguments arguments = Arguments.parse(args);
            if (arguments.generationMode()) generate(arguments.count, arguments.range, workingDirectory, out);
            else grade(arguments.exerciseFile, arguments.answerFile, workingDirectory, out);
            return 0;
        } catch (Exception exception) {
            err.println("错误: " + exception.getMessage());
            err.print(HELP);
            return 2;
        }
    }

    private void generate(int count, int range, Path directory, PrintStream out) throws IOException {
        long seed = System.nanoTime();
        GenerationResult result = new ExerciseGenerator().generate(count, range, seed);
        List<String> exercises = new ArrayList<>(count);
        List<String> answers = new ArrayList<>(count);
        for (int index = 0; index < result.exercises().size(); index++) {
            Expression expression = result.exercises().get(index);
            exercises.add((index + 1) + ". " + expression.render() + " =");
            answers.add((index + 1) + ") " + expression.value());
        }
        Files.write(directory.resolve("Exercises.txt"), exercises, StandardCharsets.UTF_8);
        Files.write(directory.resolve("Answers.txt"), answers, StandardCharsets.UTF_8);
        out.printf("已生成 %d 道题目：%s，答案：%s%n", count,
                directory.resolve("Exercises.txt").toAbsolutePath(), directory.resolve("Answers.txt").toAbsolutePath());
    }

    private void grade(Path exercise, Path answer, Path directory, PrintStream out) throws IOException {
        GradeResult result = new Grader().grade(exercise, answer);
        Path gradeFile = directory.resolve("Grade.txt");
        Files.writeString(gradeFile, result.format(), StandardCharsets.UTF_8);
        out.println(result.format().stripTrailing());
        out.println("统计结果：" + gradeFile.toAbsolutePath());
    }

    private static final class Arguments {
        Integer count;
        Integer range;
        Path exerciseFile;
        Path answerFile;

        static Arguments parse(String[] args) {
            Arguments result = new Arguments();
            if (args.length == 0 || args.length % 2 != 0) throw new IllegalArgumentException("参数不完整");
            for (int index = 0; index < args.length; index += 2) {
                String option = args[index];
                String value = args[index + 1];
                switch (option) {
                    case "-n" -> { ensureUnset(result.count, option); result.count = positiveInt(value, option); }
                    case "-r" -> { ensureUnset(result.range, option); result.range = positiveInt(value, option); }
                    case "-e" -> { ensureUnset(result.exerciseFile, option); result.exerciseFile = Path.of(value); }
                    case "-a" -> { ensureUnset(result.answerFile, option); result.answerFile = Path.of(value); }
                    default -> throw new IllegalArgumentException("未知参数: " + option);
                }
            }
            boolean anyGeneration = result.count != null || result.range != null;
            boolean anyGrading = result.exerciseFile != null || result.answerFile != null;
            if (anyGeneration == anyGrading) throw new IllegalArgumentException("必须且只能选择生成模式或判题模式");
            if (anyGeneration && (result.count == null || result.range == null)) throw new IllegalArgumentException("生成模式必须同时提供 -n 和 -r");
            if (anyGrading && (result.exerciseFile == null || result.answerFile == null)) throw new IllegalArgumentException("判题模式必须同时提供 -e 和 -a");
            return result;
        }

        boolean generationMode() { return count != null; }
        private static int positiveInt(String value, String option) {
            try {
                int parsed = Integer.parseInt(value);
                if (parsed <= 0) throw new NumberFormatException();
                return parsed;
            } catch (NumberFormatException exception) {
                throw new IllegalArgumentException(option + " 必须是正整数: " + value);
            }
        }
        private static void ensureUnset(Object previous, String option) {
            if (previous != null) throw new IllegalArgumentException("参数重复: " + option);
        }
    }
}

