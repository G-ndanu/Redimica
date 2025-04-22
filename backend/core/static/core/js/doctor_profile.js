let currentField = ''; // Store the current field to be edited

// Get CSRF token from the browser's cookies
function getCsrfToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            csrfToken = cookie.substring('csrftoken='.length);
            break;
        }
    }
    return csrfToken;
}


// Show modal for editing field (Qualifications, Experience, Affiliations)
function editInfo(field) {
    document.getElementById("editModal").style.display = "flex";
    document.getElementById("edit-field").value = document.getElementById("doctor-" + field).innerText;
    document.getElementById("edit-form").onsubmit = function(event) {
        event.preventDefault();
        saveEdit(field, document.getElementById("edit-field").value);
    };
}

// Show modal for editing profile photo
function editPhoto() {
    document.getElementById("photoModal").style.display = "flex";
}

// Close Modals
function closeModal() {
    document.getElementById("editModal").style.display = "none";
}

function closePhotoModal() {
    document.getElementById("photoModal").style.display = "none";
}


// Save edited information
function saveEdit(field, value) {
    // Send the updated data to the server via an API call (you'll need to implement this)
    fetch(`/update-doctor-info/`, {
        method: 'POST',
        body: JSON.stringify({ field: field, value: value }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the displayed info on the page
            document.getElementById("doctor-" + field).innerText = value;
            closeModal();  // Close the modal after saving
        } else {
            alert("Error saving information.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Save new profile image
document.getElementById("photo-form").onsubmit = function(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("profile-picture", document.getElementById("profile-picture").files[0]);

    fetch("/update-profile-picture/", {
        method: "POST",
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelector(".profile-photo img").src = data.new_image_url;  // Update image
            closePhotoModal();  // Close the modal after upload
        } else {
            alert("Error uploading the image.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
};
