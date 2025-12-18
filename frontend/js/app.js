/**
 * TruthLens Frontend Logic
 * Connects to the Django Backend API to verify news claims.
 */

// CONFIGURATION
// Replace this with your deployed backend URL (e.g., https://truthlens-backend.onrender.com)
// If running locally with CORS enabled, you might use http://127.0.0.1:8000/
const API_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("analysis-form");
    const resultSection = document.getElementById("result-section"); // Container for results
    const verdictText = document.getElementById("verdict-text");
    const verdictCard = document.getElementById("verdict-card");
    const confidenceBadge = document.getElementById("confidence-badge");
    const visualContainer = document.getElementById("visual-container");
    const sourcesContainer = document.getElementById("sources-container");
    const submitBtn = document.querySelector(".btn-verify");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            // 1. Get Input
            const query = document.getElementById("facts").value.trim();
            if (!query) return;

            // 2. UI Loading State
            const originalBtnText = submitBtn.innerText;
            submitBtn.innerText = "Verifying...";
            submitBtn.disabled = true;

            // Hide previous results
            if (resultSection) resultSection.style.display = "none";
            // Clear previous states
            verdictCard.className = "verdict-card";

            try {
                // 3. API Call
                // Note: The backend must expect a POST request with 'facts' in the body
                // and return a JSON response with:
                // {
                //   "fact_check": "Verdict String",
                //   "fine": "HTML Table of Sources" (or list of URLs),
                //   "news_image": "URL of image" (optional),
                //   "data": "Base64 string" (optional fallback)
                // }

                const formData = new FormData();
                formData.append('facts', query);

                // Option A: If backend returns HTML (Legacy Mode support)
                // In a perfect separated world, we'd use JSON. 
                // Since we can't touch backend, we'll try to fetch the page 
                // and parse the specific parts from the HTML response (Scraping own backend).
                // Or if the backend supports JSON, usage is simpler.

                // Assuming standard form submission behavior over AJAX for now
                // to support existing backend without code changes:
                const response = await fetch(API_BASE_URL, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("Network response was not ok");

                // HACK: Since existing backend returns full HTML, we parse it to extract data.
                // This makes the frontend compatible WITHOUT backend changes.
                const updatedHtmlText = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(updatedHtmlText, "text/html");

                // 4. Extract Data from Response HTML
                const newVerdict = doc.getElementById("verdict-text")?.innerText;
                const newVisuals = doc.getElementById("visual-container")?.innerHTML;
                const newSources = doc.querySelector(".sources-table")?.innerHTML;

                if (newVerdict) {
                    // 5. Update UI
                    verdictText.innerText = newVerdict;
                    if (confidenceBadge) confidenceBadge.innerText = "Analysis Complete";

                    if (visualContainer && newVisuals) {
                        visualContainer.innerHTML = newVisuals;
                    }

                    if (sourcesContainer && newSources) {
                        sourcesContainer.innerHTML = newSources;
                    }

                    updateVerdictStyle(newVerdict, verdictCard);

                    // Show Results
                    if (resultSection) {
                        resultSection.style.display = "block";
                        // Re-trigger animation
                        resultSection.style.animation = 'none';
                        resultSection.offsetHeight; /* trigger reflow */
                        resultSection.style.animation = "fadeIn 0.6s ease-out";
                    }
                } else {
                    alert("Could not verify. Please try again.");
                }

            } catch (error) {
                console.error("Error:", error);
                alert("Connection failed. Ensure backend is running.");
            } finally {
                // Reset Button
                submitBtn.innerText = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }
});

// Helper: Apply colors based on verdict text
function updateVerdictStyle(text, cardElement) {
    if (!text || !cardElement) return;
    text = text.toLowerCase();

    // Clear classes
    cardElement.classList.remove("v-strong-true", "v-likely-true", "v-fake", "v-unverified");

    if (text.includes("true") && text.includes("high confidence")) {
        cardElement.classList.add("v-strong-true");
    } else if (text.includes("true") || text.includes("likely")) {
        cardElement.classList.add("v-likely-true");
    } else if (text.includes("fake") || text.includes("hate") || text.includes("profanity")) {
        cardElement.classList.add("v-fake");
    } else {
        cardElement.classList.add("v-unverified");
    }
}
