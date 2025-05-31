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