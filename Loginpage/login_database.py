import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
import time

class LoginDatabase:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'user_management'
        }
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Initialize database with reset tokens table"""
        try:
            if self.connect():
                cursor = self.connection.cursor()
                
                # Create password reset tokens table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS password_reset_tokens (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        email VARCHAR(255) NOT NULL,
                        token VARCHAR(255) NOT NULL UNIQUE,
                        expires_at TIMESTAMP NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
                    )
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_tokens_token ON password_reset_tokens(token)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_tokens_email ON password_reset_tokens(email)
                ''')
                
                self.connection.commit()
                cursor.close()
                print("✅ Password reset tokens table initialized")
        except Error as e:
            print(f"❌ Database initialization error: {e}")
    
    def connect(self):
        """Create database connection"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                print("✅ Login Database connected successfully")
            return True
        except Error as e:
            print(f"❌ Login Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login_user(self, email, password):
        """Authenticate user login"""
        try:
            if not self.connect():
                return False, "Database connection failed", None
            
            cursor = self.connection.cursor(dictionary=True)
            hashed_password = self.hash_password(password)
            
            cursor.execute(
                "SELECT id, name, email, phone FROM users WHERE email = %s AND password = %s",
                (email, hashed_password)
            )
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                return True, "Login successful", user
            else:
                return False, "Invalid email or password", None
                
        except Error as e:
            return False, f"Database error: {str(e)}", None
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
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