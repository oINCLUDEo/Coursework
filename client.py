import json
import tkinter as tk
from tkinter import messagebox
from notifypy import Notify
import socket
import threading


def handle_messages():
    b = True
    while True:
        try:
            if b:
                received_data = client_socket.recv(4096).decode('utf-8')
                messages = json.loads(received_data)
                for message in messages:
                    if message[1] != name:
                        chat_text.config(state='normal')
                        chat_text.insert(tk.END, f'{message[1]}: {message[2]}' + '\n')
                        chat_text.config(state='disabled')
                    else:
                        chat_text.config(state='normal')
                        chat_text.insert(tk.END, f'Вы: {message[2]}' + '\n', 'right')
                        chat_text.config(state='disabled')
                chat_text.see(tk.END)
                b = False
            else:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    if message.split(':')[0] != name:
                        chat_text.config(state='normal')
                        chat_text.insert(tk.END, message + '\n')
                        chat_text.config(state='disabled')
                        if chat_window.wm_state() == 'iconic':
                            notification.message = f"У вас новое сообщение от пользователя: {message[1]}!"
                            notification.audio = 'notification.wav'
                            notification.icon = "notif1.jpg"
                            notification.send()
                chat_text.see(tk.END)
        except:
            break


def login(username, password):
    option = "login"
    client_socket.send(option.encode('utf-8'))
    data = [username, password]
    json_data = json.dumps(data)
    client_socket.sendall(json_data.encode())

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
    data = [username, password]
    json_data = json.dumps(data)
    client_socket.sendall(json_data.encode())
    print('пытаюсь')
    response = client_socket.recv(1024).decode('utf-8')
    if response == "Регистрация выполнена успешно":
        messagebox.showinfo("Успешно!", "Регистрация выполнена успешно. Теперь вы можете войти в аккаунт.")
        reg_canvas.destroy()
        canvas.delete(register_text)
        login_window.destroy()
        client_socket.close()
        log_window()
    else:
        messagebox.showerror("Ошибка!", 'Имя пользователя занято :(')
        reg_canvas.destroy()
        canvas.delete(register_text)
        login_window.destroy()
        client_socket.close()
        log_window()


def display_message(message, align):
    if message.split('Вы:')[1] != ' ':
        chat_text.config(state=tk.NORMAL)  # Enable editing the text widget
        chat_text.insert(tk.END, message + '\n', align)  # Use the tag to align the message
        chat_text.config(state=tk.DISABLED)  # Disable editing the text widget
        chat_text.see(tk.END)


def send_message(event=None):
    message = message_entry.get(1.0, tk.END).strip()
    if message:
        client_socket.send(message.encode('utf-8'))
        display_message(f"Вы: {message}", 'right')  # Display the user's message on the right
        message_entry.delete(1.0, tk.END)


def open_chat(username):
    global message_entry, chat_window, notification, chat_window
    notification = Notify()
    notification.title = 'Мессенджер'

    def on_closing():
        client_socket.close()
        chat_window.destroy()

    chat_window = tk.Tk()
    chat_window.title(f"Открыт чат для пользователя - {username}")
    chat_window.protocol("WM_DELETE_WINDOW", on_closing)  # Handle window closing event
    chat_window.iconbitmap(r'icon.ico')
    global name
    name = username
    chat_canvas = tk.Canvas(chat_window, width=460, height=50, bg='#3300cc')
    chat_canvas.grid(row=0, column=0, columnspan=2)
    welcome_text = chat_canvas.create_text(232.5, 30, anchor='center', text=f'Добро пожаловать, {name.upper()}',
                                      fill="#fff",
                                      font=('Segoe UI', 14, 'bold'))
    # chat_label = tk.Label(chat_window, text=f"Добро пожаловать, {username}!", font=("Segoe UI", 14), bg='#3300cc')
    # chat_label.grid(row=0, column=0, columnspan=2)

    global chat_text
    scrollbar = tk.Scrollbar(chat_window)
    scrollbar.grid(row=1, column=1, sticky=tk.NS)

    chat_text = tk.Text(chat_window, height=20, width=50, wrap="word", yscrollcommand=scrollbar.set)
    chat_text.grid(row=1, column=0)

    scrollbar.config(command=chat_text.yview)
    chat_text.config(state='disabled')
    chat_text.tag_configure('left', justify='left')
    chat_text.tag_configure('right', justify='right')

    message_entry = tk.Text(chat_window, width=40, height=4)
    message_entry.grid(row=2, column=0)
    message_entry.see(1.0)
    message_entry.mark_set('insert', '1.0')

    message_entry.bind('<Return>', send_message)
    but_photo = tk.PhotoImage(file='next button.gif')
    send_button = tk.Button(chat_window, image=but_photo, command=send_message)
    send_button.grid(row=2, column=1)

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
    def focus_in(e=None):
        next_button2.configure(fg='#3300cc')  # Задаём кнопке нужные цвета
        next_button2.configure(bg='#fff')

    def focus_out(e=None):
        next_button2.configure(bg='#3300cc')
        next_button2.configure(fg='#fff')

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
    next_button2.bind('<Enter>', focus_in)  # При входе курсора в область кнопки выполняем focus_in
    next_button2.bind('<Leave>', focus_out)  # При выходе курсора из области кнопки выполняем focus_out_out
    password_entry.place(x='25', y='100')


def log_window():
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
    login_window.iconbitmap(r'icon.ico')
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
    login_window.mainloop()


log_window()
