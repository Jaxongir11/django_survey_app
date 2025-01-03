// static/js/main.js

function togglePasswordVisibility(passwordFieldId, eyeIconId) {
    const passwordField = document.getElementById(passwordFieldId);
    const eyeIcon = document.getElementById(eyeIconId);
    if (passwordField.type === "password") {
        passwordField.type = "text";
        eyeIcon.classList.remove("text-gray-500");
        eyeIcon.classList.add("text-blue-500");
    } else {
        passwordField.type = "password";
        eyeIcon.classList.remove("text-blue-500");
        eyeIcon.classList.add("text-gray-500");
    }
}