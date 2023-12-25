import json
import socket
import threading
import sqlite3
import time


# Functions for database and user handling (create_database, register_user, check_credentials) remain unchanged
def register_user(username, password):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()

    try:
        print('скул передает привет')
        info = cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        if info.fetchone() is None:
            # Делаем когда нету человека в бд
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            print('скул работает')
            conn.commit()
            conn.close()
            return True
        else:
            # Делаем когда есть человек в бд
            print('скул передает привет2')
            conn.close()
            return False
    except sqlite3.IntegrityError:
        print('скул нашел ошибку')
        conn.close()
        return False


def check_credentials(username, password):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user is not None


def create_chat_history_table():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    message TEXT
                )''')
    conn.commit()
    conn.close()


# Function to save messages to the database
def save_message_to_db(username, message):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
    conn.commit()
    conn.close()


# Function to retrieve chat history from the database
def retrieve_chat_history(client_socket):
    global chat_history
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM messages")
    history = c.fetchall()
    json_messages = json.dumps(history)
    client_socket.sendall(json_messages.encode())
    chat_history = history
    conn.close()


def handle_client(client_socket, username):
    retrieve_chat_history(client_socket)
    print('прилет')
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                save_message_to_db(username, message)
                chat_history.append((len(chat_history) + 1, username, message))
                broadcast(f"{username}: {message}")
        except Exception as e:
            print(f"Error: {e}")
            break


def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            clients.remove(client)
            client.close()


# Server setup
create_chat_history_table()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('192.168.0.107', 9090))
server.listen(100)

# List to store connected clients
clients = []


# Load chat history from the database


# Accept and handle client connections
def accept_clients():
    while True:
        client_socket, addr = server.accept()
        option = client_socket.recv(1024).decode('utf-8')

        if option.lower() == "login":
            username = client_socket.recv(1024).decode('utf-8')
            password = client_socket.recv(1024).decode('utf-8')

            global name
            name = username
            if check_credentials(username, password):
                clients.append(client_socket)
                client_socket.send("Login successful".encode('utf-8'))
                print(f"{username} connected")

                threading.Thread(target=handle_client, args=(client_socket, username)).start()
            else:
                client_socket.send("Invalid credentials".encode('utf-8'))
                client_socket.close()
        elif option.lower() == "register":
            username = client_socket.recv(1024).decode('utf-8')
            password = client_socket.recv(1024).decode('utf-8')

            if register_user(username, password):
                client_socket.send("Registration successful".encode('utf-8'))
            else:
                client_socket.send("Username already exists".encode('utf-8'))
                client_socket.close()


# Rest of the server code remains the same

# Create a separate thread to accept incoming connections
threading.Thread(target=accept_clients).start()
