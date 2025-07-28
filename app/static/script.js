const BASE_URL = "http://127.0.0.1:8000";
// Function to show notifications
function showNotification(message, type) {
    const notification = document.getElementById("notification");
    const notificationMessage = document.getElementById("notificationMessage");

    notificationMessage.textContent = message;

    if (type === "success") {
        notification.classList.add("success");
        notification.classList.remove("error");
    } else if (type === "error") {
        notification.classList.add("error");
        notification.classList.remove("success");
    }

    notification.style.display = "flex"; // Show the notification

    // Auto-hide the notification after 3 seconds
    setTimeout(() => {
        notification.style.display = "none";
    }, 3000);
}

// Function to close the notification manually
function closeNotification() {
    const notification = document.getElementById("notification");
    notification.style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    console.log("Script loaded successfully!");

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            let email = document.getElementById("login-email").value;
            let password = document.getElementById("login-password").value;

            try {
                let response = await fetch(`${BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: `username=${email}&password=${password}`
                });

                let result = await response.json();

                if (response.ok) {
                    console.log("Login Success! Token received:", result.access_token); // Log token
                    localStorage.setItem("token", result.access_token);
                    showNotification("Successfully logging in!", "success");
                    setTimeout(() => {
                        window.location.href = "/static/home.html"; // Redirect after showing notification
                    }, 3000);
                } else {
                    console.error("Login Failed:", result.detail);
                    showNotification("Invalid credentials. Please try again.", "error");
                }
            } catch (error) {
                console.error("Error during login:", error);
                showNotification("An error occurred. Please try again later.", "error");
            }
        });
    }
    // ...existing code...
const registerForm = document.getElementById("register-form");
if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("register-username").value;
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;

        try {
            const response = await fetch(`${BASE_URL}/users/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                // Success case
                showNotification("Registration successful! Please login.", "success");
                showLogin(); // Switch to login form
                registerForm.reset(); // Clear the form
            } else {
                // Error cases
                const detail = data.detail || data.msg || data.error || "Unknown error";
                
                if (detail === "Email already registered") {
                    showNotification("This email is already registered. Please use a different email.", "error");
                } else if (detail === "Username already taken") {
                    showNotification("This username is already taken. Please choose a different username.", "error");
                } else if (Array.isArray(detail)) {
                    const msg = detail[0]?.msg || "Invalid input.";
                    showNotification("Registration failed: " + msg, "error");
                } else {
                    showNotification("Registration failed: " + detail, "error");
                }
            }
        } catch (error) {
            console.error("Registration error:", error);
            showNotification("An error occurred during registration. Please try again.", "error");
        }
    });
}

    // === SETTINGS SIDEBAR ===
    const settingsButton = document.querySelector(".nav-item i.bi-gear");
    const settingsSidebar = document.getElementById("settings-sidebar");
    const closeSidebarButton = document.getElementById("close-sidebar");
    const settingsForm = document.getElementById("settings-form");

    if (settingsButton && settingsSidebar && closeSidebarButton && settingsForm) {
        settingsButton.addEventListener("click", () => {
            settingsSidebar.style.display = "block";
        });

        closeSidebarButton.addEventListener("click", () => {
            settingsSidebar.style.display = "none";
        });

        settingsForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            if (!username && !password) {
                alert("Please enter a new username or password.");
                return;
            }

            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`${BASE_URL}/update`, {
                    method: "PUT",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ username, password })
                });

                const result = await response.json();
                if (!response.ok) throw new Error(result.detail || "Failed to update settings.");

                alert("Settings updated successfully!");

                if (username) {
                    const userResponse = await fetch("${BASE_URL}/auth/me", {
                        headers: {
                            "Authorization": `Bearer ${token}`,
                            "Content-Type": "application/json"
                        }
                    });

                    const user = await userResponse.json();
                    if (userResponse.ok) {
                        document.getElementById("username").innerText = user.username;
                        document.querySelector(".profile-circle").innerText = user.username.charAt(0).toUpperCase();
                    }
                }

                settingsSidebar.style.display = "none";
            } catch (error) {
                console.error(error);
                alert("Error updating settings!");
            }
        });
    }
// ...existing code...
    const editPostForm = document.getElementById("editPostForm");
    if (editPostForm) {
        editPostForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const postId = document.getElementById("post_id").value;
            const title = document.getElementById("title").value;
            const content = document.getElementById("content").value;
            const published = document.getElementById("published").checked;

            console.log("Submitting Post Update:", { postId, title, content, published }); // Debugging

            if (!postId) {
                alert("Error: Post ID is missing!");
                return;
            }

            try {
                let response = await fetch(`${BASE_URL}/posts/${postId}`, {
                    method: "PUT",
                    headers: {
                        "Authorization": `Bearer ${localStorage.getItem("token")}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ title, content, published })
                });

                let result = await response.json();
                console.log("Update Response:", result); // Debugging

                if (!response.ok) {
                    throw new Error(result.detail || "Failed to update post");
                }

                alert("Post updated successfully!");
                window.location.href = "/static/myposts.html";

            } catch (error) {
                console.error("Error updating post:", error);
                alert(`Error updating post: ${error.message}`);
            }
        });
    }

    const logoutButton = document.getElementById("logout");
    if (logoutButton) {
        logoutButton.addEventListener("click", function (event) {
            event.preventDefault(); // Prevents default link behavior

            localStorage.removeItem("token"); // Clears authentication token
            window.location.href = "index.html"; // Redirects to login page
        });
    }

    // Removed duplicate declaration of settingsButton and related code
});
