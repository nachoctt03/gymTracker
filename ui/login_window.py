import tkinter as tk
from tkinter import ttk, messagebox
from services.firebase_service import FirebaseService
from updater import APP_VERSION


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Pesos Picados - Login | {APP_VERSION}")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        self.firebase_service = FirebaseService()
        self._create_widgets()
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Pesos Picados", font=("Arial", 24, "bold")).pack(pady=(0, 5))
        ttk.Label(main_frame, text="Inicio sesión", font=("Arial", 12)).pack(pady=(0, 20))

        form_frame = ttk.LabelFrame(main_frame, text="", padding="15")
        form_frame.pack(pady=10, padx=20, fill=tk.BOTH)

        ttk.Label(form_frame, text="Correo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)

        self.login_button = ttk.Button(button_frame, text="Login", width=15, command=self._handle_login)
        self.login_button.pack(side=tk.LEFT, padx=5)

        self.register_button = ttk.Button(button_frame, text="Registrar", width=15, command=self._show_register_window)
        self.register_button.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=5)

        self.password_entry.bind('<Return>', lambda e: self._handle_login())
        self.email_entry.focus()

    def _handle_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            self.status_label.config(text="Llena todos los campos", foreground="red")
            return

        self.status_label.config(text="Cargando...", foreground="blue")
        self.login_button.config(state=tk.DISABLED)
        self.root.update()

        success = self.firebase_service.login(email, password)
        self.login_button.config(state=tk.NORMAL)

        if success:
            self._open_main_window()
        else:
            self.status_label.config(text="Correo o contraseña incorrectos", foreground="red")

    def _show_register_window(self):
        RegisterWindow(self.root, self)

    def _open_main_window(self):
        from ui.main_window import MainWindow
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("900x600")
        MainWindow(self.root)


class RegisterWindow:
    def __init__(self, parent, login_window):
        self.parent = parent
        self.login_window = login_window
        self.firebase_service = FirebaseService()

        self.window = tk.Toplevel(parent)
        self.window.title("Registro de Usuario")
        self.window.geometry("400x380")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()
        self._center_window()

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Crear Nueva Cuenta", font=("Arial", 18, "bold")).pack(pady=(0, 15))

        form_frame = ttk.LabelFrame(main_frame, text="", padding="15")
        form_frame.pack(pady=10, padx=10, fill=tk.BOTH)

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nombre_entry = ttk.Entry(form_frame, width=25)
        self.nombre_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Correo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=25)
        self.email_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=25, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Confirmar:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = ttk.Entry(form_frame, width=25, show="*")
        self.confirm_entry.grid(row=3, column=1, pady=5, padx=5)

        self.register_button = ttk.Button(main_frame, text="Crear Cuenta", width=20, command=self._handle_register)
        self.register_button.pack(pady=15)

        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=5)

        self.nombre_entry.focus()

    def _handle_register(self):
        nombre = self.nombre_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not nombre or not email or not password:
            self.status_label.config(text="Completa todos los campos", foreground="red")
            return

        if password != confirm:
            self.status_label.config(text="Las contraseñas no coinciden", foreground="red")
            return

        if len(password) < 6:
            self.status_label.config(text="Contraseña muy corta (mín 6)", foreground="red")
            return

        self.status_label.config(text="Creando cuenta...", foreground="blue")
        self.register_button.config(state=tk.DISABLED)
        self.window.update()

        success = self.firebase_service.registro(email, password, nombre)
        self.register_button.config(state=tk.NORMAL)

        if success:
            messagebox.showinfo("OK", "Cuenta creada correctamente")
            self.window.destroy()
            self.login_window._open_main_window()
        else:
            self.status_label.config(text="Correo ya existe", foreground="red")
