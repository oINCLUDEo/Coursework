import socket
import threading

# Dictionary to store user credentials (replace this with a proper authentication system)
user_credentials = {
    "user1": "password1",
    "user2": "password2",
    "user3": "password3"
}


# Function to handle client connection
def handle_client(client_socket, username):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                broadcast(f"{username}: {message}")
        except:
            break


# Function to broadcast messages to all clients
def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))


# Start the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 9999))
server.listen()

clients = []

print("Server is running...")

while True:
    client_socket, addr = server.accept()
    username = client_socket.recv(1024).decode('utf-8')

    if username in user_credentials:
        password = client_socket.recv(1024).decode('utf-8')
        if password == user_credentials[username]:
            clients.append(client_socket)
            client_socket.send("Вход выполнен успешно".encode('utf-8'))
            print(f"{username} connected")
            threading.Thread(target=handle_client, args=(client_socket, username)).start()
        else:
            client_socket.send("Invalid credentials".encode('utf-8'))
            client_socket.close()
    else:
        client_socket.send("User not found".encode('utf-8'))
        client_socket.close()
