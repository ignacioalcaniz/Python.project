from tkinter import *
from tkinter import ttk

# Crear ventana principal
vivero_stock = Tk()
vivero_stock.title("Vivero LaPlace Stock")
vivero_stock.geometry("500x400")
vivero_stock.configure(bg="#f0f8f5")  # Fondo suave verde-agua

# Estilos globales
style = ttk.Style()
style.configure("Treeview",
                background="white",
                foreground="black",
                rowheight=25,
                fieldbackground="white",
                font=("Arial", 10))
style.map("Treeview",
          background=[("selected", "#90EE90")])  # Verde claro selección

style.configure("TButton",
                font=("Arial", 10, "bold"),
                padding=5)

# Variables de entrada
var_nombre = StringVar()
var_cantidad = IntVar()
var_precio = StringVar()

# Labels y campos de entrada
Label(vivero_stock, text="Nombre", font=("Arial", 11, "bold"), bg="#f0f8f5").grid(row=0, column=1, sticky=W)
Label(vivero_stock, text="Cantidad", font=("Arial", 11, "bold"), bg="#f0f8f5").grid(row=1, column=1, sticky=W)
Label(vivero_stock, text="Precio $", font=("Arial", 11, "bold"), bg="#f0f8f5").grid(row=2, column=1, sticky=W)

Entry(vivero_stock, textvariable=var_nombre).grid(row=0, column=2, padx=5, pady=3)
Entry(vivero_stock, textvariable=var_cantidad).grid(row=1, column=2, padx=5, pady=3)
Entry(vivero_stock, textvariable=var_precio).grid(row=2, column=2, padx=5, pady=3)

# Tabla (Treeview) para mostrar los productos
tree_vivero = ttk.Treeview(vivero_stock, columns=("col1", "col2", "col3"), show="headings")
tree_vivero.column("col1", width=150, anchor=W)
tree_vivero.column("col2", width=100, anchor=CENTER)
tree_vivero.column("col3", width=100, anchor=E)

tree_vivero.heading("col1", text="Nombre")
tree_vivero.heading("col2", text="Cantidad")
tree_vivero.heading("col3", text="Precio")

tree_vivero.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

# Exportar elementos clave para ser usados por el controlador
__all__ = [
    "vivero_stock", "var_nombre", "var_cantidad", "var_precio", "tree_vivero"
]





