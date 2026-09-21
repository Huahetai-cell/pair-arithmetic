package com.huahetai.arithmetic;

import java.util.List;

public record GenerationResult(List<Expression> exercises, GenerationStats stats) {
    public GenerationResult { exercises = List.copyOf(exercises); }
}

