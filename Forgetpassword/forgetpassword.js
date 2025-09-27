const FORGET_PASSWORD_SERVER_PORT = 8083;

document.addEventListener('DOMContentLoaded', function() {
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    const messageDiv = document.getElementById('message');
    const resetModal = document.getElementById('resetModal');
    const closeModal = document.querySelector('.close');

    // Handle forgot password form submission
    forgotPasswordForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        
        try {
            const response = await fetch(`http://localhost:${FORGET_PASSWORD_SERVER_PORT}/send_reset_link`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(result.message, 'success');
                forgotPasswordForm.reset();
                
                // Store token for demo purposes (in real app, this would be in email)
                if (result.token) {
                    localStorage.setItem('resetToken', result.token);
                    localStorage.setItem('resetEmail', email);
                    
                    // Show reset modal after delay
                    setTimeout(() => {
                        showResetModal(email, result.token);
                    }, 2000);
                }
                
            } else {
                showMessage(result.message, 'error');
            }
        } catch (error) {
            showMessage('Error sending reset link: ' + error.message, 'error');
        }
    });

    // Handle reset password form submission
    resetPasswordForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const email = document.getElementById('resetEmail').value;
        const token = document.getElementById('resetToken').value;
        
        if (newPassword !== confirmPassword) {
            showMessage('Passwords do not match', 'error');
            return;
        }
        
        if (newPassword.length < 6) {
            showMessage('Password must be at least 6 characters long', 'error');
            return;
        }
        
        try {
            const response = await fetch(`http://localhost:${FORGET_PASSWORD_SERVER_PORT}/reset_password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: token,
                    newPassword: newPassword,
                    confirmPassword: confirmPassword
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(result.message, 'success');
                resetModal.style.display = 'none';
                resetPasswordForm.reset();
                
                // Clear stored tokens
                localStorage.removeItem('resetToken');
                localStorage.removeItem('resetEmail');
                
                // Redirect to login page after successful reset
                setTimeout(() => {
                    window.location.href = '../Loginpage/loginpage.html';
                }, 2000);
            } else {
                showMessage(result.message, 'error');
            }
        } catch (error) {
            showMessage('Error resetting password: ' + error.message, 'error');
        }
    });

    // Modal functionality
    closeModal.addEventListener('click', function() {
        resetModal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === resetModal) {
            resetModal.style.display = 'none';
        }
    });

    function showMessage(message, type) {
        messageDiv.textContent = message;
        messageDiv.className = 'message ' + type;
        messageDiv.style.display = 'block';
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }

    function showResetModal(email, token) {
        document.getElementById('resetEmail').value = email;
        document.getElementById('resetToken').value = token;
        resetModal.style.display = 'block';
    }

    // Check if token is present in URL (for actual reset flow)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const emailParam = urlParams.get('email');
    
    if (token && emailParam) {
        // Validate token before showing reset modal
        validateToken(token, emailParam);
    }

    async function validateToken(token, email) {
        try {
            const response = await fetch(`http://localhost:${FORGET_PASSWORD_SERVER_PORT}/validate_token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: token })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showResetModal(email, token);
            } else {
                showMessage('Invalid or expired reset link', 'error');
            }
        } catch (error) {
                        showMessage('Error validating reset link: ' + error.message, 'error');
                    }
                }
            });