//header.html
document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.querySelector(".toggle-btn");
    const navMenu = document.querySelector(".nav-menu");

    toggleBtn.addEventListener("click", function () {
        navMenu.classList.toggle("active");
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const profileDropdown = document.querySelector(".profile-dropdown");
    const dropdownMenu = document.querySelector(".dropdown-menu");

    profileDropdown.addEventListener("click", function (event) {
        event.stopPropagation(); // Prevents closing when clicking inside
        this.classList.toggle("active");
    });

    // Close the dropdown if clicking anywhere else
    document.addEventListener("click", function (event) {
        if (!profileDropdown.contains(event.target)) {
            profileDropdown.classList.remove("active");
        }
    });
});


//header - reminders bell
document.addEventListener("DOMContentLoaded", function () {
    const bell = document.getElementById("notification-bell");
    const dropdown = document.getElementById("notification-dropdown");
    const reminderList = document.getElementById("reminder-list");

    // Toggle dropdown on bell click
    bell.addEventListener("click", function () {
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });

    // Sample reminders (replace this with real-time fetching from backend)
    const reminders = [
        { id: 1, text: "Take your medication at 3:00 PM" },
        { id: 2, text: "Your appointment is tomorrow at 10:00 AM" },
        { id: 3, text: "Drink 8 glasses of water today" }
    ];

    function renderReminders() {
        reminderList.innerHTML = "";
        if (reminders.length === 0) {
            dropdown.querySelector(".no-reminders").style.display = "block";
        } else {
            dropdown.querySelector(".no-reminders").style.display = "none";
            reminders.forEach(reminder => {
                const li = document.createElement("li");
                li.innerHTML = `${reminder.text} <button onclick="dismissReminder(${reminder.id})">✖</button>`;
                reminderList.appendChild(li);
            });
        }
    }

    window.dismissReminder = function (id) {
        const index = reminders.findIndex(r => r.id === id);
        if (index !== -1) reminders.splice(index, 1);
        renderReminders();
    };

    renderReminders();
});



//health_journal.html
document.addEventListener("DOMContentLoaded", function () {
    let addEntryBtn = document.getElementById("addEntryBtn");
    let entryModal = document.getElementById("entryModal");
    let closeModal = document.querySelector(".close");

    if (addEntryBtn && entryModal && closeModal) {
        // Open modal when clicking "Add New Entry"
        addEntryBtn.addEventListener("click", function () {
            entryModal.style.display = "flex"; // Show the modal
        });

        // Close modal when clicking the "X" button
        closeModal.addEventListener("click", function () {
            entryModal.style.display = "none"; // Hide the modal
        });

        // Close modal when clicking outside the modal-content
        window.addEventListener("click", function (event) {
            if (event.target === entryModal) {
                entryModal.style.display = "none"; // Hide the modal
            }
        });
    }
});

 

 //messages.html(chatbot)
 document.addEventListener("DOMContentLoaded", function () {
    function openChatbot() {
        document.getElementById("chat-title").textContent = "Redimica AI";
        const chatBody = document.getElementById("chat-body");
        chatBody.innerHTML = `
            <div class="message received bot">
                <p>Hello! I'm Redimica AI. Ask me anything about your health.</p>
                <span class="timestamp">Now</span>
            </div>
        `;
        document.getElementById("faq-buttons").style.display = "flex"; // Show FAQs only for chatbot
        scrollToBottom(); // Ensure chat is scrolled to the latest message
    }

    function sendMessage() {
        const inputField = document.getElementById("chat-input");
        const messageText = inputField.value.trim();
        if (messageText === "") return;

        appendUserMessage(messageText);
        inputField.value = "";

        setTimeout(() => {
            appendBotResponse("I'm still learning! You can ask about appointments, symptoms, or health tips.");
        }, 1000);
    }

    function sendFAQ(question) {
        appendUserMessage(question);

        setTimeout(() => {
            let response;
            switch (question) {
                case "How do I book an appointment?":
                    response = "You can book an appointment through the Virtual Visits section.";
                    break;
                case "What symptoms should I track?":
                    response = "It's best to track pain levels, diet, and medication adherence.";
                    break;
                case "Can I reschedule my virtual visit?":
                    response = "Yes, go to Virtual Visits and click on your scheduled appointment.";
                    break;
                case "How do I contact my doctor?":
                    response = "You can message your doctor through the Messages section.";
                    break;
                default:
                    response = "I'm not sure, but you can check the support center!";
            }
            appendBotResponse(response);
        }, 1000);
    }

    function appendUserMessage(message) {
        const chatBody = document.getElementById("chat-body");
        const userMessage = `
            <div class="message sent">
                <p>${message}</p>
                <span class="timestamp">Now</span>
            </div>
        `;
        chatBody.innerHTML += userMessage;
        scrollToBottom();
    }

    function appendBotResponse(message) {
        const chatBody = document.getElementById("chat-body");
        const botMessage = `
            <div class="message received bot">
                <p>${message}</p>
                <span class="timestamp">Now</span>
            </div>
        `;
        chatBody.innerHTML += botMessage;
        scrollToBottom();
    }

    function scrollToBottom() {
        const chatBody = document.getElementById("chat-body");
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Observe new messages to auto-scroll
    const chatObserver = new MutationObserver(scrollToBottom);
    chatObserver.observe(document.getElementById("chat-body"), { childList: true });

    // Hide FAQ buttons unless chatbot is active
    function toggleFAQ(show) {
        document.getElementById("faq-buttons").style.display = show ? "flex" : "none";
    }

    window.openChatbot = function () {
        openChatbot();
        toggleFAQ(true);
    };
    window.sendMessage = sendMessage;
    window.sendFAQ = sendFAQ;
});



//care_team_feedback.html
document.addEventListener("DOMContentLoaded", function () {
    // Sample progress data (Replace this with actual data from backend)
    const treatmentProgressData = {
        "Blood Pressure Management": 75,
        "Physical Therapy": 60,
        "Diabetes Monitoring": 40
    };

    function updateProgressBars() {
        const progressItems = document.querySelectorAll(".progress-item");

        progressItems.forEach((item) => {
            const label = item.querySelector(".progress-label").textContent.trim();
            const progressBar = item.querySelector(".progress-fill");

            if (treatmentProgressData[label] !== undefined) {
                const newValue = treatmentProgressData[label];

                // Animate progress update
                progressBar.style.width = newValue + "%";
                progressBar.textContent = newValue + "%";

                // Add glow effect when progress increases
                if (newValue > parseInt(progressBar.dataset.prevValue || "0")) {
                    progressBar.classList.add("glow");
                    setTimeout(() => progressBar.classList.remove("glow"), 1000);
                }

                progressBar.dataset.prevValue = newValue; // Store current value
            }
        });
    }

    // Initialize progress bars
    updateProgressBars();

    // Simulate progress update (Replace this with actual real-time updates)
    setTimeout(() => {
        treatmentProgressData["Blood Pressure Management"] = 85;
        treatmentProgressData["Diabetes Monitoring"] = 55;
        updateProgressBars();
    }, 3000);
});





