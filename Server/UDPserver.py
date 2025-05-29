import socket
import threading
import os
import random
import base64

class FileServerThread(threading.Thread):
    def __init__(self, filename, client_addr, server_port):
        threading.Thread.__init__(self)
        self.filename = filename
        self.client_addr = client_addr
        self.port = random.randint(50000, 51000)
        self.filepath = os.path.join(os.getcwd(), filename)  
    def run(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.bind(('0.0.0.0', self.port))
            filesize = os.path.getsize(self.filepath)
            response = f"OK {self.filename} SIZE {filesize} PORT {self.port}"
            print("SERVER DEBUG: Sending ->", response)
            client_socket.sendto(response.encode(), self.client_addr)

            with open(self.filepath, 'rb') as f:
                while True:
                    data, addr = client_socket.recvfrom(1024)
                    parts = data.decode().strip().split()
                    if not parts or parts[0] != "FILE":
                        continue
                    if parts[2] == "GET": 
                       start, end = int(parts[4]), int(parts[6])
                       f.seek(start)
                       chunk = f.read(end - start + 1)
                       encoded = base64.b64encode(chunk).decode()
                       response = f"FILE {self.filename} OK START {start} END {end} DATA {encoded}"
                       client_socket.sendto(response.encode(), addr)
                    elif parts[2] == "CLOSE":
                        response = f"FILE {self.filename} CLOSE_OK"
                        client_socket.sendto(response.encode(), addr)
                        break 
        except FileNotFoundError:
            response = f"ERR {self.filename} NOT_FOUND" 
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_socket.sendto(response.encode(), self.client_addr)
            temp_socket.close()
        finally:
            if 'client_socket' in locals(): 
                client_socket.close()
    def main(port):
        if not (1024 <= port <= 65535):
           print("Port must be between 1024 and 65535")
           return
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', port))
        print(f"Server started on port {port}")           