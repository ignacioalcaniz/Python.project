"""
Controlador principal de la Biblioteca Popular Nelly Llorens.
"""

import os
from datetime import datetime
from tkinter import (
    Toplevel, StringVar, Entry, Label, Button, Menu,
    messagebox, Frame, LEFT, Text
)
from tkinter import ttk
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk, ImageDraw

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from proyectoPY.view.view import (
    ventana_principal,

    # LIBROS
    var_titulo, var_autor, var_categoria, var_subcategoria, var_es_infantil,
    var_editorial, var_anio, var_pais, var_idioma, var_isbn,
    var_ubicacion, var_cantidad, var_descripcion, var_imagen_path,
    var_buscar_libro, tree_libros, frame_libros_buttons, frame_img_libro,
    var_cantidad_paginas,

    # SOCIOS
    var_socio_nombre, var_socio_apellido, var_socio_dni, var_socio_tel,
    var_socio_email, var_socio_direccion, var_socio_activo, var_socio_obs,
    var_socio_imagen_path, var_buscar_socio, tree_socios,
    frame_socios_buttons, tree_historial_socio, frame_img_socio,
    var_modalidad_cuota, var_estado_cuota, var_ultimo_mes_pago,
    var_fecha_ultimo_pago, var_observacion_cuota,

    # PRÉSTAMOS
    var_buscar_prestamo, var_solo_activos, tree_prestamos, frame_prestamos_buttons,

    # ESTADÍSTICAS
    var_stats_resumen, var_stats_socios, var_stats_categorias,
    var_stats_subcategorias, var_stats_libros, frame_estadisticas_buttons,

    # LOGS
    tree_logs, frame_logs_buttons, var_buscar_logs
)

from proyectoPY.model.model import BibliotecaModel, db
from proyectoPY.patterns.decorators import with_transaction
from proyectoPY.patterns.observer import (
    event_bus,
    EVT_LIBRO_CREADO, EVT_LIBRO_MODIFICADO, EVT_LIBRO_ELIMINADO,
    EVT_SOCIO_CREADO, EVT_PRESTAMO_REALIZADO, EVT_DEVOLUCION_REGISTRADA
)
from proyectoPY.infra.log_client import send_log


class BibliotecaController:
    def __init__(self):
        self.model = BibliotecaModel()

        self.usuario_sistema_actual = None
        self.nombre_persona_actual = None

        self._mostrar_login_inicial()

    # ======================================================
    # LOGIN
    # ======================================================
    def _mostrar_login_inicial(self):
        ventana_principal.withdraw()

        login = Toplevel()
        login.title("Ingreso al sistema")
        login.geometry("480x360")
        login.resizable(False, False)
        login.configure(bg="#eef4f8")
        login.protocol("WM_DELETE_WINDOW", ventana_principal.destroy)

        card = Frame(login, bg="white", bd=2, relief="groove")
        card.pack(fill="both", expand=True, padx=24, pady=24)

        Label(
            card,
            text="Biblioteca Popular Nelly Llorens",
            bg="white",
            fg="#183247",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(24, 8))

        Label(
            card,
            text="Ingreso de superusuario",
            bg="white",
            fg="#4b647a",
            font=("Segoe UI", 10)
        ).pack(pady=(0, 18))

        usuario_var = StringVar()
        password_var = StringVar()
        nombre_var = StringVar()

        form = Frame(card, bg="white")
        form.pack(pady=6)

        Label(form, text="Usuario", bg="white", fg="#183247", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=6, pady=6)
        Entry(form, textvariable=usuario_var, width=28, font=("Segoe UI", 10), relief="solid", bd=1).grid(row=0, column=1, padx=6, pady=6)

        Label(form, text="Contraseña", bg="white", fg="#183247", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=6, pady=6)
        Entry(form, textvariable=password_var, width=28, show="*", font=("Segoe UI", 10), relief="solid", bd=1).grid(row=1, column=1, padx=6, pady=6)

        Label(form, text="Nombre de quien usa la app", bg="white", fg="#183247", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", padx=6, pady=6)
        Entry(form, textvariable=nombre_var, width=28, font=("Segoe UI", 10), relief="solid", bd=1).grid(row=2, column=1, padx=6, pady=6)

        def ingresar():
            usuario = usuario_var.get().strip()
            password = password_var.get().strip()
            nombre_persona = nombre_var.get().strip()

            if not usuario or not password or not nombre_persona:
                return messagebox.showwarning("Faltan datos", "Complete usuario, contraseña y nombre.", parent=login)

            u = self.model.verificar_login(usuario, password)
            if not u:
                return messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.", parent=login)

            self.usuario_sistema_actual = u.usuario
            self.nombre_persona_actual = nombre_persona

            self.model.registrar_log(
                nombre_persona=self.nombre_persona_actual,
                usuario_sistema=self.usuario_sistema_actual,
                accion="Inicio de sesión",
                detalle=f"Ingreso al sistema por {self.nombre_persona_actual}"
            )

            login.destroy()
            ventana_principal.deiconify()
            self._configurar_menu()
            self._configurar_botones()
            self._configurar_bindings()
            self._suscribir_eventos()
            self.actualizar_todo()

        botones = Frame(card, bg="white")
        botones.pack(pady=18)

        Button(
            botones,
            text="Ingresar",
            command=ingresar,
            bg="#1976d2",
            fg="white",
            width=16,
            relief="flat"
        ).pack(side=LEFT, padx=6)

        Button(
            botones,
            text="Salir",
            command=ventana_principal.destroy,
            bg="#78909c",
            fg="white",
            width=14,
            relief="flat"
        ).pack(side=LEFT, padx=6)

        login.transient()
        login.grab_set()
        login.focus_force()

    # ======================================================
    # CONFIGURACIÓN
    # ======================================================
    def _configurar_menu(self):
        menu_bar = Menu(ventana_principal)

        archivo_menu = Menu(menu_bar, tearoff=0)
        archivo_menu.add_command(label="Exportar Libros", command=self.exportar_libros)
        archivo_menu.add_command(label="Exportar Socios", command=self.exportar_socios)
        archivo_menu.add_command(label="Exportar Préstamos", command=self.exportar_prestamos)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Backup CSV total", command=self.backup_total_csv)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=ventana_principal.quit)

        ayuda_menu = Menu(menu_bar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.acerca_de)

        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)
        menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ventana_principal.config(menu=menu_bar)

    def _configurar_botones(self):
        Button(
            frame_img_libro,
            text="...",
            command=self.seleccionar_imagen_libro,
            bg="#1976d2",
            fg="white",
            width=3,
            relief="flat"
        ).pack(side=LEFT, padx=(6, 0))

        Button(
            frame_img_socio,
            text="...",
            command=self.seleccionar_imagen_socio,
            bg="#1976d2",
            fg="white",
            width=3,
            relief="flat"
        ).pack(side=LEFT, padx=(6, 0))

        Button(frame_libros_buttons, text="Guardar", command=self.guardar_libro,
               bg="#2e7d32", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Modificar", command=self.modificar_libro,
               bg="#f9a825", fg="black", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Eliminar", command=self.eliminar_libro,
               bg="#c62828", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Prestar", command=self.ui_prestar,
               bg="#5e35b1", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Devolver", command=self.ui_devolver_libro,
               bg="#455a64", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Detalle", command=self.ver_detalle_libro,
               bg="#1976d2", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Buscar", command=self.ui_consultar_libros,
               bg="#00897b", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Resumen", command=self.ui_resumen_libro,
               bg="#3949ab", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_libros_buttons, text="Limpiar", command=self.limpiar_form_libros,
               bg="#78909c", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)

        Button(frame_socios_buttons, text="Guardar socio", command=self.guardar_socio,
               bg="#2e7d32", fg="white", width=14, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_socios_buttons, text="Modificar socio", command=self.modificar_socio,
               bg="#f9a825", fg="black", width=14, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_socios_buttons, text="Eliminar socio", command=self.eliminar_socio,
               bg="#c62828", fg="white", width=14, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_socios_buttons, text="Consultar socio", command=self.ui_consultar_socio_detalle,
               bg="#1976d2", fg="white", width=14, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_socios_buttons, text="Historial", command=self.ui_historial_socio,
               bg="#1565c0", fg="white", width=14, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_socios_buttons, text="Resumen socio", command=self.ui_resumen_socio,
               bg="#3949ab", fg="white", width=14, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_socios_buttons, text="Limpiar", command=self.limpiar_form_socios,
               bg="#78909c", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)

        Button(frame_prestamos_buttons, text="Registrar devolución", command=self.ui_devolver_desde_prestamos,
               bg="#455a64", fg="white", width=18, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_prestamos_buttons, text="Renovar préstamo", command=self.ui_renovar_prestamo,
               bg="#00897b", fg="white", width=16, relief="flat").pack(side=LEFT, padx=5, pady=6)
        Button(frame_prestamos_buttons, text="Refrescar", command=self.actualizar_todo,
               bg="#1976d2", fg="white", width=12, relief="flat").pack(side=LEFT, padx=5, pady=6)

        Button(frame_estadisticas_buttons, text="Gráfico libros", command=self.grafico_top_libros,
               bg="#1976d2", fg="white", width=16, relief="flat").pack(side=LEFT, padx=5, pady=8)
        Button(frame_estadisticas_buttons, text="Gráfico socios", command=self.grafico_top_socios,
               bg="#00897b", fg="white", width=16, relief="flat").pack(side=LEFT, padx=5, pady=8)
        Button(frame_estadisticas_buttons, text="Gráfico categorías", command=self.grafico_top_categorias,
               bg="#5e35b1", fg="white", width=18, relief="flat").pack(side=LEFT, padx=5, pady=8)
        Button(frame_estadisticas_buttons, text="Gráfico subcategorías", command=self.grafico_top_subcategorias,
               bg="#3949ab", fg="white", width=20, relief="flat").pack(side=LEFT, padx=5, pady=8)

        Button(frame_logs_buttons, text="Refrescar logs", command=self.actualizar_logs,
               bg="#455a64", fg="white", width=14, relief="flat").pack(side=LEFT, padx=5, pady=8)

    def _configurar_bindings(self):
        var_buscar_libro.trace("w", lambda *args: self.buscar_libros())
        var_buscar_socio.trace("w", lambda *args: self.buscar_socios())
        var_buscar_prestamo.trace("w", lambda *args: self.actualizar_prestamos())
        var_solo_activos.trace("w", lambda *args: self.actualizar_prestamos())
        var_buscar_logs.trace("w", lambda *args: self.actualizar_logs())

        tree_libros.bind("<<TreeviewSelect>>", lambda e: self.cargar_form_libro_desde_tabla())
        tree_libros.bind("<Double-1>", lambda e: self.ver_detalle_libro())

        tree_socios.bind("<<TreeviewSelect>>", lambda e: self.cargar_form_socio_desde_tabla())

    def _suscribir_eventos(self):
        def on_evt(payload, tag):
            send_log(f"{tag}: {payload}")
            self.actualizar_todo()

        event_bus.subscribe(EVT_LIBRO_CREADO, lambda p: on_evt(p, EVT_LIBRO_CREADO))
        event_bus.subscribe(EVT_LIBRO_MODIFICADO, lambda p: on_evt(p, EVT_LIBRO_MODIFICADO))
        event_bus.subscribe(EVT_LIBRO_ELIMINADO, lambda p: on_evt(p, EVT_LIBRO_ELIMINADO))
        event_bus.subscribe(EVT_PRESTAMO_REALIZADO, lambda p: on_evt(p, EVT_PRESTAMO_REALIZADO))
        event_bus.subscribe(EVT_DEVOLUCION_REGISTRADA, lambda p: on_evt(p, EVT_DEVOLUCION_REGISTRADA))
        event_bus.subscribe(EVT_SOCIO_CREADO, lambda p: on_evt(p, EVT_SOCIO_CREADO))

    # ======================================================
    # HELPERS
    # ======================================================
    def _registrar_log(self, accion, detalle=None):
        if not self.usuario_sistema_actual or not self.nombre_persona_actual:
            return
        self.model.registrar_log(
            nombre_persona=self.nombre_persona_actual,
            usuario_sistema=self.usuario_sistema_actual,
            accion=accion,
            detalle=detalle
        )

    def actualizar_todo(self):
        self.actualizar_libros()
        self.actualizar_socios()
        self.actualizar_prestamos()
        self.actualizar_estadisticas()
        self.actualizar_logs()

    def _libro_seleccionado_id(self):
        sel = tree_libros.focus()
        return tree_libros.item(sel, "text") if sel else None

    def _socio_seleccionado_id(self):
        sel = tree_socios.focus()
        return tree_socios.item(sel, "text") if sel else None

    def _prestamo_seleccionado_id(self):
        sel = tree_prestamos.focus()
        return tree_prestamos.item(sel, "text") if sel else None

    def _validar_numero_entero(self, valor, nombre):
        if not valor.strip().isdigit():
            raise ValueError(f"El campo '{nombre}' debe ser numérico.")

    def _parsear_fecha_ddmmyyyy(self, valor):
        valor = valor.strip()
        if not valor:
            return None
        return datetime.strptime(valor, "%d/%m/%Y").date()

    def _ordenar_treeview(self, tree, col, reverse=False):
        datos = [(tree.set(k, col), k) for k in tree.get_children("")]
        datos.sort(reverse=reverse)
        for index, (_, k) in enumerate(datos):
            tree.move(k, "", index)
        tree.heading(col, command=lambda: self._ordenar_treeview(tree, col, not reverse))

    def _aplicar_ordenacion_tabla(self, tree):
        for col in tree["columns"]:
            tree.heading(col, command=lambda c=col: self._ordenar_treeview(tree, c, False))

    def _resolver_ruta_imagen(self, ruta):
        if not ruta:
            return None
        ruta = ruta.strip().strip('"')
        if not ruta:
            return None

        if os.path.exists(ruta):
            return ruta

        abs1 = os.path.abspath(ruta)
        if os.path.exists(abs1):
            return abs1

        base_dir = os.getcwd()
        abs2 = os.path.join(base_dir, ruta)
        if os.path.exists(abs2):
            return abs2

        return None

    def _crear_placeholder(self, ancho, alto, texto):
        img = Image.new("RGB", (ancho, alto), color=(245, 245, 245))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, ancho - 1, alto - 1), outline=(180, 180, 180), width=2)
        draw.text((18, alto // 2 - 10), texto, fill=(100, 100, 100))
        return img

    def _crear_preview(self, parent, ruta_imagen, texto_default="Imagen no disponible", ancho=210, alto=280):
        cont = Frame(parent, bg="#ffffff", bd=1, relief="solid", width=ancho, height=alto)
        cont.pack_propagate(False)

        ruta_real = self._resolver_ruta_imagen(ruta_imagen)

        try:
            if ruta_real:
                img = Image.open(ruta_real)
            else:
                img = self._crear_placeholder(ancho - 20, alto - 20, texto_default)

            img.thumbnail((ancho - 16, alto - 16))
            tk_img = ImageTk.PhotoImage(img)
            lbl_img = Label(cont, image=tk_img, bg="#ffffff")
            lbl_img.image = tk_img
            lbl_img.pack(expand=True)
            return cont
        except Exception:
            img = self._crear_placeholder(ancho - 20, alto - 20, texto_default)
            tk_img = ImageTk.PhotoImage(img)
            lbl_img = Label(cont, image=tk_img, bg="#ffffff")
            lbl_img.image = tk_img
            lbl_img.pack(expand=True)
            return cont

    def _mostrar_grafico_barras(self, titulo, etiquetas, valores, ylabel="Cantidad"):
        if not etiquetas or not valores:
            return messagebox.showinfo("Sin datos", "Todavía no hay datos para graficar.")

        win = Toplevel(ventana_principal)
        win.title(titulo)
        win.geometry("980x620")
        win.configure(bg="#f6fbff")

        figura = Figure(figsize=(9, 5), dpi=100)
        ax = figura.add_subplot(111)
        ax.bar(etiquetas, valores)
        ax.set_title(titulo)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=30)

        canvas = FigureCanvasTkAgg(figura, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)

        botones = Frame(win, bg="#f6fbff", height=50)
        botones.pack(fill="x", padx=12, pady=(0, 12))
        botones.pack_propagate(False)

        Button(botones, text="Cerrar", command=win.destroy,
               bg="#78909c", fg="white", width=14, relief="flat").pack(side=LEFT, pady=10)

    def seleccionar_imagen_libro(self):
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen del libro",
            initialdir=os.path.join(os.getcwd(), "imagenes_libros"),
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if ruta:
            var_imagen_path.set(ruta)

    def seleccionar_imagen_socio(self):
        from tkinter import filedialog
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen del socio",
            initialdir=os.path.join(os.getcwd(), "imagenes_socios"),
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if ruta:
            var_socio_imagen_path.set(ruta)

    def limpiar_form_libros(self):
        var_titulo.set("")
        var_autor.set("")
        var_categoria.set("")
        var_subcategoria.set("")
        var_es_infantil.set(False)
        var_editorial.set("")
        var_anio.set("")
        var_pais.set("")
        var_idioma.set("Español")
        var_isbn.set("")
        var_ubicacion.set("")
        var_cantidad.set("")
        var_cantidad_paginas.set("")
        var_descripcion.set("")
        var_imagen_path.set("")
        for item in tree_libros.selection():
            tree_libros.selection_remove(item)

    def limpiar_form_socios(self):
        var_socio_nombre.set("")
        var_socio_apellido.set("")
        var_socio_dni.set("")
        var_socio_tel.set("")
        var_socio_email.set("")
        var_socio_direccion.set("")
        var_socio_activo.set(True)
        var_socio_obs.set("")
        var_socio_imagen_path.set("")

        var_modalidad_cuota.set("Mensual")
        var_estado_cuota.set("Pendiente")
        var_ultimo_mes_pago.set("")
        var_fecha_ultimo_pago.set("")
        var_observacion_cuota.set("")

        tree_historial_socio.delete(*tree_historial_socio.get_children())
        for item in tree_socios.selection():
            tree_socios.selection_remove(item)

    def acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "Biblioteca Popular Nelly Llorens\nSistema de gestión de libros, socios, préstamos y estadísticas."
        )

    # ======================================================
    # LIBROS
    # ======================================================
    def _validar_libro_campos(self):
        if not var_titulo.get().strip():
            raise ValueError("El campo 'Título' es obligatorio.")
        if not var_autor.get().strip():
            raise ValueError("El campo 'Autor' es obligatorio.")
        if not var_categoria.get().strip():
            raise ValueError("El campo 'Categoría' es obligatorio.")
        if not var_cantidad.get().strip():
            raise ValueError("El campo 'Cantidad' es obligatorio.")

        self._validar_numero_entero(var_cantidad.get(), "Cantidad")

        if var_anio.get().strip():
            self._validar_numero_entero(var_anio.get(), "Año")

        if var_cantidad_paginas.get().strip():
            self._validar_numero_entero(var_cantidad_paginas.get(), "Cantidad de páginas")

    def actualizar_libros(self):
        tree_libros.delete(*tree_libros.get_children())
        for l in self.model.libros_todos():
            tree_libros.insert(
                "", "end", text=l["id"],
                values=(
                    l["estado"],
                    l["titulo"],
                    l["autor"],
                    l["categoria"],
                    l["subcategoria"],
                    l["anio"],
                    l["cantidad"],
                    l["disponibles"]
                )
            )
        self._aplicar_ordenacion_tabla(tree_libros)

    def buscar_libros(self):
        filtro = var_buscar_libro.get().strip().lower()
        tree_libros.delete(*tree_libros.get_children())

        for l in self.model.libros_filtrados(texto=filtro):
            tree_libros.insert(
                "", "end", text=l["id"],
                values=(
                    l["estado"],
                    l["titulo"],
                    l["autor"],
                    l["categoria"],
                    l["subcategoria"],
                    l["anio"],
                    l["cantidad"],
                    l["disponibles"]
                )
            )
        self._aplicar_ordenacion_tabla(tree_libros)

    def cargar_form_libro_desde_tabla(self):
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return
        libro = self.model.libro_por_id(id_libro)
        if not libro:
            return

        var_titulo.set(libro["titulo"])
        var_autor.set(libro["autor"])
        var_categoria.set(libro["categoria"])
        var_subcategoria.set(libro["subcategoria"])
        var_es_infantil.set(bool(libro["es_infantil"]))
        var_editorial.set(libro["editorial"])
        var_anio.set(str(libro["anio"]) if libro["anio"] != "" else "")
        var_pais.set(libro["pais"])
        var_idioma.set(libro["idioma"])
        var_isbn.set(libro["isbn"])
        var_ubicacion.set(libro["ubicacion"])
        var_cantidad.set(str(libro["cantidad"]))
        var_cantidad_paginas.set(str(libro["cantidad_paginas"]) if libro["cantidad_paginas"] != "" else "")
        var_descripcion.set(libro["descripcion"])
        var_imagen_path.set(libro["imagen_path"])

    @with_transaction(db)
    def guardar_libro(self):
        try:
            self._validar_libro_campos()
            libro = self.model.libro_crear(
                titulo=var_titulo.get().strip(),
                autor=var_autor.get().strip(),
                categoria=var_categoria.get().strip(),
                subcategoria=var_subcategoria.get().strip() or None,
                es_infantil=bool(var_es_infantil.get()),
                editorial=var_editorial.get().strip() or None,
                anio=int(var_anio.get()) if var_anio.get().strip() else None,
                pais=var_pais.get().strip() or None,
                idioma=var_idioma.get().strip() or "Español",
                isbn=var_isbn.get().strip() or None,
                ubicacion=var_ubicacion.get().strip() or None,
                cantidad=int(var_cantidad.get()),
                cantidad_paginas=int(var_cantidad_paginas.get()) if var_cantidad_paginas.get().strip() else None,
                descripcion=var_descripcion.get().strip() or None,
                imagen_path=var_imagen_path.get().strip() or None
            )
            self._registrar_log("Guardó libro", f"{libro.titulo} | Autor: {libro.autor}")
            messagebox.showinfo("Éxito", "Libro agregado correctamente.")
            self.actualizar_todo()
            self.limpiar_form_libros()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def modificar_libro(self):
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro.")

        try:
            self._validar_libro_campos()
            self.model.libro_modificar(
                id_libro,
                titulo=var_titulo.get().strip(),
                autor=var_autor.get().strip(),
                categoria=var_categoria.get().strip(),
                subcategoria=var_subcategoria.get().strip() or None,
                es_infantil=bool(var_es_infantil.get()),
                editorial=var_editorial.get().strip() or None,
                anio=int(var_anio.get()) if var_anio.get().strip() else None,
                pais=var_pais.get().strip() or None,
                idioma=var_idioma.get().strip() or "Español",
                isbn=var_isbn.get().strip() or None,
                ubicacion=var_ubicacion.get().strip() or None,
                cantidad=int(var_cantidad.get()),
                cantidad_paginas=int(var_cantidad_paginas.get()) if var_cantidad_paginas.get().strip() else None,
                descripcion=var_descripcion.get().strip() or None,
                imagen_path=var_imagen_path.get().strip() or None
            )
            self._registrar_log("Modificó libro", var_titulo.get().strip())
            messagebox.showinfo("Éxito", "Libro modificado correctamente.")
            self.actualizar_todo()
            self.limpiar_form_libros()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def eliminar_libro(self):
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro.")
        if not messagebox.askyesno("Confirmar", "¿Seguro que querés eliminar este libro?"):
            return

        try:
            libro = self.model.libro_por_id(id_libro)
            self.model.libro_eliminar(id_libro)
            self._registrar_log("Eliminó libro", libro["titulo"] if libro else f"ID {id_libro}")
            messagebox.showinfo("Éxito", "Libro eliminado correctamente.")
            self.actualizar_todo()
            self.limpiar_form_libros()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ver_detalle_libro(self):
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro.")

        libro = self.model.libro_por_id(id_libro)
        if not libro:
            return messagebox.showerror("Error", "No se encontró el libro.")

        prestamos_activos = self.model.prestamos_activos_del_libro(id_libro)

        win = Toplevel(ventana_principal)
        win.title(f"Detalle del libro - {libro['titulo']}")
        win.geometry("1020x720")
        win.configure(bg="#f6fbff")

        cabecera = Frame(win, bg="#dff1ff", padx=18, pady=18)
        cabecera.pack(fill="x")

        Label(cabecera, text=libro["titulo"], bg="#dff1ff", fg="#183247",
              font=("Segoe UI", 20, "bold")).pack(anchor="w")
        Label(cabecera, text=f"Autor: {libro['autor']}", bg="#dff1ff", fg="#244f30",
              font=("Segoe UI", 11)).pack(anchor="w", pady=2)
        Label(cabecera, text=f"Estado: {libro['estado']} | Disponibles: {libro['disponibles']} / {libro['cantidad']}",
              bg="#dff1ff", fg="#244f30", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)

        cuerpo = Frame(win, bg="#f6fbff", padx=18, pady=18)
        cuerpo.pack(fill="both", expand=True)

        panel_sup = Frame(cuerpo, bg="#f6fbff")
        panel_sup.pack(fill="x", pady=(0, 10))

        portada = self._crear_preview(panel_sup, libro["imagen_path"], "Portada no disponible", 210, 300)
        portada.pack(side=LEFT, padx=(0, 24))

        datos = Frame(panel_sup, bg="#f6fbff")
        datos.pack(side=LEFT, fill="both", expand=True)

        lineas = [
            f"Categoría: {libro['categoria']}",
            f"Subcategoría: {libro['subcategoria'] or '-'}",
            f"Infantil: {'Sí' if libro['es_infantil'] else 'No'}",
            f"Editorial: {libro['editorial'] or '-'}",
            f"Año: {libro['anio'] or '-'}",
            f"País: {libro['pais'] or '-'}",
            f"Idioma: {libro['idioma'] or '-'}",
            f"ISBN: {libro['isbn'] or '-'}",
            f"Ubicación: {libro['ubicacion'] or '-'}",
            f"Páginas: {libro['cantidad_paginas'] or '-'}",
            f"Fecha de alta: {libro['fecha_alta']}",
            f"Préstamos históricos: {libro['total_prestamos_historicos']}",
        ]

        for texto in lineas:
            Label(datos, text=texto, bg="#f6fbff", fg="#183247",
                  font=("Segoe UI", 11)).pack(anchor="w", pady=4)

        Label(cuerpo, text="Descripción", bg="#f6fbff", fg="#183247",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 6))

        txt = Text(cuerpo, height=7, wrap="word", font=("Segoe UI", 10),
                   bg="white", relief="solid", bd=1)
        txt.pack(fill="x", expand=False)
        txt.insert("1.0", libro["descripcion"] or "Sin descripción cargada.")
        txt.config(state="disabled")

        Label(cuerpo, text="Préstamos activos de este libro", bg="#f6fbff", fg="#183247",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 6))

        tree = ttk.Treeview(
            cuerpo,
            columns=("socio", "dni", "fecha_prestamo", "fecha_vencimiento", "estado"),
            show="headings",
            height=6
        )

        for col, txt_h, w in [
            ("socio", "Socio", 220),
            ("dni", "DNI", 100),
            ("fecha_prestamo", "Fecha préstamo", 150),
            ("fecha_vencimiento", "Vence", 150),
            ("estado", "Estado", 100),
        ]:
            tree.heading(col, text=txt_h)
            tree.column(col, width=w, anchor="w")

        tree.pack(fill="both", expand=True)

        for p in prestamos_activos:
            iid = tree.insert("", "end", values=(p["socio"], p["dni"], p["fecha_prestamo"], p["fecha_vencimiento"], p["estado"]))
            if p["estado"] == "Vencido":
                tree.item(iid, tags=("vencido",))
        tree.tag_configure("vencido", background="#ffd9d9")

    def ui_consultar_libros(self):
        win = Toplevel(ventana_principal)
        win.title("Buscar libros")
        win.geometry("1180x680")
        win.configure(bg="#f6fbff")

        top = Frame(win, bg="#f6fbff")
        top.pack(fill="x", padx=10, pady=8)

        Label(top, text="Búsqueda unificada:", bg="#f6fbff", fg="#183247", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=6, pady=6)

        q = StringVar()
        Entry(top, textvariable=q, width=40, font=("Segoe UI", 10), bg="white", relief="solid", bd=1).grid(row=0, column=1, sticky="w", padx=6, pady=6)

        Label(top, text="Categoría:", bg="#f6fbff", fg="#183247", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="w", padx=6, pady=6)
        cat_var = StringVar()
        Entry(top, textvariable=cat_var, width=18, font=("Segoe UI", 10), bg="white", relief="solid", bd=1).grid(row=0, column=3, sticky="w", padx=6, pady=6)

        Label(top, text="Subcategoría:", bg="#f6fbff", fg="#183247", font=("Segoe UI", 10, "bold")).grid(row=0, column=4, sticky="w", padx=6, pady=6)
        subcat_var = StringVar()
        Entry(top, textvariable=subcat_var, width=18, font=("Segoe UI", 10), bg="white", relief="solid", bd=1).grid(row=0, column=5, sticky="w", padx=6, pady=6)

        from tkinter import BooleanVar
        infantil_bool = BooleanVar(value=False)
        disponibles_bool = BooleanVar(value=False)

        Checkbutton(top, text="Solo infantil", variable=infantil_bool,
                    bg="#f6fbff", fg="#183247", font=("Segoe UI", 10),
                    selectcolor="#d6f2d8").grid(row=1, column=0, sticky="w", padx=6, pady=6)

        Checkbutton(top, text="Solo disponibles", variable=disponibles_bool,
                    bg="#f6fbff", fg="#183247", font=("Segoe UI", 10),
                    selectcolor="#d6f2d8").grid(row=1, column=1, sticky="w", padx=6, pady=6)

        tree = ttk.Treeview(
            win,
            columns=("estado", "titulo", "autor", "categoria", "subcategoria", "anio", "disp"),
            show="headings",
            height=20
        )

        for col, txt_h, w in [
            ("estado", "Estado", 95),
            ("titulo", "Título", 250),
            ("autor", "Autor", 190),
            ("categoria", "Categoría", 120),
            ("subcategoria", "Subcategoría", 130),
            ("anio", "Año", 70),
            ("disp", "Disponibles", 90),
        ]:
            tree.heading(col, text=txt_h)
            tree.column(col, width=w, anchor="w")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def cargar():
            tree.delete(*tree.get_children())
            resultados = self.model.libros_filtrados(
                texto=q.get(),
                infantil=True if infantil_bool.get() else None,
                categoria=cat_var.get(),
                subcategoria=subcat_var.get(),
                solo_disponibles=bool(disponibles_bool.get())
            )

            for l in resultados:
                tree.insert("", "end", text=l["id"],
                            values=(l["estado"], l["titulo"], l["autor"], l["categoria"], l["subcategoria"], l["anio"], l["disponibles"]))
            self._aplicar_ordenacion_tabla(tree)

        def abrir_detalle(_=None):
            sel = tree.focus()
            if not sel:
                return
            libro_id = tree.item(sel, "text")
            for item in tree_libros.get_children():
                if str(tree_libros.item(item, "text")) == str(libro_id):
                    tree_libros.focus(item)
                    tree_libros.selection_set(item)
                    break
            self.ver_detalle_libro()

        for var in [q, cat_var, subcat_var]:
            var.trace("w", lambda *args: cargar())
        infantil_bool.trace("w", lambda *args: cargar())
        disponibles_bool.trace("w", lambda *args: cargar())

        tree.bind("<Double-1>", abrir_detalle)
        cargar()

    def ui_resumen_libro(self):
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro.")

        data = self.model.libro_estadisticas(id_libro)
        if not data:
            return messagebox.showerror("Error", "No se pudo obtener el resumen del libro.")

        texto_socios = "\n".join([f"- {x['socio']}: {x['cantidad']}" for x in data["socios_frecuentes"]]) or "Sin datos"

        win = Toplevel(ventana_principal)
        win.title("Resumen del libro")
        win.geometry("720x520")
        win.configure(bg="#f6fbff")

        card = Frame(win, bg="white", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=18, pady=18)

        Label(card, text=data["libro"], bg="white", fg="#183247",
              font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 6))
        Label(card, text=f"Total préstamos: {data['total_prestamos']}", bg="white", fg="#183247",
              font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=4)
        Label(card, text=f"Préstamos activos: {data['prestamos_activos']}", bg="white", fg="#183247",
              font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=4)
        Label(card, text=f"Préstamos devueltos: {data['prestamos_devueltos']}", bg="white", fg="#183247",
              font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=4)

        Label(card, text="Socios que más lo pidieron", bg="white", fg="#183247",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 6))

        txt = Text(card, height=10, wrap="word", font=("Segoe UI", 10), bg="#fbfdff", relief="solid", bd=1)
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        txt.insert("1.0", texto_socios)
        txt.config(state="disabled")

    # ======================================================
    # SOCIOS
    # ======================================================
    def _validar_socio_campos(self):
        if not var_socio_nombre.get().strip():
            raise ValueError("El campo 'Nombre' es obligatorio.")
        if not var_socio_dni.get().strip():
            raise ValueError("El campo 'DNI' es obligatorio.")

        self._validar_numero_entero(var_socio_dni.get(), "DNI")

    def actualizar_socios(self):
        tree_socios.delete(*tree_socios.get_children())
        for s in self.model.socios_todos():
            tree_socios.insert(
                "", "end", text=s["id"],
                values=(
                    s["nombre"],
                    s["dni"],
                    s["telefono"],
                    s["email"],
                    "Sí" if s["activo"] else "No",
                    s["prestamos_activos"]
                )
            )
        self._aplicar_ordenacion_tabla(tree_socios)

    def buscar_socios(self):
        filtro = var_buscar_socio.get().strip().lower()
        tree_socios.delete(*tree_socios.get_children())

        for s in self.model.socios_filtrados(texto=filtro):
            tree_socios.insert(
                "", "end", text=s["id"],
                values=(
                    s["nombre"],
                    s["dni"],
                    s["telefono"],
                    s["email"],
                    "Sí" if s["activo"] else "No",
                    s["prestamos_activos"]
                )
            )
        self._aplicar_ordenacion_tabla(tree_socios)

    def cargar_form_socio_desde_tabla(self):
        id_socio = self._socio_seleccionado_id()
        if not id_socio:
            return
        socio = self.model.socio_por_id(id_socio)
        if not socio:
            return

        var_socio_nombre.set(socio["nombre"])
        var_socio_apellido.set(socio["apellido"])
        var_socio_dni.set(socio["dni"])
        var_socio_tel.set(socio["telefono"])
        var_socio_email.set(socio["email"])
        var_socio_direccion.set(socio["direccion"])
        var_socio_activo.set(bool(socio["activo"]))
        var_socio_obs.set(socio["observaciones"])
        var_socio_imagen_path.set(socio["imagen_path"])

        var_modalidad_cuota.set(socio["modalidad_cuota"])
        var_estado_cuota.set(socio["estado_cuota"])
        var_ultimo_mes_pago.set(socio["ultimo_mes_pago"])
        var_fecha_ultimo_pago.set("" if socio["fecha_ultimo_pago"] == "-" else socio["fecha_ultimo_pago"])
        var_observacion_cuota.set(socio["observacion_cuota"])

        self.cargar_historial_socio_seleccionado()

    @with_transaction(db)
    def guardar_socio(self):
        try:
            self._validar_socio_campos()

            fecha_ultimo_pago = self._parsear_fecha_ddmmyyyy(var_fecha_ultimo_pago.get()) if var_fecha_ultimo_pago.get().strip() else None

            socio = self.model.socio_crear(
                nombre=var_socio_nombre.get().strip(),
                apellido=var_socio_apellido.get().strip() or None,
                dni=var_socio_dni.get().strip(),
                telefono=var_socio_tel.get().strip() or None,
                email=var_socio_email.get().strip() or None,
                direccion=var_socio_direccion.get().strip() or None,
                activo=bool(var_socio_activo.get()),
                observaciones=var_socio_obs.get().strip() or None,
                imagen_path=var_socio_imagen_path.get().strip() or None,
                modalidad_cuota=var_modalidad_cuota.get().strip() or "Mensual",
                estado_cuota=var_estado_cuota.get().strip() or "Pendiente",
                ultimo_mes_pago=var_ultimo_mes_pago.get().strip() or None,
                fecha_ultimo_pago=fecha_ultimo_pago,
                observacion_cuota=var_observacion_cuota.get().strip() or None
            )

            self._registrar_log("Guardó socio", f"{socio.nombre} | DNI: {socio.dni}")
            messagebox.showinfo("Éxito", "Socio agregado correctamente.")
            self.actualizar_todo()
            self.limpiar_form_socios()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def modificar_socio(self):
        id_socio = self._socio_seleccionado_id()
        if not id_socio:
            return messagebox.showwarning("Seleccionar", "Seleccione un socio.")

        try:
            self._validar_socio_campos()

            fecha_ultimo_pago = self._parsear_fecha_ddmmyyyy(var_fecha_ultimo_pago.get()) if var_fecha_ultimo_pago.get().strip() else None

            self.model.socio_modificar(
                id_socio,
                nombre=var_socio_nombre.get().strip(),
                apellido=var_socio_apellido.get().strip() or None,
                dni=var_socio_dni.get().strip(),
                telefono=var_socio_tel.get().strip() or None,
                email=var_socio_email.get().strip() or None,
                direccion=var_socio_direccion.get().strip() or None,
                activo=bool(var_socio_activo.get()),
                observaciones=var_socio_obs.get().strip() or None,
                imagen_path=var_socio_imagen_path.get().strip() or None,
                modalidad_cuota=var_modalidad_cuota.get().strip() or "Mensual",
                estado_cuota=var_estado_cuota.get().strip() or "Pendiente",
                ultimo_mes_pago=var_ultimo_mes_pago.get().strip() or None,
                fecha_ultimo_pago=fecha_ultimo_pago,
                observacion_cuota=var_observacion_cuota.get().strip() or None
            )

            self._registrar_log("Modificó socio", f"{var_socio_nombre.get().strip()} | DNI: {var_socio_dni.get().strip()}")
            messagebox.showinfo("Éxito", "Socio modificado correctamente.")
            self.actualizar_todo()
            self.limpiar_form_socios()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def eliminar_socio(self):
        id_socio = self._socio_seleccionado_id()
        if not id_socio:
            return messagebox.showwarning("Seleccionar", "Seleccione un socio.")
        if not messagebox.askyesno("Confirmar", "¿Seguro que querés eliminar este socio?"):
            return

        try:
            socio = self.model.socio_por_id(id_socio)
            self.model.socio_eliminar(id_socio)
            self._registrar_log("Eliminó socio", f"{socio['nombre']} | DNI: {socio['dni']}" if socio else f"ID {id_socio}")
            messagebox.showinfo("Éxito", "Socio eliminado correctamente.")
            self.actualizar_todo()
            self.limpiar_form_socios()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ui_consultar_socio_detalle(self):
        id_socio = self._socio_seleccionado_id()
        if not id_socio:
            return messagebox.showwarning("Seleccionar", "Seleccione un socio.")

        socio = self.model.socio_por_id(id_socio)
        if not socio:
            return messagebox.showerror("Error", "No se encontró el socio.")

        win = Toplevel(ventana_principal)
        win.title(f"Detalle del socio - {socio['nombre']} {socio['apellido']}")
        win.geometry("1020x720")
        win.configure(bg="#f6fbff")

        cabecera = Frame(win, bg="#dff1ff", padx=18, pady=18)
        cabecera.pack(fill="x")

        nombre_completo = f"{socio['nombre']} {socio['apellido']}".strip()

        Label(cabecera, text=nombre_completo, bg="#dff1ff", fg="#183247",
              font=("Segoe UI", 20, "bold")).pack(anchor="w")
        Label(cabecera, text=f"DNI: {socio['dni']}", bg="#dff1ff", fg="#244f30",
              font=("Segoe UI", 11)).pack(anchor="w", pady=2)
        Label(cabecera, text=f"Estado: {'Activo' if socio['activo'] else 'Inactivo'} | Préstamos activos: {socio['prestamos_activos']} | Históricos: {socio['prestamos_historicos']}",
              bg="#dff1ff", fg="#244f30", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)

        cuerpo = Frame(win, bg="#f6fbff", padx=18, pady=18)
        cuerpo.pack(fill="both", expand=True)

        panel_sup = Frame(cuerpo, bg="#f6fbff")
        panel_sup.pack(fill="x", pady=(0, 10))

        foto = self._crear_preview(panel_sup, socio.get("imagen_path", ""), "Socio sin imagen", 210, 280)
        foto.pack(side=LEFT, padx=(0, 24))

        datos = Frame(panel_sup, bg="#f6fbff")
        datos.pack(side=LEFT, fill="both", expand=True)

        lineas = [
            f"Nombre: {socio['nombre']}",
            f"Apellido: {socio['apellido'] or '-'}",
            f"DNI: {socio['dni']}",
            f"Teléfono: {socio['telefono'] or '-'}",
            f"Email: {socio['email'] or '-'}",
            f"Dirección: {socio['direccion'] or '-'}",
            f"Fecha de alta: {socio['fecha_alta']}",
            f"Estado del socio: {'Activo' if socio['activo'] else 'Inactivo'}",
            f"Préstamos activos: {socio['prestamos_activos']}",
            f"Préstamos históricos: {socio['prestamos_historicos']}",
            f"Modalidad cuota: {socio['modalidad_cuota'] or '-'}",
            f"Estado cuota: {socio['estado_cuota'] or '-'}",
            f"Último mes pago: {socio['ultimo_mes_pago'] or '-'}",
            f"Fecha último pago: {socio['fecha_ultimo_pago'] or '-'}",
        ]

        for texto in lineas:
            Label(datos, text=texto, bg="#f6fbff", fg="#183247",
                  font=("Segoe UI", 11)).pack(anchor="w", pady=4)

        Label(cuerpo, text="Observaciones", bg="#f6fbff", fg="#183247",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 6))
        txt_obs = Text(cuerpo, height=4, wrap="word", font=("Segoe UI", 10), bg="white", relief="solid", bd=1)
        txt_obs.pack(fill="x", expand=False)
        txt_obs.insert("1.0", socio["observaciones"] or "Sin observaciones cargadas.")
        txt_obs.config(state="disabled")

        Label(cuerpo, text="Observación de cuota", bg="#f6fbff", fg="#183247",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 6))
        txt_cuota = Text(cuerpo, height=4, wrap="word", font=("Segoe UI", 10), bg="white", relief="solid", bd=1)
        txt_cuota.pack(fill="x", expand=False)
        txt_cuota.insert("1.0", socio["observacion_cuota"] or "Sin observación de cuota.")
        txt_cuota.config(state="disabled")

    def ui_historial_socio(self):
        id_socio = self._socio_seleccionado_id()
        if not id_socio:
            return messagebox.showwarning("Seleccionar", "Seleccione un socio.")

        socio = self.model.socio_por_id(id_socio)
        historial = self.model.historial_socio(id_socio)

        win = Toplevel(ventana_principal)
        win.title(f"Historial del socio - {socio['nombre']} {socio['apellido']}")
        win.geometry("1100x680")
        win.configure(bg="#f6fbff")

        top = Frame(win, bg="#dff1ff", padx=18, pady=12)
        top.pack(fill="x")

        Label(top, text=f"Historial de {socio['nombre']} {socio['apellido']}".strip(),
              bg="#dff1ff", fg="#183247", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        Label(top, text=f"DNI: {socio['dni']} | Préstamos activos: {socio['prestamos_activos']} | Préstamos históricos: {socio['prestamos_historicos']}",
              bg="#dff1ff", fg="#244f30", font=("Segoe UI", 10)).pack(anchor="w", pady=2)

        tree = ttk.Treeview(
            win,
            columns=("libro", "categoria", "subcategoria", "fecha_prestamo", "fecha_vencimiento", "fecha_devolucion", "estado"),
            show="headings",
            height=20
        )

        for col, txt_h, w in [
            ("libro", "Libro", 220),
            ("categoria", "Categoría", 130),
            ("subcategoria", "Subcategoría", 130),
            ("fecha_prestamo", "Fecha préstamo", 140),
            ("fecha_vencimiento", "Vence", 140),
            ("fecha_devolucion", "Devuelto", 140),
            ("estado", "Estado", 100),
        ]:
            tree.heading(col, text=txt_h)
            tree.column(col, width=w, anchor="w")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for item in historial:
            iid = tree.insert("", "end", values=(
                item["libro"], item["categoria"], item["subcategoria"],
                item["fecha_prestamo"], item["fecha_vencimiento"],
                item["fecha_devolucion"], item["estado"]
            ))
            if item["estado"] == "Vencido":
                tree.item(iid, tags=("vencido",))
        tree.tag_configure("vencido", background="#ffd9d9")
        self._aplicar_ordenacion_tabla(tree)

    def ui_resumen_socio(self):
        id_socio = self._socio_seleccionado_id()
        if not id_socio:
            return messagebox.showwarning("Seleccionar", "Seleccione un socio.")

        data = self.model.socio_estadisticas(id_socio)
        if not data:
            return messagebox.showerror("Error", "No se pudo obtener el resumen del socio.")

        win = Toplevel(ventana_principal)
        win.title("Resumen del socio")
        win.geometry("760x580")
        win.configure(bg="#f6fbff")

        card = Frame(win, bg="white", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=18, pady=18)

        Label(card, text=data["socio"], bg="white", fg="#183247",
              font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 6))
        Label(card, text=f"Total préstamos: {data['total_prestamos']}", bg="white", fg="#183247", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)
        Label(card, text=f"Préstamos activos: {data['prestamos_activos']}", bg="white", fg="#183247", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)
        Label(card, text=f"Categoría favorita: {data['categoria_favorita'] or '-'}", bg="white", fg="#183247", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)
        Label(card, text=f"Subcategoría favorita: {data['subcategoria_favorita'] or '-'}", bg="white", fg="#183247", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)
        Label(card, text=f"Preferencia: {data['preferencia_infantil'] or '-'}", bg="white", fg="#183247", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=3)

        Label(card, text="Libros más pedidos", bg="white", fg="#183247",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(18, 6))

        libros_txt = "\n".join([f"- {x['titulo']}: {x['cantidad']}" for x in data["libros"]]) or "Sin datos"

        txt = Text(card, height=12, wrap="word", font=("Segoe UI", 10), bg="#fbfdff", relief="solid", bd=1)
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        txt.insert("1.0", libros_txt)
        txt.config(state="disabled")

    def cargar_historial_socio_seleccionado(self):
        id_socio = self._socio_seleccionado_id()
        if not id_socio:
            return

        tree_historial_socio.delete(*tree_historial_socio.get_children())

        for item in self.model.historial_socio(id_socio):
            iid = tree_historial_socio.insert(
                "", "end", text=item["prestamo_id"],
                values=(
                    item["libro"],
                    item["categoria"],
                    item["subcategoria"],
                    item["fecha_prestamo"],
                    item["fecha_vencimiento"],
                    item["fecha_devolucion"],
                    item["estado"]
                )
            )
            if item["estado"] == "Vencido":
                tree_historial_socio.item(iid, tags=("vencido",))

        tree_historial_socio.tag_configure("vencido", background="#ffd9d9")
        self._aplicar_ordenacion_tabla(tree_historial_socio)

    # ======================================================
    # PRÉSTAMOS
    # ======================================================
    def actualizar_prestamos(self):
        filtro = var_buscar_prestamo.get().strip().lower()
        solo_activos = bool(var_solo_activos.get())

        tree_prestamos.delete(*tree_prestamos.get_children())

        for p in self.model.prestamos_filtrados(texto=filtro, solo_activos=solo_activos):
            iid = tree_prestamos.insert(
                "", "end", text=p["id"],
                values=(
                    p["libro"],
                    p["categoria"],
                    p["subcategoria"],
                    p["socio"],
                    p["dni"],
                    p["fecha_prestamo"],
                    p["fecha_vencimiento"],
                    p["fecha_devolucion"],
                    p["estado"]
                )
            )
            if p["estado"] == "Vencido":
                tree_prestamos.item(iid, tags=("vencido",))

        tree_prestamos.tag_configure("vencido", background="#ffd9d9")
        self._aplicar_ordenacion_tabla(tree_prestamos)

    @with_transaction(db)
    def ui_prestar(self):
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro para prestar.")

        win = Toplevel(ventana_principal)
        win.title("Seleccionar socio para préstamo")
        win.geometry("820x580")
        win.configure(bg="#f6fbff")

        Label(win, text="Buscar socio (nombre / DNI / email):",
              bg="#f6fbff", fg="#183247", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=8)

        q = StringVar()
        Entry(win, textvariable=q, width=42, font=("Segoe UI", 10), bg="white",
              relief="solid", bd=1).pack(anchor="w", padx=10)

        venc_wrap = Frame(win, bg="#f6fbff")
        venc_wrap.pack(fill="x", padx=10, pady=8)

        Label(venc_wrap, text="Fecha de vencimiento (opcional, DD/MM/AAAA):",
              bg="#f6fbff", fg="#183247", font=("Segoe UI", 10, "bold")).pack(side=LEFT)

        fecha_venc_var = StringVar()
        Entry(venc_wrap, textvariable=fecha_venc_var, width=16, font=("Segoe UI", 10), bg="white", relief="solid", bd=1).pack(side=LEFT, padx=10)

        tree = ttk.Treeview(
            win,
            columns=("nombre", "dni", "telefono", "email", "activo"),
            show="headings",
            height=14
        )

        for col, txt_h, w in [
            ("nombre", "Nombre", 220),
            ("dni", "DNI", 110),
            ("telefono", "Teléfono", 130),
            ("email", "Email", 180),
            ("activo", "Activo", 80),
        ]:
            tree.heading(col, text=txt_h)
            tree.column(col, width=w, anchor="w")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def cargar():
            tree.delete(*tree.get_children())
            for s in self.model.socios_filtrados(texto=q.get()):
                tree.insert("", "end", text=s["id"],
                            values=(s["nombre"], s["dni"], s["telefono"], s["email"], "Sí" if s["activo"] else "No"))

        def prestar_sel():
            sel = tree.focus()
            if not sel:
                return messagebox.showwarning("Seleccionar", "Seleccione un socio.")

            id_socio = tree.item(sel, "text")
            try:
                fecha_venc = self._parsear_fecha_ddmmyyyy(fecha_venc_var.get()) if fecha_venc_var.get().strip() else None
                prestamo = self.model.prestar(id_libro, id_socio, fecha_vencimiento=fecha_venc)
                detalle = f"Libro: {prestamo.libro.titulo} | Socio: {prestamo.socio.nombre} {prestamo.socio.apellido or ''}".strip()
                self._registrar_log("Registró préstamo", detalle)
                messagebox.showinfo("Éxito", "Préstamo registrado correctamente.")
                self.actualizar_todo()
                self.limpiar_form_libros()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        botones = Frame(win, bg="#f6fbff", height=56)
        botones.pack(fill="x", padx=10, pady=8)
        botones.pack_propagate(False)

        Button(botones, text="Confirmar préstamo", command=prestar_sel,
               bg="#5e35b1", fg="white", width=18, relief="flat").pack(side=LEFT, padx=4, pady=10)
        Button(botones, text="Cancelar", command=win.destroy,
               bg="#78909c", fg="white", width=14, relief="flat").pack(side=LEFT, padx=4, pady=10)

        q.trace("w", lambda *args: cargar())
        tree.bind("<Double-1>", lambda e: prestar_sel())
        self._aplicar_ordenacion_tabla(tree)
        cargar()

    def ui_devolver_libro(self):
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro.")

        prestamos = self.model.prestamos_activos_por_libro(id_libro)
        if not prestamos:
            return messagebox.showinfo("Info", "Ese libro no tiene préstamos activos.")

        win = Toplevel(ventana_principal)
        win.title("Devolver libro")
        win.geometry("760x440")
        win.configure(bg="#f6fbff")

        tree = ttk.Treeview(
            win,
            columns=("socio", "fecha_prestamo", "fecha_vencimiento", "estado"),
            show="headings",
            height=12
        )

        for col, txt_h, w in [
            ("socio", "Socio", 260),
            ("fecha_prestamo", "Fecha préstamo", 150),
            ("fecha_vencimiento", "Vence", 150),
            ("estado", "Estado", 110),
        ]:
            tree.heading(col, text=txt_h)
            tree.column(col, width=w, anchor="w")

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for p in prestamos:
            estado = "Vencido" if p["vencido"] else "Activo"
            iid = tree.insert("", "end", text=p["id"], values=(p["socio"], p["fecha_prestamo"], p["fecha_vencimiento"], estado))
            if p["vencido"]:
                tree.item(iid, tags=("vencido",))
        tree.tag_configure("vencido", background="#ffd9d9")
        self._aplicar_ordenacion_tabla(tree)

        def devolver():
            sel = tree.focus()
            if not sel:
                return
            pid = tree.item(sel, "text")
            try:
                prestamo = self.model.devolver(pid)
                detalle = f"Libro: {prestamo.libro.titulo} | Socio: {prestamo.socio.nombre} {prestamo.socio.apellido or ''}".strip()
                self._registrar_log("Registró devolución", detalle)
                messagebox.showinfo("Éxito", "Devolución registrada correctamente.")
                self.actualizar_todo()
                self.limpiar_form_libros()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        botones = Frame(win, bg="#f6fbff", height=56)
        botones.pack(fill="x", padx=10, pady=8)
        botones.pack_propagate(False)

        Button(botones, text="Confirmar devolución", command=devolver,
               bg="#455a64", fg="white", width=18, relief="flat").pack(side=LEFT, padx=4, pady=10)
        Button(botones, text="Cancelar", command=win.destroy,
               bg="#78909c", fg="white", width=14, relief="flat").pack(side=LEFT, padx=4, pady=10)

    def ui_devolver_desde_prestamos(self):
        pid = self._prestamo_seleccionado_id()
        if not pid:
            return messagebox.showwarning("Seleccionar", "Seleccione un préstamo.")

        try:
            prestamo = self.model.devolver(pid)
            detalle = f"Libro: {prestamo.libro.titulo} | Socio: {prestamo.socio.nombre} {prestamo.socio.apellido or ''}".strip()
            self._registrar_log("Registró devolución", detalle)
            messagebox.showinfo("Éxito", "Devolución registrada correctamente.")
            self.actualizar_todo()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ui_renovar_prestamo(self):
        pid = self._prestamo_seleccionado_id()
        if not pid:
            return messagebox.showwarning("Seleccionar", "Seleccione un préstamo.")

        dias_str = askstring("Renovar préstamo", "¿Cuántos días querés agregar? (ej: 7)")
        if not dias_str:
            return
        if not dias_str.strip().isdigit():
            return messagebox.showerror("Error", "La cantidad de días debe ser numérica.")

        try:
            prestamo = self.model.renovar_prestamo(pid, dias=int(dias_str.strip()))
            detalle = f"Libro: {prestamo.libro.titulo} | Nuevo vencimiento: {prestamo.fecha_vencimiento.strftime('%d/%m/%Y') if prestamo.fecha_vencimiento else '-'}"
            self._registrar_log("Renovó préstamo", detalle)
            messagebox.showinfo("Éxito", "Préstamo renovado correctamente.")
            self.actualizar_todo()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ======================================================
    # ESTADÍSTICAS
    # ======================================================
    def actualizar_estadisticas(self):
        resumen = self.model.resumen_dashboard()
        top_socios = self.model.top_socios()
        top_categorias = self.model.top_categorias()
        top_subcategorias = self.model.top_subcategorias()
        top_libros = self.model.top_libros()

        var_stats_resumen.set(
            f"Libros: {resumen['total_libros']} | Socios: {resumen['total_socios']} | "
            f"Activos: {resumen['prestamos_activos']} | Vencidos: {resumen['prestamos_vencidos']} | "
            f"Históricos: {resumen['prestamos_historicos']}"
        )

        var_stats_socios.set(" | ".join([f"{x['nombre']} ({x['cantidad']})" for x in top_socios]) if top_socios else "Sin datos todavía")
        var_stats_categorias.set(" | ".join([f"{x['categoria']} ({x['cantidad']})" for x in top_categorias]) if top_categorias else "Sin datos todavía")
        var_stats_subcategorias.set(" | ".join([f"{x['subcategoria']} ({x['cantidad']})" for x in top_subcategorias]) if top_subcategorias else "Sin datos todavía")
        var_stats_libros.set(" | ".join([f"{x['titulo']} ({x['cantidad']})" for x in top_libros]) if top_libros else "Sin datos todavía")

    def grafico_top_libros(self):
        data = self.model.top_libros(10)
        self._mostrar_grafico_barras("Libros más pedidos", [x["titulo"] for x in data], [x["cantidad"] for x in data])

    def grafico_top_socios(self):
        data = self.model.top_socios(10)
        self._mostrar_grafico_barras("Socios con más préstamos", [x["nombre"] for x in data], [x["cantidad"] for x in data])

    def grafico_top_categorias(self):
        data = self.model.top_categorias(10)
        self._mostrar_grafico_barras("Categorías más pedidas", [x["categoria"] for x in data], [x["cantidad"] for x in data])

    def grafico_top_subcategorias(self):
        data = self.model.top_subcategorias(10)
        self._mostrar_grafico_barras("Subcategorías más pedidas", [x["subcategoria"] for x in data], [x["cantidad"] for x in data])

    # ======================================================
    # LOGS
    # ======================================================
    def actualizar_logs(self):
        filtro = var_buscar_logs.get().strip().lower()

        tree_logs.delete(*tree_logs.get_children())

        for log in self.model.logs_todos():
            texto_log = " ".join([
                str(log["fecha_hora"]),
                str(log["nombre_persona"]),
                str(log["usuario_sistema"]),
                str(log["accion"]),
                str(log["detalle"])
            ]).lower()

            if filtro and filtro not in texto_log:
                continue

            tree_logs.insert(
                "", "end", text=log["id"],
                values=(
                    log["fecha_hora"],
                    log["nombre_persona"],
                    log["usuario_sistema"],
                    log["accion"],
                    log["detalle"]
                )
            )

        self._aplicar_ordenacion_tabla(tree_logs)

    # ======================================================
    # EXPORT / BACKUP
    # ======================================================
    def exportar_libros(self):
        path = self.model.exportar_libros_csv()
        messagebox.showinfo("Exportado", f"Se generó:\n{path}")

    def exportar_socios(self):
        path = self.model.exportar_socios_csv()
        messagebox.showinfo("Exportado", f"Se generó:\n{path}")

    def exportar_prestamos(self):
        path = self.model.exportar_prestamos_csv()
        messagebox.showinfo("Exportado", f"Se generó:\n{path}")

    def backup_total_csv(self):
        paths = self.model.backup_total_csv()
        messagebox.showinfo(
            "Backup generado",
            "Se exportaron los CSV:\n\n"
            f"Libros: {paths['libros']}\n"
            f"Socios: {paths['socios']}\n"
            f"Préstamos: {paths['prestamos']}"
        )











