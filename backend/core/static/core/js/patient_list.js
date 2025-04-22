function filterPatients() {
    var input, filter, patientList, patientEntries, patientEntry, name, i;
    input = document.getElementById('searchBar');
    filter = input.value.toLowerCase();
    patientList = document.getElementsByClassName('patient-list')[0];
    patientEntries = patientList.getElementsByClassName('patient-entry');

    for (i = 0; i < patientEntries.length; i++) {
        patientEntry = patientEntries[i];
        name = patientEntry.getElementsByTagName('p')[0];  // Patient Name is in the first <p> tag
        if (name) {
            if (name.innerText.toLowerCase().indexOf(filter) > -1) {
                patientEntry.style.display = "";
            } else {
                patientEntry.style.display = "none";
            }
        }
    }
}


// Show feedback input area when "Add Feedback" button is clicked
document.addEventListener("click", function (e) {
    if (e.target.classList.contains("add-feedback-btn")) {
        const entryId = e.target.dataset.id;
        const patientCard = e.target.closest(".patient-entry");

        // Show the feedback input area
        const feedbackArea = patientCard.querySelector(".feedback-area");
        feedbackArea.classList.remove("hidden");

        // Fetch existing feedback if needed
        fetch(`/api/feedback/${entryId}/`)
        .then(res => res.json())
        .then(data => {
            const feedbackText = data.feedback || "";
            patientCard.querySelector(".feedback-input").value = feedbackText;
        })
        .catch(error => {
            console.error("Error fetching feedback:", error.message);
        });
    }
});

// Save feedback from the card
document.addEventListener("click", function (e) {
    if (e.target.classList.contains("save-feedback-btn")) {
        const patientCard = e.target.closest(".patient-entry");

        // Get the entryId from the add-feedback-btn (which has the correct data-id)
        const entryId = patientCard.querySelector(".add-feedback-btn").dataset.id;

        const feedbackText = patientCard.querySelector(".feedback-input").value;

        fetch(`/api/save-docfeedback/${entryId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.getElementById("csrf-token").value
            },
            body: JSON.stringify({ feedback: feedbackText })
        })
        .then(() => {
            alert("Feedback saved!");
            patientCard.querySelector(".feedback-area").classList.add("hidden");
        })
        .catch(error => {
            console.error("Error saving feedback:", error.message);
            alert("Failed to save feedback.");
        });
    }
});


// Hide feedback area when clicking outside of it
document.addEventListener("click", function (e) {
    const feedbackArea = e.target.closest(".patient-entry")?.querySelector(".feedback-area");
    const feedbackButton = e.target.closest(".patient-entry")?.querySelector(".add-feedback-btn");

    if (
        feedbackArea && // Ensure the feedback area exists
        !feedbackArea.contains(e.target) && // Check if the click is outside the feedback area
        feedbackButton && // Ensure the button exists
        !feedbackButton.contains(e.target) && // Check if the click is outside the feedback button
        !e.target.classList.contains("add-feedback-btn") // Check if the click is not directly on the button
    ) {
        feedbackArea.classList.add("hidden"); // Hide the feedback area
    }
});
