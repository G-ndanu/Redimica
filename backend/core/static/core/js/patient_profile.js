document.addEventListener('DOMContentLoaded', function () {
    let currentField = '';

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

    window.editInfo = function(field) {
        document.getElementById("editModal").style.display = "flex";
        document.getElementById("edit-field").value = document.getElementById("patient-" + field).innerText;
        document.getElementById("edit-form").onsubmit = function(event) {
            event.preventDefault();
            saveEdit(field, document.getElementById("edit-field").value);
        };
    }

    window.editPhoto = function() {
        document.getElementById("photoModal").style.display = "flex";
    }

    window.closeModal = function() {
        document.getElementById("editModal").style.display = "none";
    }

    window.closePhotoModal = function() {
        document.getElementById("photoModal").style.display = "none";
    }

    function saveEdit(field, value) {
        fetch(`/update-patient-info/`, {
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
                document.getElementById("patient-" + field).innerText = value;
                closeModal();
            } else {
                alert("Error saving information.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    document.getElementById("photo-form").onsubmit = function(event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("profile-picture", document.getElementById("profile-picture").files[0]);

        fetch("/update-patient-profile-picture/", {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(".profile-photo img").src = data.new_image_url;
                closePhotoModal();
            } else {
                alert("Error uploading the image.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
});
