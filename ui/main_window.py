import tkinter as tk
from tkinter import ttk, messagebox
from services.firebase_service import FirebaseService
from models.ejercicio import Ejercicio


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Pesos Picados")
        self.firebase_service = FirebaseService()
        self.ejercicios = []
        self._create_widgets()
        self._load_ejercicios()

    def _create_widgets(self):
        header_frame = tk.Frame(self.root, bg="lightgray", bd=2, relief=tk.SOLID)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            header_frame,
            text="Pesos Picados",
            font=("Arial", 20, "bold"),
            bg="lightgray"
        ).pack(side=tk.LEFT, padx=15, pady=10)

        ttk.Button(header_frame, text="Salir", command=self._handle_logout).pack(side=tk.RIGHT, padx=15, pady=10)

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Agregar Ejercicio", width=20, command=self._show_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", width=12, command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", width=12, command=self._load_ejercicios).pack(side=tk.LEFT, padx=5)

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("Ejercicio", "Peso", "Reps", "Series", "Fecha", "Notas")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("Ejercicio", width=200)
        self.tree.column("Peso", width=80)
        self.tree.column("Reps", width=80)
        self.tree.column("Series", width=80)
        self.tree.column("Fecha", width=100)
        self.tree.column("Notas", width=250)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def _load_ejercicios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.ejercicios = self.firebase_service.obtener_ejercicios()

        for ejercicio in self.ejercicios:
            self.tree.insert("", tk.END, values=(
                ejercicio.nombre,
                f"{ejercicio.peso} kg",
                ejercicio.repeticiones,
                ejercicio.series,
                ejercicio.fecha,
                ejercicio.notas
            ), tags=(ejercicio.id,))

    def _show_add_dialog(self):
        AddEjercicioDialog(self.root, self)

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Selecciona un ejercicio primero")
            return

        item = selected[0]
        ejercicio_id = self.tree.item(item)['tags'][0]

        ejercicio = next((e for e in self.ejercicios if e.id == ejercicio_id), None)
        if not ejercicio:
            return

        if messagebox.askyesno("Eliminar", f"¿Eliminar: {ejercicio.nombre}?"):
            if self.firebase_service.eliminar_ejercicio(ejercicio_id):
                messagebox.showinfo("OK", "Eliminado")
                self._load_ejercicios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar")

    def _handle_logout(self):
        if messagebox.askyesno("Salir", "¿Seguro que quieres salir?"):
            self.firebase_service.logout()
            for widget in self.root.winfo_children():
                widget.destroy()
            from ui.login_window import LoginWindow
            self.root.geometry("450x350")
            LoginWindow(self.root)


class AddEjercicioDialog:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.firebase_service = FirebaseService()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Agregar Ejercicio")
        self.dialog.geometry("400x380")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._center_window()

    def _center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Ingresar datos del ejercicio", font=("Arial", 12, "bold")).pack(pady=(0, 15))

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)

        fields = [("Ejercicio:", "nombre"), ("Peso (kg):", "peso"), ("Repeticiones:", "reps"), ("Series:", "series")]
        self.entries = {}

        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=8)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, pady=8, padx=5)
            self.entries[key] = entry

        ttk.Label(form_frame, text="Notas:").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.notas_text = tk.Text(form_frame, width=30, height=3)
        self.notas_text.grid(row=4, column=1, pady=8, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)

        ttk.Button(button_frame, text="Guardar", width=12, command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", width=12, command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        self.entries["nombre"].focus()

    def _save(self):
        try:
            nombre = self.entries["nombre"].get().strip()
            peso   = float(self.entries["peso"].get().strip())
            reps   = int(self.entries["reps"].get().strip())
            series = int(self.entries["series"].get().strip())
            notas  = self.notas_text.get("1.0", tk.END).strip()

            if not nombre:
                messagebox.showerror("Error", "Falta el nombre del ejercicio")
                return

            ejercicio = Ejercicio(nombre, peso, reps, series, notas)

            if self.firebase_service.guardar_ejercicio(ejercicio):
                messagebox.showinfo("OK", "Guardado OK")
                self.dialog.destroy()
                self.main_window._load_ejercicios()
            else:
                messagebox.showerror("Error", "Error al guardar")

        except ValueError:
            messagebox.showerror("Error", "Los números están mal")
