import socket
import threading
import os

connected_clients = []

def handle_client(conn, addr):
    print(f"[New Connection] {addr} connected.")
    connected_clients.append(conn)
    
    while True:
        try:
            # We increased this to 4096 to handle large files and images much faster!
            data = conn.recv(4096)
            if not data:
                break
                
            # Broadcast to everyone else
            for client in connected_clients:
                if client != conn:
                    try:
                        client.sendall(data)
                    except:
                        # If a client disconnected unexpectedly, remove them
                        connected_clients.remove(client)
        except Exception as e:
            break
            
    print(f"[Diconnected] {addr} left.")
    if conn in connected_clients:
        connected_clients.remove(conn)
    conn.close()

def start_server():
    # Use Railway's port or default to 65432 for local testing
    port = int(os.environ.get("PORT", 50000))
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on port {port}")
    
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

# This is the line we discussed! It safely starts the server.
if __name__ == "__main__":
    start_server()