package com.truthlens.app;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface ApiService {
    @POST("verify")
    Call<VerificationResponse> verifyClaim(@Body VerificationRequest request);
}
