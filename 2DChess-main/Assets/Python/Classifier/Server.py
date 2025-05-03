import socket
import EEGController
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
    eeg = EEGController.EEGController(debug=False)
    print(f"Connected by {address}")
    
    clientsocket.send(bytes("Python Server Connected", "utf-8"))

    while True:
        time.sleep(0.1)
        data = clientsocket.recv(1024)
        
        if not data:
            break
        
        if (data.decode() == "STOP"):
            print("GOT STOP")
            eeg.setMarker(start=False)
            selection = eeg.evaluate()
            clientsocket.send(bytes(str(selection), "utf-8"))
            
        if (data.decode() == "START"):
            print("GOT START")
            eeg.setMarker(start=True)
            clientsocket.send(bytes("Got Start", "utf-8"))
            
            
    print("Connection Terminated")
    eeg.close()