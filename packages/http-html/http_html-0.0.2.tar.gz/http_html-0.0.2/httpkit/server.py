# httpkit/server.py
import socket
from .router import Router
from .request import Request

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.router = Router()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)

    def route(self, path, method):
        return self.router.add_route(path, method)

    def run(self):
        print(f"الخادم يعمل على http://{self.host}:{self.port}")
        while True:
            client_connection, client_address = self.server_socket.accept()
            request = client_connection.recv(1024).decode()
            
            req = Request(request)
            handler = self.router.find_handler(req.path, req.method)
            
            if handler:
                handler(client_connection, req)
            else:
                # إرسال استجابة 404 إذا لم يتم العثور على المسار
                not_found_response = b"HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\n\r\nNot Found"
                client_connection.sendall(not_found_response)
            
            client_connection.close()
