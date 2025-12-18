package com.truthlens.app;

import com.google.gson.annotations.SerializedName;

public class VerificationRequest {
    @SerializedName("claim")
    private String claim;

    public VerificationRequest(String claim) {
        this.claim = claim;
    }

    public String getClaim() {
        return claim;
    }

    public void setClaim(String claim) {
        this.claim = claim;
    }
}
