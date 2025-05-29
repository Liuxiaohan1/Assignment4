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