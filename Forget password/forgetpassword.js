document.getElementById("resetForm").addEventListener("submit", function(event) {
  event.preventDefault();

  const password = document.getElementById("password").value.trim();
  const confirmPassword = document.getElementById("confirmPassword").value.trim();
  const errorMsg = document.getElementById("errorMsg");

  errorMsg.textContent = ""; // reset message

  if (password !== confirmPassword) {
    errorMsg.textContent = "Passwords do not match!";
    return;
  }

  alert("Password reset successfully!");
  window.location.href = "/HTML/home.html"; // Redirect to home page
});
