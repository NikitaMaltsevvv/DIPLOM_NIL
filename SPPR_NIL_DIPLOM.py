# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pyodbc
import subprocess
import re
from datetime import datetime

# Настройки для подключения к MS SQL Server
DATABASE_CONFIG = {
    "server": "NIKITA\\SQLEXPRESS",
    "database": "IMMOD_DIPLOM_NIL",
    "username": "SPPR",
    "password": "123",
}

def authenticate_user(username, password):
    try:
        connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DATABASE_CONFIG['server']};"
            f"DATABASE={DATABASE_CONFIG['database']};"
            f"UID={DATABASE_CONFIG['username']};"
            f"PWD={DATABASE_CONFIG['password']}"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM User WHERE Email = ? AND PasswordHash = ?", (username, password))
        result = cursor.fetchone()
        connection.close()
        return result[0] > 0
    except Exception as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return False

def launch_anylogic():
    """Запускает AnyLogic через системный вызов."""
    try:
        anylogic_path = ".\\model_nil\\model_nil.alp"  # Укажите путь к исполняемому файлу AnyLogic
        subprocess.Popen(anylogic_path, shell=True)
        messagebox.showinfo("Успех", "AnyLogic запущен успешно.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить AnyLogic: {e}")

def validate_name(name):
    return re.match(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$", name)

def validate_date(date):
    try:
        input_date = datetime.strptime(date, "%d.%m.%Y")
        return input_date >= datetime.now()
    except ValueError:
        return False

def validate_text(text):
    return len(text.strip()) > 0

def create_interface():
    def login():
        username = username_entry.get()
        password = password_entry.get()
        # if authenticate_user(username, password):
        #     messagebox.showinfo("Успех", "Вход выполнен успешно!")
        show_main_interface()
        # else:
        #     messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

    def show_main_interface():
        for widget in root.winfo_children():
            widget.destroy()
        try:
            background_image_path = ".\\img\\sibsutis.jpg"
            background_image = Image.open(background_image_path)
            background_image = background_image.resize((800, 600), Image.Resampling.LANCZOS)
            bg_image = ImageTk.PhotoImage(background_image)
            background_label = tk.Label(root, image=bg_image)
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            root.background_image_ref = bg_image
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")

        tab_control = ttk.Notebook(root)

        # Вкладка 1: Составить отчет
        def submit_report():
            dob = dob_entry.get()
            selected_parts = []
            if checkbox_failures_var.get():
                selected_parts.append("Прогноз отказов")
            if checkbox_state_var.get():
                selected_parts.append("Состояние КТС")
            if checkbox_prevention_var.get():
                selected_parts.append("Генерация профилактических мероприятий")
    
            if not validate_date(dob):
                messagebox.showerror("Ошибка", "Введите корректную дату (ДД.ММ.ГГГГ) не ранее текущей.")
                return
    
            if not selected_parts:
                messagebox.showerror("Ошибка", "Выберите хотя бы одну часть отчета.")
                return
    
            selected_parts_str = ", ".join(selected_parts)
            messagebox.showinfo("Успех", f"Отчет успешно сформирован для следующих частей: {selected_parts_str}!")

        tab_report = ttk.Frame(tab_control)
        tab_control.add(tab_report, text="Составить отчет")

        ttk.Label(tab_report, text="Введите данные для отчета:", font=("Arial", 12)).pack(pady=10)

        ttk.Label(tab_report, text="Дата планирования (ДД.ММ.ГГГГ):", font=("Arial", 10)).pack(anchor="w", padx=20, pady=5)
        dob_entry = ttk.Entry(tab_report, width=40)
        dob_entry.pack(padx=20, pady=5)

        ttk.Label(tab_report, text="Выберите части отчета:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=5)

        checkbox_failures_var = tk.BooleanVar()
        checkbox_state_var = tk.BooleanVar()
        checkbox_prevention_var = tk.BooleanVar()

        ttk.Checkbutton(tab_report, text="Прогноз отказов", variable=checkbox_failures_var).pack(anchor="w", padx=40)
        ttk.Checkbutton(tab_report, text="Состояние КТС", variable=checkbox_state_var).pack(anchor="w", padx=40)
        ttk.Checkbutton(tab_report, text="Генерация профилактических мероприятий", variable=checkbox_prevention_var).pack(anchor="w", padx=40)

        ttk.Button(tab_report, text="Составить отчет", command=submit_report).pack(pady=20)


        # Вкладка 2: Имитационный эксперимент
        tab_experiment = ttk.Frame(tab_control)
        tab_control.add(tab_experiment, text="Имитационный эксперимент")

        ttk.Label(tab_experiment, text="Имитационный эксперимент:", font=("Arial", 12)).pack(pady=10)
        ttk.Button(tab_experiment, text="Запустить эксперимент", command=launch_anylogic).pack(pady=20)

        # Вкладка 3: Создать профилактическое мероприятие
        def create_event():
            event_name = event_name_entry.get()
            event_description = event_description_entry.get("1.0", "end").strip()
            event_date = event_date_entry.get()
            if not validate_text(event_name):
                messagebox.showerror("Ошибка", "Название мероприятия не может быть пустым.")
                return
            if not validate_text(event_description):
                messagebox.showerror("Ошибка", "Описание мероприятия не может быть пустым.")
                return
            if not validate_date(event_date):
                messagebox.showerror("Ошибка", "Введите корректную дату (ДД.ММ.ГГГГ) не ранее текущей.")
                return
            messagebox.showinfo("Успех", "Мероприятие успешно создано!")

        tab_prevention = ttk.Frame(tab_control)
        tab_control.add(tab_prevention, text="Создать профилактическое мероприятие")

        ttk.Label(tab_prevention, text="Введите данные для создания мероприятия:", font=("Arial", 12)).pack(pady=10)

        ttk.Label(tab_prevention, text="Название мероприятия:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=5)
        event_name_entry = ttk.Entry(tab_prevention, width=40)
        event_name_entry.pack(padx=20, pady=5)

        ttk.Label(tab_prevention, text="Описание мероприятия:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=5)
        event_description_entry = tk.Text(tab_prevention, height=5, width=40)
        event_description_entry.pack(padx=20, pady=5)

        ttk.Label(tab_prevention, text="Дата проведения (ДД.ММ.ГГГГ):", font=("Arial", 10)).pack(anchor="w", padx=20, pady=5)
        event_date_entry = ttk.Entry(tab_prevention, width=40)
        event_date_entry.pack(padx=20, pady=5)

        ttk.Button(tab_prevention, text="Создать мероприятие", command=create_event).pack(pady=20)

        tab_control.pack(expand=1, fill="both")

    root = tk.Tk()
    root.title("СППР по выработке профилактических мероприятий")
    root.geometry("800x400")

    ttk.Label(root, text="Вход в систему", font=("Arial", 16)).pack(pady=20)

    ttk.Label(root, text="Email:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)
    username_entry = ttk.Entry(root, width=30)
    username_entry.pack(padx=20, pady=5)

    ttk.Label(root, text="Пароль:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)
    password_entry = ttk.Entry(root, width=30, show="*")
    password_entry.pack(padx=20, pady=5)

    ttk.Button(root, text="Войти", command=login).pack(pady=20)

    root.mainloop()

create_interface()
