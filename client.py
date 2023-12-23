import tkinter as tk
from tkinter import messagebox
import socket
import threading


def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                chat_text.insert(tk.END, message + '\n')
        except:
            break


def send_message():
    message = message_entry.get()
    if message:
        client_socket.send(message.encode('utf-8'))
        message_entry.delete(0, tk.END)


def login():
    username = username_entry.get()
    password = password_entry.get()

    client_socket.send(username.encode('utf-8'))
    client_socket.send(password.encode('utf-8'))

    response = client_socket.recv(1024).decode('utf-8')
    if response == "Вход выполнен успешно":
        login_window.destroy()
        open_chat(username)
    else:
        messagebox.showerror("Error", response)


def open_chat(username):
    chat_window = tk.Tk()
    chat_window.title(f"Chat - {username}")

    chat_label = tk.Label(chat_window, text=f"Welcome, {username}!", font=("Arial", 12))
    chat_label.pack(pady=10)

    global chat_text
    chat_text = tk.Text(chat_window, height=20, width=50)
    chat_text.pack()

    global message_entry
    message_entry = tk.Entry(chat_window, width=40)
    message_entry.pack(pady=10)

    send_button = tk.Button(chat_window, text="Send", command=send_message)
    send_button.pack()

    threading.Thread(target=receive_messages).start()

    chat_window.mainloop()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9999))

login_window = tk.Tk()
login_window.title("Login")

username_label = tk.Label(login_window, text="Username")
username_label.pack()

username_entry = tk.Entry(login_window)
username_entry.pack()

password_label = tk.Label(login_window, text="Password")
password_label.pack()

password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

login_button = tk.Button(login_window, text="Login", command=login)
login_button.pack(pady=10)

login_window.mainloop()
