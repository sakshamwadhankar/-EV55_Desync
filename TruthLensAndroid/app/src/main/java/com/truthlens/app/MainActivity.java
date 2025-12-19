package com.truthlens.app;

import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;

import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {

    // TODO: REPLACE WITH YOUR ACTUAL BACKEND URL
    private static final String BASE_URL = "https://anonymous-krysta-sakshamwadhankar-fe5fe52c.koyeb.app/";

    private TextInputEditText etClaim;
    private MaterialButton btnVerify;
    private ProgressBar progressBar;
    private CardView cvResult;
    private TextView tvVerdict, tvConfidence, tvSources;

    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize Views
        etClaim = findViewById(R.id.etClaim);
        btnVerify = findViewById(R.id.btnVerify);
        progressBar = findViewById(R.id.progressBar);
        cvResult = findViewById(R.id.cvResult);
        tvVerdict = findViewById(R.id.tvVerdict);
        tvConfidence = findViewById(R.id.tvConfidence);
        tvSources = findViewById(R.id.tvSources);

        // Initialize Retrofit
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        apiService = retrofit.create(ApiService.class);

        btnVerify.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                verifyClaim();
            }
        });
    }

    private void verifyClaim() {
        String claimText = etClaim.getText().toString().trim();
        if (claimText.isEmpty()) {
            etClaim.setError("Please enter a claim");
            return;
        }

        // UI Updates for Loading
        btnVerify.setEnabled(false);
        progressBar.setVisibility(View.VISIBLE);
        cvResult.setVisibility(View.GONE);
        etClaim.setError(null);

        VerificationRequest request = new VerificationRequest(claimText);
        Call<VerificationResponse> call = apiService.verifyClaim(request);

        call.enqueue(new Callback<VerificationResponse>() {
            @Override
            public void onResponse(Call<VerificationResponse> call, Response<VerificationResponse> response) {
                btnVerify.setEnabled(true);
                progressBar.setVisibility(View.GONE);

                if (response.isSuccessful() && response.body() != null) {
                    showResult(response.body());
                } else {
                    Toast.makeText(MainActivity.this, "Verification failed: " + response.code(), Toast.LENGTH_SHORT)
                            .show();
                }
            }

            @Override
            public void onFailure(Call<VerificationResponse> call, Throwable t) {
                btnVerify.setEnabled(true);
                progressBar.setVisibility(View.GONE);
                Toast.makeText(MainActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showResult(VerificationResponse response) {
        cvResult.setVisibility(View.VISIBLE);
        cvResult.setAlpha(0f);
        cvResult.animate().alpha(1f).setDuration(300).start();

        tvVerdict.setText(response.getVerdict());
        tvConfidence.setText(response.getConfidence());
        tvSources.setText(String.valueOf(response.getSources()));

        // Simple color coding logic based on verdict string
        String verdictRef = response.getVerdict().toLowerCase();
        int colorRes;

        if (verdictRef.contains("true")) {
            colorRes = R.color.verdict_true_green;
        } else if (verdictRef.contains("fake") || verdictRef.contains("false")) {
            colorRes = R.color.verdict_fake_red;
        } else {
            colorRes = R.color.verdict_unverified_gray;
        }

        tvVerdict.setTextColor(getResources().getColor(colorRes));
    }
}
