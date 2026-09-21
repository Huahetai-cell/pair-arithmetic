package com.huahetai.arithmetic;

import java.nio.file.Path;

public final class Main {
    private Main() { }
    public static void main(String[] args) {
        int exitCode = new Application().run(args, Path.of("."), System.out, System.err);
        if (exitCode != 0) System.exit(exitCode);
    }
}

