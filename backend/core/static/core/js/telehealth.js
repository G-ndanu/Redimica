console.log("✅ telehealth.js is loaded successfully!");

// Schedule Consultation (with Google Meet integration)
document.getElementById("scheduleBtn").addEventListener("click", function () {
    let date = document.getElementById("consultDate").value;
    let time = document.getElementById("consultTime").value;
    let type = document.getElementById("consultType").value;
    let condition = document.getElementById("consultCondition").value;
    let patientId = document.getElementById("selectedPatientId").value;
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    if (!patientId) {
        alert("Please select a patient.");
        return;
    }
    if (!date || !time) {
        alert("Please select date and time.");
        return;
    }

    // Convert selected date and time into a Date object
    let selectedDateTime = new Date(`${date}T${time}`);
    let now = new Date();

    if (selectedDateTime <= now) {
        alert("You cannot schedule a consultation for the past.");
        return;
    }

    let formData = new FormData();
    formData.append("patient_id", patientId);
    formData.append("scheduled_date", date);
    formData.append("scheduled_time", time);
    formData.append("consult_type", type);
    formData.append("condition", condition); 
    formData.append("csrfmiddlewaretoken", csrfToken);

    fetch("/schedule-consultation/", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json().catch(() => {
            throw new Error("Invalid JSON response");
        });
    })
    .then(data => {
        if (data.success) {
            alert("Consultation scheduled successfully!");
            window.location.reload();
            let meetContainer = document.getElementById("meetContainer");
            if (meetContainer) {
                meetContainer.innerHTML = `<a href="${data.google_meet_link}" target="_blank">Join Consultation</a>`;
            }
        } else {
            throw new Error("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error.message);
        alert("Failed to schedule consultation: " + error.message);
    });
});

document.querySelectorAll(".select-patient").forEach(link => {
    link.addEventListener("click", function (e) {
        e.preventDefault();
        const patientId = this.dataset.id;
        const patientName = this.dataset.name;
        document.getElementById("selectedPatientId").value = patientId;
        document.getElementById("selectedPatientName").innerText = patientName;
    });
});


document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/consultations/")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch consultations.");
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.message);
            }

            const upcomingContainer = document.getElementById("upcomingAppointments");
            const pastContainer = document.getElementById("pastAppointments");

            // Helper to generate appointment HTML with Add Feedback button
            const createAppointmentCard = (consult, isPast = false) => {
                return `
                    <div class="appointment-card">
                        <p><strong>Patient:</strong> ${consult.patient}</p>
                        <p><strong>Date:</strong> ${consult.date}</p>
                        <p><strong>Time:</strong> ${consult.time}</p>
                        <p><strong>Type:</strong> ${consult.type}</p>
                        <p><strong>Condition:</strong> ${consult.condition}</p>
                        ${
                            isPast
                                ? `<button class="add-feedback-btn" data-id="${consult.id}">Feedback</button>
                                <div class="feedback-area hidden">
                                    <textarea class="feedback-input" placeholder="Add your feedback here..."></textarea>
                                    <button class="save-feedback-btn">Save Feedback</button>
                                </div>`
                                : `<a href="${consult.link}" target="_blank" class="join-btn">Join Now</a>`
                        }
                    </div>
                `;
            };
            
            // Render Upcoming and Past
            if (data.upcoming.length > 0) {
                data.upcoming.forEach(c => {
                    upcomingContainer.innerHTML += createAppointmentCard(c);
                });
            } else {
                upcomingContainer.innerHTML = "<p>No upcoming consultations.</p>";
            }

            if (data.past.length > 0) {
                data.past.forEach(c => {
                    pastContainer.innerHTML += createAppointmentCard(c, true);
                });
            } else {
                pastContainer.innerHTML = "<p>No past consultations.</p>";
            }
        })
        .catch(error => {
            console.error("Error fetching consultations:", error.message);
        });
});


// Show feedback input area when "Add Feedback" button is clicked
document.addEventListener("click", function (e) {
    if (e.target.classList.contains("add-feedback-btn")) {
        const consultId = e.target.dataset.id;
        const consultationCard = e.target.closest(".appointment-card");

        // Show the feedback input area
        const feedbackArea = consultationCard.querySelector(".feedback-area");
        feedbackArea.classList.remove("hidden");

        // Optionally, fetch existing feedback if needed
        fetch(`/api/consultation-details/${consultId}/`)
            .then(res => res.json())
            .then(data => {
                consultationCard.querySelector(".feedback-input").value = data.feedback || "";
            });
    }
});

// Save feedback from the card
document.addEventListener("click", function (e) {
    if (e.target.classList.contains("save-feedback-btn")) {
        const consultationCard = e.target.closest(".appointment-card");
        const consultId = consultationCard.querySelector(".add-feedback-btn").dataset.id;
        const feedbackText = consultationCard.querySelector(".feedback-input").value;

        fetch(`/api/save-feedback/${consultId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({ feedback: feedbackText })
        })
        .then(() => {
            alert("Feedback saved!");
            consultationCard.querySelector(".feedback-area").classList.add("hidden");
        })
        .catch(error => {
            console.error("Error saving feedback:", error.message);
            alert("Failed to save feedback.");
        });
    }
});

// Hide feedback area when clicking outside of it
document.addEventListener("click", function (e) {
    const feedbackArea = e.target.closest(".appointment-card")?.querySelector(".feedback-area");
    const feedbackButton = e.target.closest(".appointment-card")?.querySelector(".add-feedback-btn");

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
