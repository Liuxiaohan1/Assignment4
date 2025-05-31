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
        except ValueError:
            print(f"Error: Invalid filesize({parts[3]}) or port({parts[5]})")
            return False       
        print(f"Downloading {filename} ({filesize} bytes)")
        
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        with open(local_filename, 'wb') as f:
            bytes_received = 0
            block_size = 1000
            stars_printed = 0
            while bytes_received < filesize:
                start = bytes_received
                end = min(start + block_size - 1, filesize - 1)
                request = f"FILE {filename} GET START {start} END {end}"
                response = reliable_send_receive(data_sock, request, (server_addr, port))
                if not response.startswith("FILE") or "OK" not in response:
                    print(f"\nError: Invalid data response: {response}")
                    return False
                resp_parts = response.split()
                data_start = int(resp_parts[4])
                data_end = int(resp_parts[6])
                encoded_data = ' '.join(resp_parts[8:])
                chunk = base64.b64decode(encoded_data.encode())

                f.seek(data_start)
                f.write(chunk)
                bytes_received += len(chunk)

                progress = bytes_received / filesize
                new_stars = int(progress * 10)
                if new_stars > stars_printed:
                    print(f"\rProgress: {bytes_received}/{filesize} bytes [{'*' * new_stars}]", 
                          end='', flush=True)
                    stars_printed = new_stars 
                    print(f"\rProgress: {bytes_received}/{filesize} bytes [{'*' * 10}]")
                    close_resp = reliable_send_receive(data_sock, f"FILE {filename} CLOSE", (server_addr, port))
            if not close_resp.startswith("FILE") or "CLOSE_OK" not in close_resp:
                print("Warning: Abnormal close response")
        
        print(f"File {filename} downloaded successfully\n")
        return True
    except Exception as e:
        print(f"\nDownload failed: {str(e)}")
        return False
    finally:
        sock.close()  
        if 'data_sock' in locals():
            data_sock.close()          
