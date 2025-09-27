import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
import time

class ForgetPasswordDatabase:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'user_management'
        }
        self.connection = None
    
    def connect(self):
        """Create database connection"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                print("✅ Forget Password Database connected successfully")
            return True
        except Error as e:
            print(f"❌ Forget Password Database connection error: {e}")
            return False
    
    def check_email_exists(self, email):
        """Check if email exists in database"""
        try:
            if not self.connect():
                return False
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            exists = cursor.fetchone() is not None
            cursor.close()
            
            return exists
            
        except Error as e:
            print(f"Error checking email: {e}")
            return False
    
    def create_reset_token(self, email):
        """Create a password reset token"""
        try:
            if not self.connect():
                return False, "Database connection failed"
            
            # Check if email exists
            if not self.check_email_exists(email):
                return False, "Email not found"
            
            # Clean up expired tokens
            self.cleanup_expired_tokens()
            
            # Generate unique token
            token = secrets.token_urlsafe(32)
            expires_at = time.time() + 3600  # 1 hour from now
            
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO password_reset_tokens (email, token, expires_at) VALUES (%s, %s, FROM_UNIXTIME(%s))",
                (email, token, expires_at)
            )
            
            self.connection.commit()
            cursor.close()
            
            return True, token
            
        except Error as e:
            return False, f"Database error: {str(e)}"
    
    def validate_reset_token(self, token):
        """Validate reset token"""
        try:
            if not self.connect():
                return False, "Database connection failed", None
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT email, expires_at, used FROM password_reset_tokens WHERE token = %s",
                (token,)
            )
            
            token_data = cursor.fetchone()
            cursor.close()
            
            if not token_data:
                return False, "Invalid token", None
            
            if token_data['used']:
                return False, "Token already used", None
            
            # Check if token is expired
            if time.time() > token_data['expires_at'].timestamp():
                return False, "Token expired", None
            
            return True, "Token valid", token_data['email']
            
        except Error as e:
            return False, f"Database error: {str(e)}", None
    
    def reset_password(self, token, new_password):
        """Reset user password using token"""
        try:
            if not self.connect():
                return False, "Database connection failed"
            
            # Validate token
            valid, message, email = self.validate_reset_token(token)
            if not valid:
                return False, message
            
            # Update password
            hashed_password = self.hash_password(new_password)
            
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (hashed_password, email)
            )
            
            # Mark token as used
            cursor.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
                (token,)
            )
            
            self.connection.commit()
            cursor.close()
            
            return True, "Password reset successfully"
            
        except Error as e:
            return False, f"Database error: {str(e)}"
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def cleanup_expired_tokens(self):
        """Clean up expired reset tokens"""
        try:
            if not self.connect():
                return
            
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM password_reset_tokens WHERE expires_at < NOW() OR used = TRUE"
            )
            self.connection.commit()
            cursor.close()
            
        except Error as e:
            print(f"Error cleaning up tokens: {e}")