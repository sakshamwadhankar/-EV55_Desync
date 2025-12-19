// TruthLens Desktop - Renderer Logic
const API_BASE_URL = "https://anonymous-krysta-sakshamwadhankar-fe5fe52c.koyeb.app";
// const API_BASE_URL = "http://127.0.0.1:8000";

const claimInput = document.getElementById('claimInput');
const verifyBtn = document.getElementById('verifyBtn');
const loader = document.getElementById('loader');
const resultCard = document.getElementById('resultCard');
const errorBox = document.getElementById('errorBox');
const errorText = document.getElementById('errorText');

const verdictText = document.getElementById('verdictText');
const confidenceValue = document.getElementById('confidenceValue');
const sourceCount = document.getElementById('sourceCount');

verifyBtn.addEventListener('click', verifyClaim);

claimInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') verifyClaim();
});

async function verifyClaim() {
    const claim = claimInput.value.trim();
    if (!claim) return;

    // Reset UI
    hide(resultCard);
    hide(errorBox);
    show(loader);
    verifyBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ claim: claim })
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }

        const data = await response.json();
        displayResult(data);
    } catch (error) {
        console.error("Verification Error:", error);
        showError("Unable to connect to TruthLens server. Please check your internet connection.");
    } finally {
        hide(loader);
        verifyBtn.disabled = false;
    }
}

function displayResult(data) {
    verdictText.textContent = data.verdict;
    confidenceValue.textContent = data.confidence;
    sourceCount.textContent = data.sources;

    // Apply color coding
    const verdict = data.verdict.toLowerCase();
    verdictText.className = ""; // Reset

    if (verdict.includes("true")) {
        verdictText.classList.add('true-verdict');
    } else if (verdict.includes("fake") || verdict.includes("false")) {
        verdictText.classList.add('fake-verdict');
    } else {
        verdictText.classList.add('unverified-verdict');
    }

    show(resultCard);
}

function showError(msg) {
    errorText.textContent = msg;
    show(errorBox);
}

function show(el) {
    el.classList.remove('d-none');
}

function hide(el) {
    el.classList.add('d-none');
}
