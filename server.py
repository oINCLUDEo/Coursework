import json
import socket
import threading
import sqlite3


def register_user(username, password):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()

    try:
        info = cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        if info.fetchone() is None:
            # Делаем когда нету человека в бд
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return True
        else:
            # Делаем когда есть человек в бд
            conn.close()
            return False
    except sqlite3.IntegrityError:
        conn.close()
        return False


def check_credentials(username, password):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user is not None


def save_message_to_db(username, message):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
    conn.commit()
    conn.close()


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
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                save_message_to_db(username, message)
                chat_history.append((len(chat_history) + 1, username, message))
                broadcast(f"{username}: {message}")
        except Exception as e:
            print(f"Ошибка: {e}")
            break


def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            clients.remove(client)
            client.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 9090))
server.listen(100)

clients = []


def accept_clients():
    while True:
        client_socket, addr = server.accept()
        option = client_socket.recv(1024).decode('utf-8')

        if option.lower() == "login":
            data = client_socket.recv(4096).decode('utf-8')
            username, password = json.loads(data)

            global name
            name = username
            if check_credentials(username, password):
                clients.append(client_socket)
                client_socket.send("Login successful".encode('utf-8'))
                print(f"{username} connected")

                threading.Thread(target=handle_client, args=(client_socket, username)).start()
            else:
                client_socket.send("Введены неверные данные".encode('utf-8'))
        elif option.lower() == "register":
            data = client_socket.recv(4096).decode('utf-8')
            username, password = json.loads(data)
            if register_user(username, password):
                client_socket.send("Регистрация выполнена успешно".encode('utf-8'))
            else:
                client_socket.send("Имя пользователя занято :(".encode('utf-8'))


threading.Thread(target=accept_clients).start()
