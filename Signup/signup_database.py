import sqlite3
import hashlib
import re
import secrets
import time
from datetime import datetime

class SignupDB:
    def __init__(self, db_path="../user_database.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with users table and enable foreign keys"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys for proper relationship with reset_tokens table
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tokens_token ON password_reset_tokens (token)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tokens_email ON password_reset_tokens (email)
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully with password reset support")

    # ... (keep all existing validation methods) ...

    def create_reset_token(self, email):
        """Create a password reset token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if email exists
            if not self.get_user_by_email(email):
                conn.close()
                return False, "Email not found"
            
            # Clean up expired tokens
            self.cleanup_expired_tokens()
            
            # Generate unique token
            token = secrets.token_urlsafe(32)
            expires_at = time.time() + 3600  # 1 hour from now
            
            cursor.execute('''
                INSERT INTO password_reset_tokens (email, token, expires_at) 
                VALUES (?, ?, ?)
            ''', (email, token, expires_at))
            
            conn.commit()
            conn.close()
            
            return True, token
            
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"

    def validate_reset_token(self, token):
        """Validate reset token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email, expires_at, used 
                FROM password_reset_tokens 
                WHERE token = ?
            ''', (token,))
            
            token_data = cursor.fetchone()
            conn.close()
            
            if not token_data:
                return False, "Invalid token", None
            
            if token_data[2]:  # used field
                return False, "Token already used", None
            
            # Check if token is expired
            if time.time() > token_data[1]:
                return False, "Token expired", None
            
            return True, "Token valid", token_data[0]
            
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}", None

    def reset_password(self, token, new_password):
        """Reset user password using token"""
        try:
            # Validate token
            valid, message, email = self.validate_reset_token(token)
            if not valid:
                return False, message
            
            # Validate password
            valid_password, password_msg = self.validate_password(new_password)
            if not valid_password:
                return False, password_msg
            
            # Update password
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET password = ? WHERE email = ?
            ''', (hashed_password, email))
            
            # Mark token as used
            cursor.execute('''
                UPDATE password_reset_tokens SET used = TRUE WHERE token = ?
            ''', (token,))
            
            conn.commit()
            conn.close()
            
            return True, "Password reset successfully"
            
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"

    def cleanup_expired_tokens(self):
        """Clean up expired reset tokens"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM password_reset_tokens 
                WHERE expires_at < ? OR used = TRUE
            ''', (time.time(),))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Error cleaning up tokens: {e}")

    # ... (keep all other existing methods) ...