// Declare socket in the global scope so it can be accessed throughout
let socket;
let CURRENT_USER_ID;

function formatLocalTime(utcTimestamp) {
    const date = new Date(utcTimestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
}


document.addEventListener("DOMContentLoaded", function () {
    if (!window.WebSocket) {
        alert("Your browser does not support WebSocket. Please upgrade.");
        return;
    }

    // Fetch User ID for chat
    fetch("/api/current-user/")
        .then(response => response.json())
        .then(data => {
            CURRENT_USER_ID = data.user_id;
            loadRecentChats();  // Proceed with loading recent chats after the user ID is fetched
        })
        .catch(error => console.error("Failed to load user ID:", error));

        


    function debounce(func, delay) {
        let timeoutId;
        return function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(func, delay);
        };
    }
        
    
   // Declare socket and search input
    const searchInput = document.getElementById("searchInput");
    const resultsContainer = document.getElementById("search-results");

    searchInput.addEventListener("input", debounce(function () {
        const query = searchInput.value.trim().toLowerCase();
        
        if (query.length === 0) {
            resultsContainer.innerHTML = ''; // Clear results if input is empty
            return;
        }

        // Send search query to server
        fetch(`/search_conversation/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                if (!data.users) {
                    console.warn("No 'users' array in response.");
                    resultsContainer.innerHTML = "<p>Error: Invalid response format.</p>";
                    return;
                }

                displaySearchResults(data.users);
            })
            .catch(error => {
                console.error("Search error:", error);
                resultsContainer.innerHTML = "<p>Error occurred. Please try again.</p>";
            });
    }, 300)); // 300ms debounce delay

    
    function displaySearchResults(users) {
        const resultsContainer = document.getElementById("search-results");
        resultsContainer.innerHTML = "";  // Clear previous results
    
        if (users.length === 0) {
            resultsContainer.innerHTML = "<p>No users found.</p>";
            return;
        }
    
        users.forEach(user => {
            console.log("user.chat_id:", user.chat_id);
            const userDiv = document.createElement("div");
            userDiv.classList.add("search-result-item");
            userDiv.innerHTML = `
                <div class="user-info">
                    <img src="${user.profile_picture}" alt="${user.name}'s profile picture" class="profile-img">
                    <div class="user-details">
                        <p><strong>${user.name}</strong></p>
                        <p>${user.username}</p>
                    </div>
                </div>
            `;
            userDiv.addEventListener("click", () => {
                searchInput.value = ""; // Clear search input
                resultsContainer.innerHTML = ""; // Clear search results
                if (user.chat_id) {
                    startNewChat(user.chat_id, user.name); // Start chat if valid chat_id is provided
                    console.log("user.chat_id:", user.chat_id);
                } else {
                    // If no chat_id, create a new chat_id and start the chat
                    createNewChat(user.id, user.name);
                }
            });
            resultsContainer.appendChild(userDiv);
        });
    }
    

    // Function to get the CSRF token from the meta tag
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }
    

    // Function to create a new chat
    function createNewChat(userId, userName) {
        const csrfToken = getCsrfToken();  // Get the CSRF token
    
        fetch(`/api/create_chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Add the CSRF token to the headers
            },
            body: JSON.stringify({ userId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // On success, start the chat with the new chatId
                startNewChat(data.chat_id, userName); 
                console.log("New chat response:", data);  // Use the newly created chat_id
            } else {
                console.error('Error creating new chat:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    

    // Display incoming message
    function displayIncomingMessage(message, sender, timestamp, fileUrl, filename) {
        const chatBox = document.getElementById("chatBox");
        const isSender = sender === CURRENT_USER_ID;  // Check if the sender is the current user

        if (fileUrl) {
            console.log("Full media file URL:", `/media/${fileUrl}`);
        }
    
        // Add message to chat with proper styling
        chatBox.innerHTML += `
            <div class="message ${isSender ? 'sent' : 'received'}">
                <p>${message}</p>
                ${fileUrl ? `<a href="${fileUrl}" target="_blank">📎 ${filename || 'Download File'}</a>` : ""}
                <span>${formatLocalTime(timestamp)}</span>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    }


    function toggleMessageInput(visible) {
        const inputContainer = document.getElementById("chatInputContainer");
        if (visible) {
            inputContainer.classList.remove("hidden");
        } else {
            inputContainer.classList.add("hidden");
        }
    }
    
    

    // Start New Chat
    function startNewChat(chatId, userName) {
        console.log("Starting chat with ID:", chatId);
        document.getElementById("chatTitle").textContent = userName;
        document.getElementById("chatBox").innerHTML = "<p>Loading messages...</p>";
    
        if (!chatId) {
            console.error("No valid chatId provided");
            toggleMessageInput(false);  // Hide message input when no chat is selected
            return;  // Exit if chatId is missing or invalid
        }
    
        toggleMessageInput(true);  // Show message input when a chat is selected
    
    
        // Fetch the chat messages for this chatId
        fetch(`/get_chat_messages/${chatId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    document.getElementById("chatBox").innerHTML = `<p>Error: ${data.error}</p>`;
                    return;
                }

                // Sort messages by timestamp (oldest first or newest first)
                data.messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

                // Display the chat messages in the chat box
                let chatContent = "";
                data.messages.forEach(msg => {
                    const isSender = parseInt(msg.sender) === parseInt(CURRENT_USER_ID);
                    console.log(`msg.sender: ${msg.sender}, CURRENT_USER_ID: ${CURRENT_USER_ID}, isSender: ${isSender}`);

                    chatContent += `
                        <div class="message ${isSender ? 'sent' : 'received'}">
                            <p>${msg.content}</p>
                            ${msg.file && msg.filename ? `<a href="/media/${msg.file}" target="_blank">📎 ${msg.filename}</a>` : ""}
                            <span>${msg.timestamp}</span>
                        </div>
                    `;

                });
                document.getElementById("chatBox").innerHTML = chatContent || "<p>No messages yet.</p>";
                chatBox.scrollTop = chatBox.scrollHeight;
    
                // Start WebSocket connection
                startWebSocket(chatId);
            })
            .catch(error => {
                console.error('Error loading chat:', error);
                document.getElementById("chatBox").innerHTML = "<p>Failed to load messages.</p>";
            });
    }
    

    // Send Message via WebSocket
    document.getElementById("sendButton").addEventListener("click", sendMessage);
    document.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            const messageText = document.getElementById("messageInput").value.trim();
            const fileSelected = document.getElementById("fileInput").files.length > 0;
            if (messageText || fileSelected) {
                sendMessage();
                e.preventDefault();  // Optional: prevent form submission behavior
            }
        }
    });

    function sendMessage() {
        const messageInput = document.getElementById("messageInput");
        const fileInput = document.getElementById("fileInput");
        const messageText = messageInput.value.trim();
        const file = fileInput.files[0];
        
        if (!messageText && !file) return; // Prevent empty messages
        
        if (!socket) {
            console.error("WebSocket is not defined.");
            alert("WebSocket connection not established. Please try again later.");
            return;
        }
        
        if (socket.readyState !== WebSocket.OPEN) {
            console.error("WebSocket is not open. Current state:", socket.readyState);
            alert("WebSocket connection is closed. Reconnecting...");
            reconnectWebSocket(CURRENT_USER_ID); // Attempt to reconnect the WebSocket
            return;
        }
        
        const messageData = { message: messageText, sender: CURRENT_USER_ID };
        
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                messageData.file = event.target.result; // Base64 string
                messageData.filename = file.name;       // Add original file name
                socket.send(JSON.stringify(messageData));
                displaySentMessage(messageData.message, messageData.sender, messageData.filename);
            };
            reader.readAsDataURL(file);        
        } else {
            socket.send(JSON.stringify(messageData)); // Send the message without file
            displaySentMessage(messageData.message, messageData.sender); // Update chat with sent message
        }
        
        messageInput.value = "";
        fileInput.value = "";
        document.getElementById("filePreview").style.display = "none";
    }
    
    // Display sent message immediately after sending
    function displaySentMessage(message, sender, filename = null, fileUrl = null) {
        const chatBox = document.getElementById("chatBox");
        
        let fileLink = "";
        if (filename) {
            const constructedUrl = `/media/uploads/messages/${filename}`;
            fileLink = `<a href="${constructedUrl}" target="_blank">📎 ${filename}</a>`;
        }
    
        chatBox.innerHTML += `
            <div class="message sent">
                <p>${message || ""}</p>
                ${fileLink}
                <span>${formatLocalTime(new Date().toISOString())}</span>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    

    // Reconnect WebSocket function if it's closed
    function reconnectWebSocket(contactId) {
        console.log("Attempting to reconnect WebSocket...");
        if (socket) {
            socket.close();  // Close any existing socket
        }
        startWebSocket(contactId); // Re-establish WebSocket connection for the current chat
    }

    // Start WebSocket connection after chat is loaded or during initialization
    function startWebSocket(contactId) {
        socket = new WebSocket(`ws://${window.location.host}/ws/chat/${contactId}/`);

        socket.onopen = function() {
            console.log("WebSocket connection established");
        };

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.status === 'success') {
                const chatBox = document.getElementById("chatBox");

                if (fileUrl) {
                    console.log("Full media file URL:", `/media/${fileUrl}`);
                }
        
                // Only update chatBox if it's the correct chat
                if (data.chat_id === CURRENT_CHAT_ID) {
                    const isSender = data.sender === CURRENT_USER_ID; // Check if the message is from the current user
                    const messageElement = document.createElement('div');
                    messageElement.classList.add('message', isSender ? 'sent' : 'received');
                    messageElement.innerHTML = `
                        <p>${data.message}</p>
                        ${data.file_url ? `<a href="${data.file_url}" target="_blank">📎 ${data.filename}</a>` : ""}
                        <span>${formatLocalTime(data.timestamp)}</span>
                    `;

                    if (fileUrl) {
                        console.log("Full media file URL:", `/media/${fileUrl}`);
                    }
                    
                    chatBox.appendChild(messageElement);
                    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the latest message
                }
        
                // Optionally update the preview in the chat list
                updateChatListWithMessage(data.chat_id, data.message, data.sender);
            }
        };
        
        
        
        socket.onerror = function(error) {
            console.error("WebSocket error:", error);
        };

        socket.onclose = function() {
            console.log("WebSocket connection closed");
            reconnectWebSocket(contactId); // Reconnect if the WebSocket closes unexpectedly
        };
    }

    // Function to update the recent chat list with the new message
    function updateChatListWithMessage(chatId, message, sender) {
        const chatListContainer = document.getElementById("chatListContainer");
    
        if (!chatListContainer) {
            console.error("Error: chatListContainer not found.");
            return;
        }
    
        const chatItems = chatListContainer.querySelectorAll(".chat-item");
    
        // Find the chat item in the list based on chatId
        let chatItem = Array.from(chatItems).find(item => item.dataset.chatId === chatId.toString());
    
        if (chatItem) {
            const messagePreview = chatItem.querySelector(".chat-preview");
            if (messagePreview) {
                messagePreview.textContent = message;  // Update the message preview with the new message
                // You can also update other details like the time of the message if you want
            } else {
                console.error("Error: messagePreview element not found.");
            }
        } else {
            console.log("Chat item not found, adding new one...");
            // If the chat isn't found, load the recent chats again
            loadRecentChats();  // Optionally reload the chats if the item is not found
        }
    }
    

    
    // Load Recent Chats
    function loadRecentChats() {
        fetch("/recent-chats/")
            .then(response => response.json())
            .then(data => {
                console.log("Recent Chats Data:", data);
                const chatListContainer = document.getElementById("chatListContainer");
                if (!chatListContainer) {
                    console.error("Error: chatListContainer not found.");
                    return;
                }

                chatListContainer.innerHTML = "";
                if (data.chats.length === 0) {
                    chatListContainer.innerHTML = "<p>No recent chats.</p>";
                    return;
                }

                data.chats.forEach(chat => {
                    console.log("Chat object:", chat);
                    const div = document.createElement("div");
                    div.classList.add("chat-item");
                    div.innerHTML = `
                        <img src="${chat.profile_picture || '/static/core/images/profile.jpg'}" alt="Profile">
                        <div>
                            <p class="chat-name">${chat.name}</p>
                            <p class="chat-preview">${chat.last_message}</p>
                        </div>
                    `;
                    div.addEventListener("click", () => startNewChat(chat.chat_id, chat.name));
                    chatListContainer.appendChild(div);
                });
            })
            .catch(error => console.error("Error loading recent chats:", error));
    }

    // File Preview Before Sending
document.getElementById("fileInput").addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;

    const filePreview = document.getElementById("filePreview");
    filePreview.style.display = "block";
    filePreview.innerHTML = "";  // Clear any previous preview content

    // Create a close button
    const closeButton = document.createElement("button");
    closeButton.textContent = "X";  // Text for the button
    closeButton.classList.add("close-btn");  // You can style this button using CSS

    // Append the close button to the preview container
    filePreview.appendChild(closeButton);

    // Event listener to close the preview when button is clicked
    closeButton.addEventListener("click", function () {
        filePreview.style.display = "none";  // Hide the preview
        document.getElementById("fileInput").value = "";  // Optionally reset the file input
    });

    // Handle image files
    if (file.type.startsWith("image/")) {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = "100px";
        filePreview.appendChild(img);
    } else {
        // Handle non-image files by creating a paragraph element for the file name
        const fileName = document.createElement("p");
        fileName.textContent = `📎 ${file.name}`;
        filePreview.appendChild(fileName);
    }
});
document.addEventListener("click", function (event) {
    const isClickInside = searchInput.contains(event.target) || resultsContainer.contains(event.target);
    if (!isClickInside) {
        resultsContainer.innerHTML = ""; // Hide search results
    }
});

});


