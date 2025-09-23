// /JS/signup.js
function handleSignup(event) {
  event.preventDefault();
  
  const name = document.querySelector('input[type="text"]').value;
  const email = document.querySelector('input[type="email"]').value;
  const phone = document.querySelector('input[type="tel"]').value;
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  
  // Validate passwords match
  if (password !== confirmPassword) {
    alert('Passwords do not match!');
    return;
  }
  
  // Store user data in localStorage
  localStorage.setItem('customerName', name);
  localStorage.setItem('customerEmail', email);
  localStorage.setItem('customerPhone', phone);
  localStorage.setItem('customerPassword', password); // Note: In real app, hash this
  
  alert('Signup successful! Redirecting to login...');
  window.location.href = '/HTML/loginpage.html';
}