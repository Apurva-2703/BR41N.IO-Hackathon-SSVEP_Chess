import socket
import EEGDataCollector
import time

# Set up a TCP server
HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port number
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
print("Waiting for connection...")

while True:
    
    # Wait for client socket
    clientsocket, address = sock.accept()
    eeg = EEGDataCollector.EEGDataCollector(debug=True)
    print(f"Connected by {address}")
    
    clientsocket.send(bytes("Python Server Connected", "utf-8"))

    while True:
        time.sleep(0.1)
        data = clientsocket.recv(1024)
        
        if not data:
            break
        
        message = data.decode()
        print(message)
        clientsocket.send(bytes(message, "utf-8"))
        eeg.setMarker(message)
            
    print("Connection Terminated")
    eeg.close()