document.getElementById("loginForm").addEventListener("submit", function(event) {
   event.preventDefault(); // Prevent page refresh

   const username = document.getElementById("username").value;
   const password = document.getElementById("password").value;
   const role = document.getElementById("role").value;

   // Basic authentication simulation (replace with real authentication in future)
   if (username && password) {
       localStorage.setItem("userRole", role); // Store role in local storage

       if (role === "patient") {
           window.location.href = "patients.html";
       } else if (role === "doctor") {
           window.location.href = "doctors.html";
       }
   } else {
       alert("Please enter valid credentials.");
   }
});


// Function to check if user has the right access
function checkAccess(expectedRole) {
   const role = localStorage.getItem("userRole");
   
   if (role !== expectedRole) {
       alert("Unauthorized access! Redirecting to login.");
       window.location.href = "index.html";
   }
}

// Function to navigate sections dynamically
function navigate(section) {
   document.getElementById("content-area").innerHTML = `<p>Loading ${section}...</p>`;
}

// Function to logout
function logout() {
   localStorage.removeItem("userRole"); // Clear user role
   window.location.href = "index.html"; // Redirect to login page
}

let lastScrollTop = 0; // Variable to store the last scroll position

window.addEventListener('scroll', function() {
   const header = document.querySelector('header');
   const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

   if (scrollTop > lastScrollTop) {
      // Scrolling down
      header.classList.add('header-shadow'); // Add shadow
   } else {
      // Scrolling up
      header.classList.remove('header-shadow'); // Remove shadow
   }

   lastScrollTop = scrollTop; // Update the last scroll position
});