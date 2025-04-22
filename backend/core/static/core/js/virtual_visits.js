document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/patient-consultations/")
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch consultations.");
            return response.json();
        })
        .then(data => {
            const upcomingList = document.getElementById("upcomingConsultationsList");
            const pastList = document.getElementById("pastConsultationsList");

            const createAppointmentCard = (consult, isPast = false) => `
                <div class="appointment-card">
                    <p><strong>Doctor:</strong> ${consult.doctor}</p>
                    <p><strong>Date:</strong> ${consult.date}</p>
                    <p><strong>Time:</strong> ${consult.time}</p>
                    <p><strong>Type:</strong> ${consult.type}</p>
                    <p><strong>Condition:</strong> ${consult.condition || "Not specified"}</p>
                    ${
                        isPast
                            ? `<p><strong>Feedback:</strong> ${consult.feedback || "No feedback yet."}</p>`
                            : `<a href="${consult.link}" target="_blank" class="join-btn">Join Now</a>`
                    }
                </div>
            `;

            if (data.upcoming.length > 0) {
                upcomingList.innerHTML = "";
                data.upcoming.forEach(c => upcomingList.innerHTML += createAppointmentCard(c));
            } else {
                upcomingList.innerHTML = "<p>No upcoming consultations.</p>";
            }

            if (data.past.length > 0) {
                pastList.innerHTML = "";
                data.past.forEach(c => pastList.innerHTML += createAppointmentCard(c, true));
            } else {
                pastList.innerHTML = "<p>No past consultations.</p>";
            }
        })
        .catch(error => {
            console.error("Error:", error.message);
        });
});
