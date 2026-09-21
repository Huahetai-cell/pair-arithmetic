package com.huahetai.arithmetic;

public final class GenerationStats {
    private long candidateCount;
    private long constraintRejectCount;
    private long duplicateCount;
    void candidate() { candidateCount++; }
    void constraintReject() { constraintRejectCount++; }
    void duplicate() { duplicateCount++; }
    public long candidateCount() { return candidateCount; }
    public long constraintRejectCount() { return constraintRejectCount; }
    public long duplicateCount() { return duplicateCount; }
}

