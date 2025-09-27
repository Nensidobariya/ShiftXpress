import socket
import threading
import sys
import os

sys.path.append(os.path.dirname(__file__))

from forgetpassword_handler import ForgetPasswordRequestHandler

class ForgetPasswordServer:
    def __init__(self, host='127.0.0.1', port=8083):
        self.host = host
        self.port = port
        self.handler = ForgetPasswordRequestHandler()
        self.socket = None
        self.running = False
    
    def start(self):
        """Start the Forget Password server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1)
            
            self.running = True
            print(f"🚀 Forget Password Server running on http://{self.host}:{self.port}")
            print("📝 Available endpoints:")
            print("   POST /send_reset_link - Send password reset link")
            print("   POST /reset_password - Reset password with token")
            print("   POST /validate_token - Validate reset token")
            print("   GET /health - Health check")
            print("\nPress Ctrl+C to stop the server")
            print("=" * 50)
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"🔗 Forget Password Server: Connection from {client_address}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️ Forget Password Server Error: {e}")
                        
        except Exception as e:
            print(f"❌ Failed to start Forget Password Server: {e}")
            print("💡 Check if port 8083 is already in use")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """Handle client connection"""
        try:
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
            
            if 'OPTIONS' in request_text:
                response = self.handle_cors_preflight()
                client_socket.send(response.encode('utf-8'))
            else:
                response = self.handler.handle_request(request_text)
                client_socket.send(response.encode('utf-8'))
                
        except socket.timeout:
            print("⏰ Forget Password Server: Client connection timeout")
        except Exception as e:
            print(f"❌ Forget Password Server Error handling client: {e}")
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
        response += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        response += "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
        response += "Content-Length: 0\r\n"
        response += "\r\n"
        return response
    
    def stop(self):
        """Stop the server"""
        print("🛑 Stopping Forget Password Server...")
        self.running = False
        if self.socket:
            self.socket.close()
        print("✅ Forget Password Server stopped successfully")

if __name__ == '__main__':
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex(('127.0.0.1', 8083)) == 0:
                print("❌ Port 8083 is already in use!")
                exit(1)
    except:
        pass
    
    server = ForgetPasswordServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal - Shutting down Forget Password Server...")
        server.stop()