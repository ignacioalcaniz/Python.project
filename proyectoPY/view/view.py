from tkinter import *
from tkinter import ttk
import os
from PIL import Image, ImageTk

# =========================================================
# VENTANA PRINCIPAL
# =========================================================
ventana_principal = Tk()
ventana_principal.title("Biblioteca Popular Nelly Llorens - Gestión")
ventana_principal.geometry("1540x920")
ventana_principal.minsize(1420, 840)
ventana_principal.configure(bg="#eef4f8")

# =========================================================
# PALETA
# =========================================================
COLOR_BG = "#eef4f8"
COLOR_HEADER = "#17324d"
COLOR_HEADER_2 = "#224d77"
COLOR_CARD = "#ffffff"
COLOR_ACCENT = "#3aa6b9"
COLOR_TEXT = "#183247"
COLOR_TAB = "#d7e9f7"

COLOR_STAT_1 = "#dff6ff"
COLOR_STAT_2 = "#e8f8e1"
COLOR_STAT_3 = "#fff5d6"
COLOR_STAT_4 = "#f3e8ff"
COLOR_STAT_5 = "#ffe4e1"

# =========================================================
# LISTAS DESPLEGABLES
# =========================================================
Paises = [
    "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Costa Rica", "Cuba",
    "Ecuador", "El Salvador", "España", "Estados Unidos", "Francia", "Italia",
    "México", "Paraguay", "Perú", "Uruguay", "Venezuela", "Alemania", "Portugal",
    "Reino Unido", "Canadá", "Australia", "Japón", "China", "India", "Rusia",
    "Corea del Sur", "Sudáfrica", "Egipto", "Marruecos", "Israel", "Turquía",
    "Grecia", "Suiza", "Bélgica", "Países Bajos", "Suecia", "Noruega", "Dinamarca",
    "Finlandia", "Irlanda", "Austria", "Polonia", "Hungría", "Rumania", "Ucrania",
    "Croacia", "Serbia", "República Checa", "Eslovaquia", "Eslovenia", "Bulgaria",
    "Arabia Saudita", "Emiratos Árabes Unidos", "Qatar", "Irán", "Irak", "Pakistán",
    "Bangladés", "Nepal", "Tailandia", "Vietnam", "Indonesia", "Malasia", "Filipinas",
    "Singapur", "Nueva Zelanda", "Nigeria", "Kenia", "Etiopía", "Angola", "Argelia",
    "Túnez", "Libia", "Senegal", "Ghana", "Camerún", "Panamá", "Guatemala",
    "Honduras", "Nicaragua", "República Dominicana", "Puerto Rico", "Jamaica",
    "Islandia", "Luxemburgo", "Estonia", "Letonia", "Lituania", "Mónaco",
    "Andorra", "San Marino", "Vaticano", "Malta", "Chipre", "Kazajistán",
    "Uzbekistán", "Afganistán", "Sri Lanka", "Mongolia"
]

Idiomas = [
    "Español", "Inglés", "Francés", "Italiano", "Portugués", "Alemán", "Ruso",
    "Chino mandarín", "Japonés", "Coreano", "Árabe", "Hebreo", "Hindi", "Urdu",
    "Bengalí", "Turco", "Griego", "Latín", "Catalán", "Gallego", "Euskera",
    "Quechua", "Guaraní", "Aymara", "Mapudungun", "Neerlandés", "Sueco", "Noruego",
    "Danés", "Finés", "Islandés", "Polaco", "Checo", "Eslovaco", "Húngaro",
    "Rumano", "Búlgaro", "Ucraniano", "Croata", "Serbio", "Esloveno", "Albanés",
    "Persa", "Tailandés", "Vietnamita", "Indonesio", "Malayo", "Tagalo", "Swahili",
    "Afrikáans", "Amhárico", "Zulu", "Xhosa", "Yoruba", "Igbo", "Hausa", "Somalí",
    "Tamil", "Telugu", "Kannada", "Malayalam", "Punjabi", "Marathi", "Gujarati",
    "Nepalí", "Sinhala", "Birmano", "Lao", "Camboyano", "Mongol", "Kazajo",
    "Uzbeko", "Georgiano", "Armenio", "Azerí", "Esperanto", "Irlandés", "Galés",
    "Escocés gaélico", "Bretón", "Luxemburgués", "Maltés", "Estonio", "Letón",
    "Lituano", "Bosnio", "Macedonio", "Bielorruso", "Tártaro", "Kurdo", "Pashto",
    "Dari", "Tibetano", "Maorí", "Samoano", "Hawaiano"
]

MODALIDADES_CUOTA = ["Mensual", "Anual"]
ESTADOS_CUOTA = ["Al día", "Pendiente"]

# =========================================================
# ESTILOS TTK
# =========================================================
style = ttk.Style()
style.theme_use("clam")

style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
style.configure(
    "TNotebook.Tab",
    padding=(18, 10),
    font=("Segoe UI", 10, "bold"),
    background=COLOR_TAB,
    foreground=COLOR_TEXT
)
style.map(
    "TNotebook.Tab",
    background=[("selected", COLOR_ACCENT), ("active", "#bfe7ee")],
    foreground=[("selected", "white"), ("active", COLOR_TEXT)]
)

style.configure(
    "Treeview",
    rowheight=28,
    font=("Segoe UI", 10),
    background="white",
    fieldbackground="white",
    foreground=COLOR_TEXT
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 10, "bold"),
    background=COLOR_HEADER_2,
    foreground="white",
    relief="flat"
)

style.map(
    "Treeview",
    background=[("selected", "#d7eef6")],
    foreground=[("selected", COLOR_TEXT)]
)

style.configure(
    "Custom.TCombobox",
    fieldbackground="#fbfdff",
    background="white",
    foreground=COLOR_TEXT
)

# =========================================================
# HEADER CON LOGOS REALES
# =========================================================
header = Frame(ventana_principal, bg=COLOR_HEADER, height=110)
header.pack(fill="x")
header.pack_propagate(False)


def cargar_logo(parent, ruta, ancho=96, alto=96):
    cont = Frame(parent, bg=COLOR_HEADER, width=ancho, height=alto)
    cont.pack_propagate(False)

    try:
        if os.path.exists(ruta):
            img = Image.open(ruta)
            img.thumbnail((ancho, alto))
            tk_img = ImageTk.PhotoImage(img)

            lbl = Label(cont, image=tk_img, bg=COLOR_HEADER)
            lbl.image = tk_img
            lbl.pack(expand=True)
        else:
            Label(
                cont,
                text="Logo",
                bg=COLOR_HEADER,
                fg="white",
                font=("Segoe UI", 10, "bold")
            ).pack(expand=True)
    except Exception:
        Label(
            cont,
            text="Logo",
            bg=COLOR_HEADER,
            fg="white",
            font=("Segoe UI", 10, "bold")
        ).pack(expand=True)

    return cont


assets_dir = os.path.join(os.getcwd(), "assets")
logo_1_path = os.path.join(assets_dir, "logo_biblioteca_1.jpeg")
logo_2_path = os.path.join(assets_dir, "logo_biblioteca_2.jpeg")

logo_izq = cargar_logo(header, logo_1_path, 96, 96)
logo_izq.pack(side=LEFT, padx=(18, 14), pady=7)

header_text = Frame(header, bg=COLOR_HEADER)
header_text.pack(side=LEFT, pady=14)

Label(
    header_text,
    text="Biblioteca Popular Nelly Llorens",
    bg=COLOR_HEADER,
    fg="white",
    font=("Segoe UI", 22, "bold")
).pack(anchor="w")

Label(
    header_text,
    text="Gestión de libros, socios, préstamos, estadísticas y logs",
    bg=COLOR_HEADER,
    fg="#cfe6f6",
    font=("Segoe UI", 11)
).pack(anchor="w")

logo_der = cargar_logo(header, logo_2_path, 96, 96)
logo_der.pack(side=RIGHT, padx=(14, 18), pady=7)

# =========================================================
# NOTEBOOK
# =========================================================
notebook = ttk.Notebook(ventana_principal)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# =========================================================
# HELPERS
# =========================================================
def mk_label(parent, text, row, col):
    Label(
        parent,
        text=text,
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=row, column=col, sticky="w", padx=6, pady=4)


def mk_entry(parent, textvar, row, col, width=24):
    Entry(
        parent,
        textvariable=textvar,
        width=width,
        font=("Segoe UI", 10),
        bg="#fbfdff",
        fg=COLOR_TEXT,
        relief="solid",
        bd=1
    ).grid(row=row, column=col, sticky="w", padx=6, pady=4)


def stat_card(parent, bg_color, title_text, var_text):
    card = Frame(parent, bg=bg_color, bd=1, relief="solid")
    Label(
        card,
        text=title_text,
        bg=bg_color,
        fg=COLOR_TEXT,
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=12, pady=(10, 2))
    Label(
        card,
        textvariable=var_text,
        bg=bg_color,
        fg=COLOR_TEXT,
        font=("Segoe UI", 10),
        justify=LEFT,
        wraplength=280
    ).pack(anchor="w", padx=12, pady=(0, 10))
    return card


# =========================================================
# TAB LIBROS
# =========================================================
tab_libros = Frame(notebook, bg=COLOR_BG)
notebook.add(tab_libros, text="Libros")

var_titulo = StringVar()
var_autor = StringVar()
var_categoria = StringVar()
var_subcategoria = StringVar()
var_es_infantil = BooleanVar(value=False)
var_editorial = StringVar()
var_anio = StringVar()
var_pais = StringVar()
var_idioma = StringVar(value="Español")
var_isbn = StringVar()
var_ubicacion = StringVar()
var_cantidad = StringVar()
var_cantidad_paginas = StringVar()
var_descripcion = StringVar()
var_imagen_path = StringVar()
var_buscar_libro = StringVar()

libros_main = Frame(tab_libros, bg=COLOR_BG)
libros_main.pack(fill="both", expand=True, padx=8, pady=8)

libros_form = LabelFrame(
    libros_main,
    text="Datos del libro",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=8,
    bd=2,
    relief="groove"
)
libros_form.pack(fill="x", pady=(0, 8))

mk_label(libros_form, "Título *", 0, 0)
mk_entry(libros_form, var_titulo, 0, 1, 24)

mk_label(libros_form, "Autor *", 0, 2)
mk_entry(libros_form, var_autor, 0, 3, 22)

mk_label(libros_form, "Categoría *", 1, 0)
mk_entry(libros_form, var_categoria, 1, 1, 18)

mk_label(libros_form, "Subcategoría", 1, 2)
mk_entry(libros_form, var_subcategoria, 1, 3, 18)

mk_label(libros_form, "Editorial", 2, 0)
mk_entry(libros_form, var_editorial, 2, 1, 18)

mk_label(libros_form, "Año", 2, 2)
mk_entry(libros_form, var_anio, 2, 3, 10)

mk_label(libros_form, "País", 3, 0)
combo_pais = ttk.Combobox(
    libros_form,
    textvariable=var_pais,
    values=Paises,
    width=18,
    font=("Segoe UI", 10),
    state="normal",
    style="Custom.TCombobox"
)
combo_pais.grid(row=3, column=1, sticky="w", padx=6, pady=4)

mk_label(libros_form, "Idioma", 3, 2)
combo_idioma = ttk.Combobox(
    libros_form,
    textvariable=var_idioma,
    values=Idiomas,
    width=18,
    font=("Segoe UI", 10),
    state="normal",
    style="Custom.TCombobox"
)
combo_idioma.grid(row=3, column=3, sticky="w", padx=6, pady=4)

mk_label(libros_form, "ISBN", 4, 0)
mk_entry(libros_form, var_isbn, 4, 1, 18)

mk_label(libros_form, "Ubicación", 4, 2)
mk_entry(libros_form, var_ubicacion, 4, 3, 18)

mk_label(libros_form, "Cantidad *", 5, 0)
mk_entry(libros_form, var_cantidad, 5, 1, 8)

mk_label(libros_form, "Páginas", 5, 2)
mk_entry(libros_form, var_cantidad_paginas, 5, 3, 10)

mk_label(libros_form, "Imagen", 6, 0)
frame_img_libro = Frame(libros_form, bg=COLOR_CARD)
frame_img_libro.grid(row=6, column=1, sticky="w", padx=6, pady=4)

Entry(
    frame_img_libro,
    textvariable=var_imagen_path,
    width=21,
    font=("Segoe UI", 10),
    bg="#fbfdff",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).pack(side=LEFT)

Checkbutton(
    libros_form,
    text="Infantil",
    variable=var_es_infantil,
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10),
    activebackground=COLOR_CARD,
    activeforeground=COLOR_TEXT,
    selectcolor="#d6f2d8"
).grid(row=6, column=2, columnspan=2, sticky="w", padx=6, pady=6)

mk_label(libros_form, "Descripción", 7, 0)
Entry(
    libros_form,
    textvariable=var_descripcion,
    width=68,
    font=("Segoe UI", 10),
    bg="#fbfdff",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).grid(row=7, column=1, columnspan=3, sticky="w", padx=6, pady=4)

buscador_libros = Frame(libros_main, bg=COLOR_BG)
buscador_libros.pack(fill="x", pady=(0, 8))

Label(
    buscador_libros,
    text="Buscar libro:",
    bg=COLOR_BG,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold")
).pack(side=LEFT, padx=(0, 8))

Entry(
    buscador_libros,
    textvariable=var_buscar_libro,
    width=42,
    font=("Segoe UI", 10),
    bg="white",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).pack(side=LEFT)

frame_libros_buttons = Frame(libros_main, bg=COLOR_BG, height=60)
frame_libros_buttons.pack(fill="x", pady=(0, 8))
frame_libros_buttons.pack_propagate(False)

tabla_libros_wrap = Frame(libros_main, bg=COLOR_BG)
tabla_libros_wrap.pack(fill="both", expand=True)

tree_libros = ttk.Treeview(
    tabla_libros_wrap,
    columns=("estado", "titulo", "autor", "categoria", "subcategoria", "anio", "cant", "disp"),
    show="headings",
    height=14
)

for col, txt, w in [
    ("estado", "Estado", 95),
    ("titulo", "Título", 240),
    ("autor", "Autor", 170),
    ("categoria", "Categoría", 120),
    ("subcategoria", "Subcategoría", 130),
    ("anio", "Año", 70),
    ("cant", "Total", 70),
    ("disp", "Disponibles", 95),
]:
    tree_libros.heading(col, text=txt)
    tree_libros.column(col, width=w, anchor="w")

scroll_y_libros = ttk.Scrollbar(tabla_libros_wrap, orient="vertical", command=tree_libros.yview)
tree_libros.configure(yscrollcommand=scroll_y_libros.set)

tree_libros.pack(side=LEFT, fill="both", expand=True)
scroll_y_libros.pack(side=RIGHT, fill=Y)

# =========================================================
# TAB SOCIOS
# =========================================================
tab_socios = Frame(notebook, bg=COLOR_BG)
notebook.add(tab_socios, text="Socios")

var_socio_nombre = StringVar()
var_socio_apellido = StringVar()
var_socio_dni = StringVar()
var_socio_tel = StringVar()
var_socio_email = StringVar()
var_socio_direccion = StringVar()
var_socio_activo = BooleanVar(value=True)
var_socio_obs = StringVar()
var_socio_imagen_path = StringVar()
var_buscar_socio = StringVar()

var_modalidad_cuota = StringVar(value="Mensual")
var_estado_cuota = StringVar(value="Pendiente")
var_ultimo_mes_pago = StringVar()
var_fecha_ultimo_pago = StringVar()
var_observacion_cuota = StringVar()

socios_main = Frame(tab_socios, bg=COLOR_BG)
socios_main.pack(fill="both", expand=True, padx=8, pady=8)

socios_form = LabelFrame(
    socios_main,
    text="Datos del socio",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=8,
    bd=2,
    relief="groove"
)
socios_form.pack(fill="x", pady=(0, 8))

mk_label(socios_form, "Nombre *", 0, 0)
mk_entry(socios_form, var_socio_nombre, 0, 1, 22)

mk_label(socios_form, "Apellido", 0, 2)
mk_entry(socios_form, var_socio_apellido, 0, 3, 22)

mk_label(socios_form, "DNI *", 1, 0)
mk_entry(socios_form, var_socio_dni, 1, 1, 16)

mk_label(socios_form, "Teléfono", 1, 2)
mk_entry(socios_form, var_socio_tel, 1, 3, 16)

mk_label(socios_form, "Email", 2, 0)
mk_entry(socios_form, var_socio_email, 2, 1, 24)

mk_label(socios_form, "Dirección", 2, 2)
mk_entry(socios_form, var_socio_direccion, 2, 3, 22)

mk_label(socios_form, "Imagen", 3, 0)
frame_img_socio = Frame(socios_form, bg=COLOR_CARD)
frame_img_socio.grid(row=3, column=1, sticky="w", padx=6, pady=4)

Entry(
    frame_img_socio,
    textvariable=var_socio_imagen_path,
    width=21,
    font=("Segoe UI", 10),
    bg="#fbfdff",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).pack(side=LEFT)

Checkbutton(
    socios_form,
    text="Socio activo",
    variable=var_socio_activo,
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10),
    activebackground=COLOR_CARD,
    activeforeground=COLOR_TEXT,
    selectcolor="#d6f2d8"
).grid(row=3, column=2, columnspan=2, sticky="w", padx=6, pady=6)

mk_label(socios_form, "Observaciones", 4, 0)
Entry(
    socios_form,
    textvariable=var_socio_obs,
    width=56,
    font=("Segoe UI", 10),
    bg="#fbfdff",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).grid(row=4, column=1, columnspan=3, sticky="w", padx=6, pady=4)

cuota_frame = LabelFrame(
    socios_main,
    text="Seguimiento de cuota",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=8,
    bd=2,
    relief="groove"
)
cuota_frame.pack(fill="x", pady=(0, 8))

mk_label(cuota_frame, "Modalidad", 0, 0)
combo_modalidad_cuota = ttk.Combobox(
    cuota_frame,
    textvariable=var_modalidad_cuota,
    values=MODALIDADES_CUOTA,
    width=18,
    font=("Segoe UI", 10),
    state="readonly",
    style="Custom.TCombobox"
)
combo_modalidad_cuota.grid(row=0, column=1, sticky="w", padx=6, pady=4)

mk_label(cuota_frame, "Estado cuota", 0, 2)
combo_estado_cuota = ttk.Combobox(
    cuota_frame,
    textvariable=var_estado_cuota,
    values=ESTADOS_CUOTA,
    width=18,
    font=("Segoe UI", 10),
    state="readonly",
    style="Custom.TCombobox"
)
combo_estado_cuota.grid(row=0, column=3, sticky="w", padx=6, pady=4)

mk_label(cuota_frame, "Último mes pago", 1, 0)
mk_entry(cuota_frame, var_ultimo_mes_pago, 1, 1, 18)

mk_label(cuota_frame, "Fecha último pago", 1, 2)
mk_entry(cuota_frame, var_fecha_ultimo_pago, 1, 3, 18)

mk_label(cuota_frame, "Observación cuota", 2, 0)
Entry(
    cuota_frame,
    textvariable=var_observacion_cuota,
    width=56,
    font=("Segoe UI", 10),
    bg="#fbfdff",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).grid(row=2, column=1, columnspan=3, sticky="w", padx=6, pady=4)

buscador_socios = Frame(socios_main, bg=COLOR_BG)
buscador_socios.pack(fill="x", pady=(0, 8))

Label(
    buscador_socios,
    text="Buscar socio:",
    bg=COLOR_BG,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold")
).pack(side=LEFT, padx=(0, 8))

Entry(
    buscador_socios,
    textvariable=var_buscar_socio,
    width=40,
    font=("Segoe UI", 10),
    bg="white",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).pack(side=LEFT)

frame_socios_buttons = Frame(socios_main, bg=COLOR_BG, height=60)
frame_socios_buttons.pack(fill="x", pady=(0, 8))
frame_socios_buttons.pack_propagate(False)

tabla_socios_wrap = Frame(socios_main, bg=COLOR_BG)
tabla_socios_wrap.pack(fill="both", expand=True, pady=(0, 8))

tree_socios = ttk.Treeview(
    tabla_socios_wrap,
    columns=("nombre", "dni", "telefono", "email", "activo", "prestamos_activos"),
    show="headings",
    height=10
)

for col, txt, w in [
    ("nombre", "Nombre", 220),
    ("dni", "DNI", 110),
    ("telefono", "Teléfono", 130),
    ("email", "Email", 220),
    ("activo", "Activo", 70),
    ("prestamos_activos", "Préstamos activos", 130),
]:
    tree_socios.heading(col, text=txt)
    tree_socios.column(col, width=w, anchor="w")

scroll_y_socios = ttk.Scrollbar(tabla_socios_wrap, orient="vertical", command=tree_socios.yview)
tree_socios.configure(yscrollcommand=scroll_y_socios.set)

tree_socios.pack(side=LEFT, fill="both", expand=True)
scroll_y_socios.pack(side=RIGHT, fill=Y)

historial_socio_frame = LabelFrame(
    socios_main,
    text="Historial rápido del socio seleccionado",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=8,
    bd=2,
    relief="groove"
)
historial_socio_frame.pack(fill="both", expand=True)

tree_historial_socio = ttk.Treeview(
    historial_socio_frame,
    columns=("libro", "categoria", "subcategoria", "fecha_prestamo", "fecha_vencimiento", "fecha_devolucion", "estado"),
    show="headings",
    height=6
)

for col, txt, w in [
    ("libro", "Libro", 170),
    ("categoria", "Categoría", 110),
    ("subcategoria", "Subcategoría", 120),
    ("fecha_prestamo", "Prestado", 125),
    ("fecha_vencimiento", "Vence", 125),
    ("fecha_devolucion", "Devuelto", 125),
    ("estado", "Estado", 85),
]:
    tree_historial_socio.heading(col, text=txt)
    tree_historial_socio.column(col, width=w, anchor="w")

tree_historial_socio.pack(fill="both", expand=True)

# =========================================================
# TAB PRÉSTAMOS
# =========================================================
tab_prestamos = Frame(notebook, bg=COLOR_BG)
notebook.add(tab_prestamos, text="Préstamos")

var_buscar_prestamo = StringVar()
var_solo_activos = BooleanVar(value=False)

prestamos_main = Frame(tab_prestamos, bg=COLOR_BG)
prestamos_main.pack(fill="both", expand=True, padx=8, pady=8)

prestamos_top = Frame(prestamos_main, bg=COLOR_BG)
prestamos_top.pack(fill="x", pady=(0, 8))

Label(
    prestamos_top,
    text="Buscar préstamo:",
    bg=COLOR_BG,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold")
).pack(side=LEFT, padx=(0, 8))

Entry(
    prestamos_top,
    textvariable=var_buscar_prestamo,
    width=38,
    font=("Segoe UI", 10),
    bg="white",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).pack(side=LEFT)

Checkbutton(
    prestamos_top,
    text="Mostrar solo activos",
    variable=var_solo_activos,
    bg=COLOR_BG,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10),
    activebackground=COLOR_BG,
    activeforeground=COLOR_TEXT,
    selectcolor="#d6f2d8"
).pack(side=LEFT, padx=16)

frame_prestamos_buttons = Frame(prestamos_main, bg=COLOR_BG, height=60)
frame_prestamos_buttons.pack(fill="x", pady=(0, 8))
frame_prestamos_buttons.pack_propagate(False)

tabla_prestamos_wrap = Frame(prestamos_main, bg=COLOR_BG)
tabla_prestamos_wrap.pack(fill="both", expand=True, pady=(0, 8))

tree_prestamos = ttk.Treeview(
    tabla_prestamos_wrap,
    columns=("libro", "categoria", "subcategoria", "socio", "dni", "fecha_prestamo", "fecha_vencimiento", "fecha_devolucion", "estado"),
    show="headings",
    height=13
)

for col, txt, w in [
    ("libro", "Libro", 170),
    ("categoria", "Categoría", 110),
    ("subcategoria", "Subcategoría", 120),
    ("socio", "Socio", 180),
    ("dni", "DNI", 90),
    ("fecha_prestamo", "Fecha préstamo", 125),
    ("fecha_vencimiento", "Vence", 125),
    ("fecha_devolucion", "Devuelto", 125),
    ("estado", "Estado", 85),
]:
    tree_prestamos.heading(col, text=txt)
    tree_prestamos.column(col, width=w, anchor="w")

scroll_y_prestamos = ttk.Scrollbar(tabla_prestamos_wrap, orient="vertical", command=tree_prestamos.yview)
tree_prestamos.configure(yscrollcommand=scroll_y_prestamos.set)

tree_prestamos.pack(side=LEFT, fill="both", expand=True)
scroll_y_prestamos.pack(side=RIGHT, fill=Y)

# =========================================================
# TAB ESTADÍSTICAS
# =========================================================
tab_estadisticas = Frame(notebook, bg=COLOR_BG)
notebook.add(tab_estadisticas, text="Estadísticas")

estadisticas_main = Frame(tab_estadisticas, bg=COLOR_BG)
estadisticas_main.pack(fill="both", expand=True, padx=8, pady=8)

var_stats_resumen = StringVar(value="Sin datos todavía")
var_stats_socios = StringVar(value="Sin datos todavía")
var_stats_categorias = StringVar(value="Sin datos todavía")
var_stats_subcategorias = StringVar(value="Sin datos todavía")
var_stats_libros = StringVar(value="Sin datos todavía")

titulo_stats = Frame(estadisticas_main, bg=COLOR_BG)
titulo_stats.pack(fill="x", pady=(0, 10))

Label(
    titulo_stats,
    text="Panel de estadísticas",
    bg=COLOR_BG,
    fg=COLOR_TEXT,
    font=("Segoe UI", 18, "bold")
).pack(anchor="w")

Label(
    titulo_stats,
    text="Indicadores generales y gráficos de circulación de la biblioteca",
    bg=COLOR_BG,
    fg="#4b647a",
    font=("Segoe UI", 10)
).pack(anchor="w", pady=(2, 0))

stats_cards_row1 = Frame(estadisticas_main, bg=COLOR_BG)
stats_cards_row1.pack(fill="x", pady=(0, 10))

card_resumen = stat_card(stats_cards_row1, COLOR_STAT_1, "Resumen general", var_stats_resumen)
card_resumen.pack(side=LEFT, fill="both", expand=True, padx=(0, 6))

card_socios = stat_card(stats_cards_row1, COLOR_STAT_2, "Socios más activos", var_stats_socios)
card_socios.pack(side=LEFT, fill="both", expand=True, padx=6)

stats_cards_row2 = Frame(estadisticas_main, bg=COLOR_BG)
stats_cards_row2.pack(fill="x", pady=(0, 10))

card_categorias = stat_card(stats_cards_row2, COLOR_STAT_3, "Categorías más pedidas", var_stats_categorias)
card_categorias.pack(side=LEFT, fill="both", expand=True, padx=(0, 6))

card_subcategorias = stat_card(stats_cards_row2, COLOR_STAT_4, "Subcategorías más pedidas", var_stats_subcategorias)
card_subcategorias.pack(side=LEFT, fill="both", expand=True, padx=6)

card_libros = stat_card(stats_cards_row2, COLOR_STAT_5, "Libros más pedidos", var_stats_libros)
card_libros.pack(side=LEFT, fill="both", expand=True, padx=(6, 0))

graficos_frame = LabelFrame(
    estadisticas_main,
    text="Gráficos",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold"),
    padx=12,
    pady=12,
    bd=2,
    relief="groove"
)
graficos_frame.pack(fill="x", pady=(6, 0))

Label(
    graficos_frame,
    text="Abrí gráficos para visualizar rápidamente qué se presta más y quiénes usan más la biblioteca.",
    bg=COLOR_CARD,
    fg="#4b647a",
    font=("Segoe UI", 10)
).pack(anchor="w", pady=(0, 8))

frame_estadisticas_buttons = Frame(graficos_frame, bg=COLOR_CARD, height=58)
frame_estadisticas_buttons.pack(fill="x")
frame_estadisticas_buttons.pack_propagate(False)

# =========================================================
# TAB LOGS
# =========================================================
tab_logs = Frame(notebook, bg=COLOR_BG)
notebook.add(tab_logs, text="Logs")

var_buscar_logs = StringVar()

logs_main = Frame(tab_logs, bg=COLOR_BG)
logs_main.pack(fill="both", expand=True, padx=8, pady=8)

logs_header = LabelFrame(
    logs_main,
    text="Registro de actividad",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=8,
    bd=2,
    relief="groove"
)
logs_header.pack(fill="x", pady=(0, 8))

logs_header_top = Frame(logs_header, bg=COLOR_CARD)
logs_header_top.pack(fill="x")

Label(
    logs_header_top,
    text="Aquí se registra quién usó la aplicación y qué acciones principales realizó.",
    bg=COLOR_CARD,
    fg="#4b647a",
    font=("Segoe UI", 10)
).pack(anchor="w", side=LEFT)

try:
    if os.path.exists(logo_2_path):
        img_logs = Image.open(logo_2_path)
        img_logs.thumbnail((70, 70))
        tk_img_logs = ImageTk.PhotoImage(img_logs)

        lbl_logo_logs = Label(logs_header_top, image=tk_img_logs, bg=COLOR_CARD)
        lbl_logo_logs.image = tk_img_logs
        lbl_logo_logs.pack(side=RIGHT, padx=10)
except Exception:
    pass

logs_search_frame = Frame(logs_header, bg=COLOR_CARD)
logs_search_frame.pack(fill="x", pady=(10, 0))

Label(
    logs_search_frame,
    text="Buscar log:",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=("Segoe UI", 10, "bold")
).pack(side=LEFT, padx=(0, 8))

Entry(
    logs_search_frame,
    textvariable=var_buscar_logs,
    width=48,
    font=("Segoe UI", 10),
    bg="white",
    fg=COLOR_TEXT,
    relief="solid",
    bd=1
).pack(side=LEFT)

Label(
    logs_search_frame,
    text="Buscar por fecha, persona, usuario, acción o detalle",
    bg=COLOR_CARD,
    fg="#6b7c8f",
    font=("Segoe UI", 9)
).pack(side=LEFT, padx=12)

frame_logs_buttons = Frame(logs_main, bg=COLOR_BG, height=58)
frame_logs_buttons.pack(fill="x", pady=(0, 8))
frame_logs_buttons.pack_propagate(False)

tabla_logs_wrap = Frame(logs_main, bg=COLOR_BG)
tabla_logs_wrap.pack(fill="both", expand=True)

tree_logs = ttk.Treeview(
    tabla_logs_wrap,
    columns=("fecha_hora", "nombre_persona", "usuario_sistema", "accion", "detalle"),
    show="headings",
    height=18
)

for col, txt, w in [
    ("fecha_hora", "Fecha y hora", 160),
    ("nombre_persona", "Persona", 180),
    ("usuario_sistema", "Usuario sistema", 130),
    ("accion", "Acción", 170),
    ("detalle", "Detalle", 620),
]:
    tree_logs.heading(col, text=txt)
    tree_logs.column(col, width=w, anchor="w")

scroll_y_logs = ttk.Scrollbar(tabla_logs_wrap, orient="vertical", command=tree_logs.yview)
tree_logs.configure(yscrollcommand=scroll_y_logs.set)

tree_logs.pack(side=LEFT, fill="both", expand=True)
scroll_y_logs.pack(side=RIGHT, fill=Y)

# =========================================================
# EXPORTS
# =========================================================
__all__ = [
    "ventana_principal",

    # Libros
    "var_titulo", "var_autor", "var_categoria", "var_subcategoria", "var_es_infantil",
    "var_editorial", "var_anio", "var_pais", "var_idioma", "var_isbn",
    "var_ubicacion", "var_cantidad", "var_cantidad_paginas", "var_descripcion",
    "var_imagen_path", "var_buscar_libro", "tree_libros", "frame_libros_buttons",
    "combo_pais", "combo_idioma", "frame_img_libro",

    # Socios
    "var_socio_nombre", "var_socio_apellido", "var_socio_dni", "var_socio_tel",
    "var_socio_email", "var_socio_direccion", "var_socio_activo", "var_socio_obs",
    "var_socio_imagen_path", "var_buscar_socio", "tree_socios",
    "frame_socios_buttons", "tree_historial_socio", "frame_img_socio",
    "var_modalidad_cuota", "var_estado_cuota", "var_ultimo_mes_pago",
    "var_fecha_ultimo_pago", "var_observacion_cuota",

    # Préstamos
    "var_buscar_prestamo", "var_solo_activos", "tree_prestamos", "frame_prestamos_buttons",

    # Estadísticas
    "var_stats_resumen", "var_stats_socios", "var_stats_categorias",
    "var_stats_subcategorias", "var_stats_libros", "frame_estadisticas_buttons",

    # Logs
    "tree_logs", "frame_logs_buttons", "var_buscar_logs"
]










