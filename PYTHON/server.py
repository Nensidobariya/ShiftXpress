import socket
import threading
import sys
import os

# Add the PYTHON folder to the path so imports work correctly
sys.path.append(os.path.dirname(__file__))

from request_handler import RequestHandler

class HTTPServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.handler = RequestHandler()
        self.socket = None
        self.running = False
    
    def start(self):
        """Start the HTTP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1)  # Add timeout for graceful shutdown
            
            self.running = True
            print(f"🚀 Server running on http://{self.host}:{self.port}")
            print("📝 Available endpoints:")
            print("   POST /api/signup - User registration")
            print("   POST /api/login - User login")
            print("   POST /api/check-email - Check email existence")
            print("   GET /api/health - Health check")
            print("\nPress Ctrl+C to stop the server")
            print("=" * 50)
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"🔗 Connection from {client_address}")
                    
                    # Handle each connection in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue  # Timeout is normal, continue running
                except Exception as e:
                    if self.running:
                        print(f"⚠️ Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            print("💡 Check if port 5000 is already in use")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """Handle client connection"""
        try:
            # Receive request data with larger buffer
            request_data = b""
            client_socket.settimeout(5.0)
            
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                request_data += chunk
                if b"\r\n\r\n" in request_data:
                    break
            
            if not request_data:
                client_socket.close()
                return
            
            request_text = request_data.decode('utf-8', errors='ignore')
            print(f"📨 Received request: {request_text.splitlines()[0] if request_text else 'Empty'}")
            
            # Handle CORS preflight requests
            if 'OPTIONS' in request_text:
                response = self.handle_cors_preflight()
                client_socket.send(response.encode('utf-8'))
            else:
                # Process the request
                response = self.handler.handle_request(request_text)
                client_socket.send(response.encode('utf-8'))
                
        except socket.timeout:
            print("⏰ Client connection timeout")
        except Exception as e:
            print(f"❌ Error handling client: {e}")
            try:
                error_response = self.handler.error_response(500, "Internal Server Error")
                client_socket.send(error_response.encode('utf-8'))
            except:
                pass
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def handle_cors_preflight(self):
        """Handle CORS preflight requests"""
        response = "HTTP/1.1 204 No Content\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n"
        response += "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
        response += "Content-Length: 0\r\n"
        response += "\r\n"
        return response
    
    def stop(self):
        """Stop the server"""
        print("🛑 Stopping server...")
        self.running = False
        if self.socket:
            self.socket.close()
        print("✅ Server stopped successfully")

if __name__ == '__main__':
    # Check if port is available
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex(('127.0.0.1', 5000)) == 0:
                print("❌ Port 5000 is already in use!")
                print("💡 Try: netstat -ano | findstr :5000 (Windows) or lsof -i :5000 (Mac/Linux)")
                exit(1)
    except:
        pass
    
    server = HTTPServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal - Shutting down gracefully...")
        server.stop()