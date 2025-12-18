package com.truthlens.app;

import com.google.gson.annotations.SerializedName;

public class VerificationResponse {
    @SerializedName("verdict")
    private String verdict;

    @SerializedName("confidence")
    private String confidence;

    @SerializedName("sources")
    private int sources;

    public String getVerdict() {
        return verdict;
    }

    public String getConfidence() {
        return confidence;
    }

    public int getSources() {
        return sources;
    }
}
