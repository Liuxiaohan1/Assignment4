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