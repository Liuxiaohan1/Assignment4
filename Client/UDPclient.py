import socket  
import base64  
import os
def reliable_send_receive(sock, message, addr, max_retries=5, initial_timeout=1.0):
    """Reliable UDP send/receive with retry mechanism"""
    timeout = initial_timeout
    for attempt in range(max_retries):
        try:
            sock.sendto(message.encode(), addr)
            sock.settimeout(timeout)
            data, _ = sock.recvfrom(65536)
            return data.decode()
        except socket.timeout: 
            print(f"Timeout (attempt {attempt + 1}/{max_retries}), retrying...")
            timeout *= 2    
    raise ConnectionError(f"Failed after {max_retries} attempts")
def download_file(server_addr, server_port, filename, local_filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        response = reliable_send_receive(sock, f"DOWNLOAD {filename}", (server_addr, server_port))
        print("CLIENT DEBUG: Received ->", response)
        parts = response.strip().split()
        if len(parts) != 6:  
            print(f"Error: Response needs 6 fields, got {len(parts)} -> {parts}")
            return False
        if parts[0] != "OK" or parts[2] != "SIZE" or parts[4] != "PORT":
            print("Error: Missing protocol keywords (expected OK/SIZE/PORT)")
            return False
        try:
            filesize = int(parts[3])  
            port = int(parts[5])     
