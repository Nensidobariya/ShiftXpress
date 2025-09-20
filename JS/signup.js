
    function handleSignup(event) {
      event.preventDefault();

      const password = document.getElementById("password").value;
      const confirmPassword = document.getElementById("confirmPassword").value;

      if (password !== confirmPassword) {
        alert("Passwords do not match. Please try again.");
        return;
      }

      alert("Account created successfully!");
      window.location.href = "loginpage.html"; // Update path if needed
    }
