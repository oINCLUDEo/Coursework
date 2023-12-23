import tkinter as tk
from tkinter import messagebox
import socket
import threading


def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                chat_text.config(state='normal')
                chat_text.insert(tk.END, message + '\n')
                chat_text.config(state='disabled')
        except:
            break


def send_message():
    message = message_entry.get()
    if message:
        client_socket.send(message.encode('utf-8'))
        message_entry.delete(0, tk.END)


def login(username, password):
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
    chat_window.title(f"Открыт чат для пользователя - {username}")

    chat_label = tk.Label(chat_window, text=f"Добро пожаловать, {username}!", font=("Segoe UI", 14), bg='#3300cc')
    chat_label.pack(pady=10)

    global chat_text
    chat_text = tk.Text(chat_window, height=20, width=50)
    chat_text.pack()
    chat_text.config(state='disabled')

    global message_entry
    message_entry = tk.Entry(chat_window, width=40)
    message_entry.pack(pady=10)

    send_button = tk.Button(chat_window, text="Send", command=send_message)
    send_button.pack()

    threading.Thread(target=receive_messages).start()

    chat_window.mainloop()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9999))


def log_window():
    def focus_in(e=None):
        login_button.configure(fg='#3300cc')  # Задаём кнопке нужные цвета
        login_button.configure(bg='#fff')

    def focus_out(e=None):
        login_button.configure(bg='#3300cc')
        login_button.configure(fg='#fff')

    global login_window
    login_window = tk.Tk()
    login_window.geometry('1000x750')  # Задаём размер
    login_window.title("Messenger")
    login_window.resizable(width=False, height=False)

    canvas = tk.Canvas(login_window, width=1000, height=750)
    canvas.pack()
    canvas.pack_propagate(False)
    img = tk.PhotoImage(file='back.gif')
    canvas.create_image(0, 0, anchor=tk.NW, image=img)

    auth_canvas = tk.Canvas(canvas, width=250, height=300, bg='white')
    auth_canvas.place(x='375', y='225')
    auth_canvas.pack_propagate(False)

    username_text = auth_canvas.create_text(125, 20, text="Имя пользователя", fill="Black", font=('Perpetua', 14))
    username_entry = tk.Entry(auth_canvas, width=20, font=('Segoe UI', 14))
    username_entry.config(highlightbackground="black")

    password_text = auth_canvas.create_text(125, 95, text="Пароль", fill="Black", font=('Perpetua', 14))
    password_entry = tk.Entry(auth_canvas, width=20, show="*", font=('Segoe UI', 14))

    login_button = tk.Button(auth_canvas, text="Вход в аккаунт",
                             command=lambda: login(username_entry.get(), password_entry.get()), pady='5',
                             cursor='hand2', fg='#fff', bg='#3300cc',
                             font=('Perpetua', 14))
    login_button.bind('<Enter>', focus_in)  # При входе курсора в область кнопки выполняем focus_in
    login_button.bind('<Leave>', focus_out)  # При выходе курсора из области кнопки выполняем focus_out_out
    register_button = tk.Label(auth_canvas, text="Регистрация", fg='blue', bg='white', cursor='hand2',
                               font=('Perpetua', 14, 'underline'))

    username_entry.pack_propagate(False)
    username_entry.place(x='35', y='40')

    password_entry.place(x='35', y='120')

    login_button.place(x='50', y='160')
    register_button.place(x='65', y='220')

    login_window.mainloop()


log_window()
