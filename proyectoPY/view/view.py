from tkinter import *
from tkinter import ttk

# ---------- VENTANA PRINCIPAL ----------
ventana_principal = Tk()
ventana_principal.title("Biblioteca Popular Nelly Llorens - Gestión")
ventana_principal.geometry("1020x660")
ventana_principal.configure(bg="#f0f8f5")

# ---------- NOTEBOOK (Pestañas) ----------
notebook = ttk.Notebook(ventana_principal)
notebook.pack(fill="both", expand=True)

# =========================================================
#  PESTAÑA: LIBROS
# =========================================================
tab_libros = Frame(notebook, bg="#f0f8f5")
notebook.add(tab_libros, text="Libros")

# Vars Libros
var_titulo = StringVar()
var_autor = StringVar()
var_categoria = StringVar()
var_editorial = StringVar()
var_anio = StringVar()
var_pais = StringVar()
var_ubicacion = StringVar()
var_cantidad = IntVar()
var_precio = StringVar()
var_buscar_libro = StringVar()

# Formulario de Libros
r = 0
Label(tab_libros, text="Título *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_titulo, width=48).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="Autor *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_autor, width=48).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="Categoría *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_categoria, width=30).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="Editorial *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_editorial, width=30).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="Año *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_anio, width=12).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="País *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_pais, width=20).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="Ubicación (opcional)", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_ubicacion, width=30).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="Cantidad *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_cantidad, width=12).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

Label(tab_libros, text="Precio *", font=("Arial", 10, "bold"), bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8, pady=4)
Entry(tab_libros, textvariable=var_precio, width=15).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

# Buscador de libros
Label(tab_libros, text="Buscar (título/autor):", bg="#f0f8f5").grid(row=r, column=0, sticky=W, padx=8)
Entry(tab_libros, textvariable=var_buscar_libro, width=48).grid(row=r, column=1, padx=6, pady=4, sticky=W); r += 1

# Tabla Libros
tree_libros = ttk.Treeview(
    tab_libros, columns=("titulo","autor","categoria","cant","precio"),
    show="headings", height=12
)
for col, txt, w in [
    ("titulo","Título",300),
    ("autor","Autor",220),
    ("categoria","Categoría",160),
    ("cant","Cant.",70),
    ("precio","Precio",90),
]:
    tree_libros.heading(col, text=txt)
    tree_libros.column(col, width=w, anchor=W)
tree_libros.grid(row=r, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

# Contenedor de botones Libros (lo usa el Controller)
frame_libros_buttons = Frame(tab_libros, bg="#f0f8f5")
frame_libros_buttons.grid(row=r+1, column=0, columnspan=5, pady=8)

# =========================================================
#  PESTAÑA: SOCIOS
# =========================================================
tab_socios = Frame(notebook, bg="#eef6ff")
notebook.add(tab_socios, text="Socios")

var_socio_nombre = StringVar()
var_socio_dni = StringVar()
var_socio_tel = StringVar()
var_socio_email = StringVar()

Label(tab_socios, text="Nombre *", bg="#eef6ff", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=W, padx=8, pady=4)
Entry(tab_socios, textvariable=var_socio_nombre, width=40).grid(row=0, column=1, padx=6, pady=4, sticky=W)

Label(tab_socios, text="DNI *", bg="#eef6ff", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=W, padx=8, pady=4)
Entry(tab_socios, textvariable=var_socio_dni, width=20).grid(row=1, column=1, padx=6, pady=4, sticky=W)

Label(tab_socios, text="Teléfono *", bg="#eef6ff", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=W, padx=8, pady=4)
Entry(tab_socios, textvariable=var_socio_tel, width=20).grid(row=2, column=1, padx=6, pady=4, sticky=W)

Label(tab_socios, text="Email *", bg="#eef6ff", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=W, padx=8, pady=4)
Entry(tab_socios, textvariable=var_socio_email, width=30).grid(row=3, column=1, padx=6, pady=4, sticky=W)

tree_socios = ttk.Treeview(
    tab_socios, columns=("nombre","dni","telefono","email"),
    show="headings", height=14
)
for col, txt, w in [
    ("nombre","Nombre",280),
    ("dni","DNI",120),
    ("telefono","Teléfono",160),
    ("email","Email",240),
]:
    tree_socios.heading(col, text=txt)
    tree_socios.column(col, width=w, anchor=W)
tree_socios.grid(row=6, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

# Contenedor de botones Socios (lo usa el Controller)
frame_socios_buttons = Frame(tab_socios, bg="#eef6ff")
frame_socios_buttons.grid(row=7, column=0, columnspan=5, pady=8)

# ---------- EXPORT ----------
__all__ = [
    "ventana_principal", "notebook",
    # Libros
    "tab_libros", "var_titulo", "var_autor", "var_categoria", "var_editorial",
    "var_anio", "var_pais", "var_ubicacion", "var_cantidad", "var_precio",
    "tree_libros", "var_buscar_libro", "frame_libros_buttons",
    # Socios
    "tab_socios", "var_socio_nombre", "var_socio_dni", "var_socio_tel", "var_socio_email",
    "tree_socios", "frame_socios_buttons",
]











