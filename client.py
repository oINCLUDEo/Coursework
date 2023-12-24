import json
import tkinter as tk
from tkinter import messagebox
import socket
import threading


def handle_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                chat_text.config(state='normal')
                chat_text.insert(tk.END, message + '\n')
                chat_text.config(state='disabled')
                chat_text.see(tk.END)
        except:
            break


def login(username, password):
    option = "login"
    client_socket.send(option.encode('utf-8'))

    client_socket.send(username.encode('utf-8'))
    client_socket.send(password.encode('utf-8'))

    print('работаем')
    response = client_socket.recv(1024).decode('utf-8')
    print('не работаем')
    if response == "Login successful":
        login_window.destroy()
        open_chat(username)
    else:
        messagebox.showerror("Error", response)


def register(username, password):
    option = "register"
    client_socket.send(option.encode('utf-8'))

    client_socket.send(username.encode('utf-8'))
    client_socket.send(password.encode('utf-8'))
    print('пытаюсь')
    response = client_socket.recv(1024).decode('utf-8')
    if response == "Registration successful":
        messagebox.showinfo("Success", "Registration successful. You can now log in.")
        reg_canvas.destroy()
        # canvas.delete(register_text)
        # log_window(False)
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

    def send_message():
        message = message_entry.get()
        client_socket.send(message.encode('utf-8'))
        message_entry.delete(0, tk.END)

    send_button = tk.Button(chat_window, text="Send", command=send_message)
    send_button.pack()

    threading.Thread(target=handle_messages).start()

    chat_window.mainloop()


def reg_window_username(event):
    auth_canvas.destroy()
    global register_text
    register_text = canvas.create_text(500, 100, anchor='center', text='        СОЗДАНИЕ\n УЧЕТНОЙ ЗАПИСИ',
                                       fill="White",
                                       font=('Perpetua', 32, 'bold'))

    def focus_in(e=None):
        next_button.configure(fg='#3300cc')  # Задаём кнопке нужные цвета
        next_button.configure(bg='#fff')

    def focus_out(e=None):
        next_button.configure(bg='#3300cc')
        next_button.configure(fg='#fff')

    def check_data():
        print('ку')
        if len(username_entry.get().rstrip(' ')) >= 1:
            username = username_entry.get()
            reg_window_password(username)

    global reg_canvas
    reg_canvas = tk.Canvas(canvas, width=250, height=300, bg='white')
    reg_canvas.place(x='375', y='225')
    reg_canvas.pack_propagate(False)

    global username_text, username_entry, next_button
    username_text = reg_canvas.create_text(125, 70, text="Имя пользователя", fill="Black", font=('Perpetua', 14))
    username_entry = tk.Entry(reg_canvas, width=20, font=('Segoe UI', 14))
    username_entry.config(highlightbackground="black")

    next_button = tk.Button(reg_canvas, text="Далее", pady='5',
                            cursor='hand2', command=check_data, fg='#fff', bg='#3300cc',
                            font=('Perpetua', 14))
    next_button.bind('<Enter>', focus_in)  # При входе курсора в область кнопки выполняем focus_in
    next_button.bind('<Leave>', focus_out)  # При выходе курсора из области кнопки выполняем focus_out_out
    # register_button = tk.Label(auth_canvas, text="Регистрация", fg='blue', bg='white', cursor='hand2',
    #                           font=('Perpetua', 14, 'underline'))
    # register_button.bind("<Button-1>", reg_window)

    username_entry.pack_propagate(False)
    username_entry.place(x='25', y='100')

    next_button.place(x='95', y='160')
    # register_button.place(x='65', y='220')


def reg_window_password(username):
    def check_data():
        if len(password_entry.get().rstrip(' ')) >= 1:
            print('Проверил данные')
            register(username, password_entry.get())

    reg_canvas.delete(username_text)
    username_entry.destroy()
    next_button.destroy()
    password_text = reg_canvas.create_text(125, 70, text="Пароль", fill="Black", font=('Perpetua', 14))
    password_entry = tk.Entry(reg_canvas, width=20, show="*", font=('Segoe UI', 14))

    next_button2 = tk.Button(reg_canvas, text="Далее", pady='5',
                             cursor='hand2', command=check_data, fg='#fff', bg='#3300cc',
                             font=('Perpetua', 14))

    next_button2.place(x='95', y='160')
    password_entry.place(x='25', y='100')


def log_window(k):
    def focus_in(e=None):
        login_button.configure(fg='#3300cc')  # Задаём кнопке нужные цвета
        login_button.configure(bg='#fff')

    def focus_out(e=None):
        login_button.configure(bg='#3300cc')
        login_button.configure(fg='#fff')

    global client_socket, login_window
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9090))
    login_window = tk.Tk()
    login_window.geometry('1000x750')  # Задаём размер
    login_window.title("Messenger")
    login_window.resizable(width=False, height=False)
    global canvas
    canvas = tk.Canvas(login_window, width=1000, height=750)
    canvas.pack()
    canvas.pack_propagate(False)
    img = tk.PhotoImage(file='back.gif')
    canvas.create_image(0, 0, anchor=tk.NW, image=img)
    global auth_canvas
    auth_canvas = tk.Canvas(canvas, width=250, height=300, bg='white')
    auth_canvas.place(x='375', y='225')
    auth_canvas.pack_propagate(False)
    print('норм')
    username_text = auth_canvas.create_text(125, 20, text="Имя пользователя", fill="Black", font=('Perpetua', 14))
    username_entry = tk.Entry(auth_canvas, width=20, font=('Segoe UI', 14))
    username_entry.config(highlightbackground="black")

    password_text = auth_canvas.create_text(125, 95, text="Пароль", fill="Black", font=('Perpetua', 14))
    password_entry = tk.Entry(auth_canvas, width=20, show="*", font=('Segoe UI', 14))

    login_button = tk.Button(auth_canvas, text="Вход в аккаунт", pady='5',
                             command=lambda: login(username_entry.get(), password_entry.get()),
                             cursor='hand2', fg='#fff', bg='#3300cc',
                             font=('Perpetua', 14))
    login_button.bind('<Enter>', focus_in)  # При входе курсора в область кнопки выполняем focus_in
    login_button.bind('<Leave>', focus_out)  # При выходе курсора из области кнопки выполняем focus_out_out
    register_button = tk.Label(auth_canvas, text="Регистрация", fg='blue', bg='white', cursor='hand2',
                               font=('Perpetua', 14, 'underline'))
    register_button.bind("<Button-1>", reg_window_username)

    username_entry.pack_propagate(False)
    username_entry.place(x='35', y='40')

    password_entry.place(x='35', y='120')

    login_button.place(x='50', y='160')
    register_button.place(x='65', y='220')
    if k:
        login_window.mainloop()


log_window(True)
