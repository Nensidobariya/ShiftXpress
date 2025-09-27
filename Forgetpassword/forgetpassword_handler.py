import json
from forgetpassword_database import ForgetPasswordDatabase

class ForgetPasswordRequestHandler:
    def __init__(self):
        self.db = ForgetPasswordDatabase()
        self.routes = {
            'POST': {
                '/send_reset_link': self.handle_send_reset_link,
                '/reset_password': self.handle_reset_password,
                '/validate_token': self.handle_validate_token
            },
            'GET': {
                '/': self.handle_root,
                '/health': self.handle_health
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
        
        print(f"🔄 Forget Password Server: Handling {method} {path}")
        
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
            "message": "Welcome to Forget Password API",
            "endpoints": {
                "POST /send_reset_link": "Send password reset link",
                "POST /reset_password": "Reset password with token",
                "POST /validate_token": "Validate reset token",
                "GET /health": "Health check"
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
    
    def handle_send_reset_link(self, request):
        """Handle sending password reset link"""
        try:
            if not request['body']:
                return self.error_response(400, "No data provided")
            
            data = json.loads(request['body'])
            email = data.get('email', '').strip().lower()
            
            print(f"📧 Password reset request for: {email}")
            
            if not email:
                return self.error_response(400, "Email is required")
            
            # Create reset token
            success, result = self.db.create_reset_token(email)
            
            if success:
                print(f"✅ Reset token created for: {email}")
                # In a real application, you would send an email here
                # For demo purposes, we'll return the token
                return self.json_response(200, {
                    "success": True,
                    "message": "Password reset link sent successfully",
                    "token": result,  # Remove this in production
                    "reset_url": f"http://localhost:8083/reset.html?token={result}&email={email}"
                })
            else:
                print(f"❌ Failed to create reset token for: {email}")
                return self.json_response(400, {
                    "success": False,
                    "message": result
                })
                
        except json.JSONDecodeError:
            return self.error_response(400, "Invalid JSON data")
        except Exception as e:
            print(f"❌ Server error in send_reset_link: {e}")
            return self.error_response(500, f"Server error: {str(e)}")
    
    def handle_reset_password(self, request):
        """Handle password reset"""
        try:
            if not request['body']:
                return self.error_response(400, "No data provided")
            
            data = json.loads(request['body'])
            token = data.get('token', '')
            new_password = data.get('newPassword', '')
            confirm_password = data.get('confirmPassword', '')
            
            if not token or not new_password or not confirm_password:
                return self.error_response(400, "All fields are required")
            
            if new_password != confirm_password:
                return self.error_response(400, "Passwords do not match")
            
            if len(new_password) < 6:
                return self.error_response(400, "Password must be at least 6 characters")
            
            # Reset password
            success, message = self.db.reset_password(token, new_password)
            
            if success:
                print(f"✅ Password reset successful for token: {token}")
                return self.json_response(200, {
                    "success": True,
                    "message": message
                })
            else:
                print(f"❌ Password reset failed for token: {token}")
                return self.json_response(400, {
                    "success": False,
                    "message": message
                })
                
        except json.JSONDecodeError:
            return self.error_response(400, "Invalid JSON data")
        except Exception as e:
            print(f"❌ Server error in reset_password: {e}")
            return self.error_response(500, f"Server error: {str(e)}")
    
    def handle_validate_token(self, request):
        """Validate reset token"""
        try:
            if not request['body']:
                return self.error_response(400, "No data provided")
            
            data = json.loads(request['body'])
            token = data.get('token', '')
            
            if not token:
                return self.error_response(400, "Token is required")
            
            # Validate token
            valid, message, email = self.db.validate_reset_token(token)
            
            return self.json_response(200, {
                "success": valid,
                "message": message,
                "email": email if valid else None
            })
                
        except json.JSONDecodeError:
            return self.error_response(400, "Invalid JSON data")
        except Exception as e:
            print(f"❌ Server error in validate_token: {e}")
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