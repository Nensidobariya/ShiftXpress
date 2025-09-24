import json
from database import Database

class RequestHandler:
    def __init__(self):
        self.db = Database()
        self.routes = {
            'POST': {
                '/api/signup': self.handle_signup,
                '/api/login': self.handle_login,
                '/api/check-email': self.handle_check_email
            },
            'GET': {
                '/': self.handle_root,
                '/api/health': self.handle_health
            }
        }
    
    def parse_request(self, request_data):
        """Parse HTTP request"""
        try:
            lines = request_data.split('\r\n')
            if not lines:
                return None
            
            # Parse request line
            request_line = lines[0]
            method, path, _ = request_line.split(' ')
            
            # Parse headers
            headers = {}
            body = None
            body_start = False
            
            for line in lines[1:]:
                if not line:
                    body_start = True
                    continue
                
                if not body_start:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
                else:
                    body = line
                    break
            
            return {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body
            }
        except Exception as e:
            print(f"Error parsing request: {e}")
            return None
    
    def handle_request(self, request_data):
        """Handle incoming request and return response"""
        request = self.parse_request(request_data)
        if not request:
            return self.error_response(400, "Bad Request")
        
        method = request['method']
        path = request['path']
        
        # Route handling
        if method in self.routes and path in self.routes[method]:
            return self.routes[method][path](request)
        else:
            return self.error_response(404, "Not Found")
    
    def handle_root(self, request):
        """Handle root path"""
        response_data = {
            "message": "Welcome to User Management API",
            "endpoints": {
                "POST /api/signup": "User registration",
                "POST /api/login": "User login",
                "POST /api/check-email": "Check email existence"
            }
        }
        return self.json_response(200, response_data)
    
    def handle_health(self, request):
        """Health check endpoint"""
        db_connected = self.db.connect()
        return self.json_response(200, {"status": "healthy", "database": "connected" if db_connected else "disconnected"})
    
    def handle_signup(self, request):
        """Handle user registration"""
        try:
            if not request['body']:
                return self.error_response(400, "No data provided")
            
            data = json.loads(request['body'])
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirmPassword', '')
            
            # Validation
            if not all([name, email, phone, password, confirm_password]):
                return self.error_response(400, "All fields are required")
            
            if password != confirm_password:
                return self.error_response(400, "Passwords do not match")
            
            if len(password) < 6:
                return self.error_response(400, "Password must be at least 6 characters")
            
            # Register user
            success, message = self.db.register_user(name, email, phone, password)
            
            if success:
                return self.json_response(201, {"success": True, "message": message})
            else:
                return self.json_response(400, {"success": False, "message": message})
                
        except json.JSONDecodeError:
            return self.error_response(400, "Invalid JSON data")
        except Exception as e:
            return self.error_response(500, f"Server error: {str(e)}")
    
    def handle_login(self, request):
        """Handle user login"""
        try:
            if not request['body']:
                return self.error_response(400, "No data provided")
            
            data = json.loads(request['body'])
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return self.error_response(400, "Email and password are required")
            
            # Authenticate user
            success, message, user = self.db.login_user(email, password)
            
            if success:
                return self.json_response(200, {
                    "success": True, 
                    "message": message,
                    "user": user
                })
            else:
                return self.json_response(401, {
                    "success": False, 
                    "message": message
                })
                
        except json.JSONDecodeError:
            return self.error_response(400, "Invalid JSON data")
        except Exception as e:
            return self.error_response(500, f"Server error: {str(e)}")
    
    def handle_check_email(self, request):
        """Check if email exists"""
        try:
            if not request['body']:
                return self.error_response(400, "No data provided")
            
            data = json.loads(request['body'])
            email = data.get('email', '').strip().lower()
            
            exists = self.db.check_email_exists(email)
            return self.json_response(200, {"exists": exists})
            
        except json.JSONDecodeError:
            return self.error_response(400, "Invalid JSON data")
        except Exception as e:
            return self.error_response(500, f"Server error: {str(e)}")
    
    def json_response(self, status_code, data):
        """Create JSON response"""
        response_json = json.dumps(data)
        response = f"HTTP/1.1 {status_code} {'OK' if status_code == 200 else 'Error'}\r\n"
        response += "Content-Type: application/json\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        response += "Access-Control-Allow-Headers: Content-Type\r\n"
        response += f"Content-Length: {len(response_json)}\r\n"
        response += "\r\n"
        response += response_json
        return response
    
    def error_response(self, status_code, message):
        """Create error response"""
        return self.json_response(status_code, {
            "success": False,
            "error": message,
            "status_code": status_code
        })