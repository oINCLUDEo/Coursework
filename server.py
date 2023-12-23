import socket
import threading
import sqlite3


# Function to check user credentials from the SQLite database
def check_credentials(username, password):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user is not None


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

    password = client_socket.recv(1024).decode('utf-8')

    if not check_credentials(username, password):
        clients.append(client_socket)
        client_socket.send("Вход выполнен успешно".encode('utf-8'))
        print(f"{username} connected")
        threading.Thread(target=handle_client, args=(client_socket, username)).start()
    else:
        client_socket.send("Invalid credentials".encode('utf-8'))
        client_socket.close()
