import socket
import threading
from request_handler import RequestHandler

class HTTPServer:
    def __init__(self, host='localhost', port=5000):
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
            
            self.running = True
            print(f"🚀 Server running on http://{self.host}:{self.port}")
            print("📝 Available endpoints:")
            print("   POST /api/signup - User registration")
            print("   POST /api/login - User login")
            print("   POST /api/check-email - Check email existence")
            print("   GET /api/health - Health check")
            print("\nPress Ctrl+C to stop the server")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"🔗 Connection from {client_address}")
                    
                    # Handle each connection in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"Failed to start server: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket):
        """Handle client connection"""
        try:
            # Receive request data
            request_data = client_socket.recv(1024).decode('utf-8')
            
            if not request_data:
                return
            
            print(f"📨 Received request: {request_data.splitlines()[0] if request_data else 'Empty'}")
            
            # Handle CORS preflight requests
            if 'OPTIONS' in request_data:
                response = self.handle_cors_preflight()
                client_socket.send(response.encode('utf-8'))
            else:
                # Process the request
                response = self.handler.handle_request(request_data)
                client_socket.send(response.encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client: {e}")
            error_response = self.handler.error_response(500, "Internal Server Error")
            client_socket.send(error_response.encode('utf-8'))
        finally:
            client_socket.close()
    
    def handle_cors_preflight(self):
        """Handle CORS preflight requests"""
        response = "HTTP/1.1 200 OK\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        response += "Access-Control-Allow-Headers: Content-Type\r\n"
        response += "Content-Length: 0\r\n"
        response += "\r\n"
        return response
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("🛑 Server stopped")

if __name__ == '__main__':
    server = HTTPServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.stop()