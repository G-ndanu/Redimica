document.addEventListener("DOMContentLoaded", function () {
    const painInput = document.querySelector("#id_pain_severity");
    const painValue = document.querySelector("#painValue");

    const updateSliderBackground = (value) => {
        const percent = (value / 10) * 100;
        painInput.style.background = `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${percent}%, #E5E7EB ${percent}%, #E5E7EB 100%)`;
    };

    if (painInput) {
        updateSliderBackground(painInput.value);
        painValue.textContent = painInput.value;

        painInput.addEventListener("input", () => {
            const level = parseInt(painInput.value);
            painValue.textContent = level;
            updateSliderBackground(level);
            if (level >= 7) {
                alert("Your symptom severity is high. Please consider reaching out to a doctor.");
            }
        });
    }
});
