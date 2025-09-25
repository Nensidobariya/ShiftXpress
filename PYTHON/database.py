import mysql.connector
from mysql.connector import Error
import hashlib

class Database:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Change this if you have MySQL password
            'database': 'user_management'
        }
        self.connection = None
    
    def connect(self):
        """Create database connection"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                print("✅ Database connected successfully")
            return True
        except Error as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, name, email, phone, password):
        """Register new user"""
        try:
            if not self.connect():
                return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                return False, "Email already registered"
            
            # Insert new user
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
                (name, email, phone, hashed_password)
            )
            self.connection.commit()
            cursor.close()
            
            return True, "Registration successful"
            
        except Error as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
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