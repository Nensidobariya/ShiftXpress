import json
from login_database import LoginDatabase

class LoginRequestHandler:
    def __init__(self):
        self.db = LoginDatabase()
        self.routes = {
            'POST': {
                '/api/login': self.handle_login,
            },
            'GET': {
                '/': self.handle_root,
                '/api/health': self.handle_health
            }
        }
    
    def parse_request(self, request_data):
        """Parse HTTP request"""
        try:
            if not request_data or not request_data.strip():
                return None
            
            lines = request_data.strip().split('\r\n')
            if not lines:
                return None
            
            request_line = lines[0]
            parts = request_line.split(' ')
            if len(parts) < 3:
                return None
                
            method, path, _ = parts[0], parts[1], parts[2]
            
            headers = {}
            body = None
            i = 1
            
            while i < len(lines) and lines[i].strip():
                if ':' in lines[i]:
                    key, value = lines[i].split(':', 1)
                    headers[key.strip()] = value.strip()
                i += 1
            
            if i + 1 < len(lines):
                body = '\r\n'.join(lines[i+1:])
            
            return {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body
            }
        except Exception as e:
            print(f"❌ Error parsing request: {e}")
            return None
    
    def handle_request(self, request_data):
        """Handle incoming request and return response"""
        request = self.parse_request(request_data)
        if not request:
            return self.error_response(400, "Bad Request")
        
        method = request['method']
        path = request['path']
        
        print(f"🔄 Login Server: Handling {method} {path}")
        
        if method in self.routes:
            if path in self.routes[method]:
                return self.routes[method][path](request)
            else:
                return self.error_response(404, f"Endpoint {path} not found")
        else:
            return self.error_response(405, f"Method {method} not allowed")
    
    def handle_root(self, request):
        """Handle root path"""
        response_data = {
            "success": True,
            "message": "Welcome to Login API",
            "endpoints": {
                "POST /api/login": "User login",
                "GET /api/health": "Health check"
            }
        }
        return self.json_response(200, response_data)
    
    def handle_health(self, request):
        """Health check endpoint"""
        db_connected = self.db.connect()
        return self.json_response(200, {
            "success": True,
            "status": "healthy",
            "database": "connected" if db_connected else "disconnected"
        })
    
    def handle_login(self, request):
        """Handle user login"""
        try:
            if not request['body']:
                return self.error_response(400, "No data provided")
            
            data = json.loads(request['body'])
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            print(f"🔐 Login attempt for: {email}")
            
            if not email or not password:
                return self.error_response(400, "Email and password are required")
            
            success, message, user = self.db.login_user(email, password)
            
            if success:
                print(f"✅ Login successful for: {email}")
                return self.json_response(200, {
                    "success": True, 
                    "message": message,
                    "user": user
                })
            else:
                print(f"❌ Login failed for: {email}")
                return self.json_response(401, {
                    "success": False, 
                    "message": message
                })
                
        except json.JSONDecodeError:
            return self.error_response(400, "Invalid JSON data")
        except Exception as e:
            print(f"❌ Server error in login: {e}")
            return self.error_response(500, f"Server error: {str(e)}")
    
    def json_response(self, status_code, data):
        """Create JSON response"""
        response_json = json.dumps(data)
        response = f"HTTP/1.1 {status_code} {'OK' if status_code == 200 else 'Error'}\r\n"
        response += "Content-Type: application/json\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        response += "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
        response += f"Content-Length: {len(response_json)}\r\n"
        response += "Connection: close\r\n"
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