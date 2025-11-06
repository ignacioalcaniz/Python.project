"""
Módulo controller
-----------------
Controlador principal de la Biblioteca Popular Nelly Llorens.
UX profesional:
- Prestar: ventana con buscador + lista de socios (doble-click) → sin cambiar de pestaña
- Devolver: ventana con préstamos activos del libro seleccionado → sin ID manual

Responsabilidades:
- Coordinar la comunicación entre la vista (Tkinter) y el modelo (Peewee/MySQL).
- Validar datos de entrada (libros y socios).
- Ejecutar CRUD de Libros y Socios.
- Gestionar préstamos y devoluciones.
- Publicar eventos (Observer) y enviar logs por socket.
- Exportar CSV.
"""

from tkinter import Toplevel, StringVar, Entry, Label, Button, Menu, messagebox
from tkinter import ttk
from tkinter.simpledialog import askstring

# ----- VISTA (no se toca: sólo la usamos) -----
from proyectoPY.view.view import (
    ventana_principal,
    # Libros
    tab_libros, var_titulo, var_autor, var_categoria, var_editorial,
    var_anio, var_pais, var_ubicacion, var_cantidad, var_precio,
    var_buscar_libro, tree_libros, frame_libros_buttons,
    # Socios
    tab_socios, var_socio_nombre, var_socio_dni, var_socio_tel, var_socio_email,
    tree_socios, frame_socios_buttons
)

# ----- MODELO -----
from proyectoPY.model.model import BibliotecaModel, db

# ----- DECORADORES -----
from proyectoPY.patterns.decorators import with_transaction

# ----- OBSERVER + LOG CLIENTE -----
from proyectoPY.patterns.observer import (
    event_bus,
    EVT_LIBRO_CREADO, EVT_LIBRO_MODIFICADO, EVT_LIBRO_ELIMINADO,
    EVT_SOCIO_CREADO, EVT_PRESTAMO_REALIZADO, EVT_DEVOLUCION_REGISTRADA
)
from proyectoPY.infra.log_client import send_log


class BibliotecaController:
    """
    Controlador principal: maneja Libros + Socios + Préstamos con validaciones estrictas,
    ventanas modales de consulta, y operaciones transaccionales (decoradores).
    """

    # ======================================================================
    # INIT
    # ======================================================================
    def __init__(self):
        self.model = BibliotecaModel()

        self._configurar_menu()
        self._configurar_botones()
        self._suscribir_eventos()

        # Carga inicial de datos en grillas
        self.actualizar_libros()
        self.actualizar_socios()

        # Búsqueda rápida en la pestaña Libros
        var_buscar_libro.trace("w", lambda *args: self.buscar_libros())

    # ======================================================================
    # MENÚ SUPERIOR
    # ======================================================================
    def _configurar_menu(self):
        """
        Crea el menú superior con opciones de exportar y salir.
        """
        menu_bar = Menu(ventana_principal)
        archivo_menu = Menu(menu_bar, tearoff=0)
        archivo_menu.add_command(label="Exportar Libros", command=self.exportar_libros)
        archivo_menu.add_command(label="Exportar Socios", command=self.exportar_socios)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=ventana_principal.quit)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)
        ventana_principal.config(menu=menu_bar)

    # ======================================================================
    # BOTONES (encastrados en los frames de la vista)
    # ======================================================================
    def _configurar_botones(self):
        """
        Conecta los botones de la vista con callbacks del controlador.
        """
        # Libros
        Button(frame_libros_buttons, text="Guardar", command=self.guardar_libro, bg="#2e7d32", fg="white", width=12).grid(row=0, column=0, padx=6, pady=6)
        Button(frame_libros_buttons, text="Modificar", command=self.modificar_libro, bg="#f9a825", fg="black", width=12).grid(row=0, column=1, padx=6, pady=6)
        Button(frame_libros_buttons, text="Eliminar", command=self.eliminar_libro, bg="#c62828", fg="white", width=12).grid(row=0, column=2, padx=6, pady=6)
        Button(frame_libros_buttons, text="Prestar", command=self.ui_prestar, bg="#8A2BE2", fg="white", width=12).grid(row=0, column=3, padx=6, pady=6)
        Button(frame_libros_buttons, text="Devolver", command=self.ui_devolver, bg="#2F4F4F", fg="white", width=12).grid(row=0, column=4, padx=6, pady=6)
        Button(frame_libros_buttons, text="Consultar", command=self.ui_consultar_libros, bg="#1976D2", fg="white", width=12).grid(row=0, column=5, padx=6, pady=6)

        # Socios
        Button(frame_socios_buttons, text="Guardar Socio", command=self.guardar_socio, bg="#2e7d32", fg="white", width=14).grid(row=0, column=0, padx=6, pady=6)
        Button(frame_socios_buttons, text="Modificar Socio", command=self.modificar_socio, bg="#f9a825", fg="black", width=14).grid(row=0, column=1, padx=6, pady=6)
        Button(frame_socios_buttons, text="Eliminar Socio", command=self.eliminar_socio, bg="#c62828", fg="white", width=14).grid(row=0, column=2, padx=6, pady=6)
        Button(frame_socios_buttons, text="Consultar Socio", command=self.ui_consultar_socios, bg="#1976D2", fg="white", width=14).grid(row=0, column=3, padx=6, pady=6)

    # ======================================================================
    # OBSERVER (suscripción a eventos del dominio)
    # ======================================================================
    def _suscribir_eventos(self):
        """
        Se suscribe a los eventos del EventBus para refrescar UI y
        enviar logs al servidor de eventos.
        """
        def on_evt(payload, tag):
            send_log(f"{tag}: {payload}")
            self.actualizar_libros()  # refrescamos libros en cambios y préstamos

        event_bus.subscribe(EVT_LIBRO_CREADO, lambda p: on_evt(p, EVT_LIBRO_CREADO))
        event_bus.subscribe(EVT_LIBRO_MODIFICADO, lambda p: on_evt(p, EVT_LIBRO_MODIFICADO))
        event_bus.subscribe(EVT_LIBRO_ELIMINADO, lambda p: on_evt(p, EVT_LIBRO_ELIMINADO))
        event_bus.subscribe(EVT_PRESTAMO_REALIZADO, lambda p: on_evt(p, EVT_PRESTAMO_REALIZADO))
        event_bus.subscribe(EVT_DEVOLUCION_REGISTRADA, lambda p: on_evt(p, EVT_DEVOLUCION_REGISTRADA))
        event_bus.subscribe(EVT_SOCIO_CREADO, lambda p: send_log(f"{EVT_SOCIO_CREADO}: {p}"))

    # ======================================================================
    # LIBROS – UTILIDADES
    # ======================================================================
    def _libro_seleccionado_id(self):
        """
        Obtiene el ID (texto) del item seleccionado en el tree_libros.
        """
        sel = tree_libros.focus()
        if not sel:
            return None
        return tree_libros.item(sel, "text")

    # ======================================================================
    # LIBROS – CRUD + BÚSQUEDA
    # ======================================================================
    def actualizar_libros(self):
        """
        Vuelca al TreeView la lista completa de libros.
        """
        tree_libros.delete(*tree_libros.get_children())
        for l in self.model.libros_todos():
            tree_libros.insert("", "end", text=l["id"],
                               values=(l["titulo"], l["autor"], l["categoria"], l["cantidad"], l["precio"]))

    def buscar_libros(self):
        """
        Filtro client-side por título/autor/categoría.
        """
        filtro = var_buscar_libro.get().strip().lower()
        tree_libros.delete(*tree_libros.get_children())
        for l in self.model.libros_todos():
            if (filtro in l["titulo"].lower()
                or filtro in l["autor"].lower()
                or filtro in l["categoria"].lower()):
                tree_libros.insert("", "end", text=l["id"],
                                   values=(l["titulo"], l["autor"], l["categoria"], l["cantidad"], l["precio"]))

    # -------- VALIDACIONES (LIBROS) --------
    def _validar_libro_obligatorio(self, valor: str, nombre: str):
        if not valor or not valor.strip():
            raise ValueError(f"El campo '{nombre}' es obligatorio.")

    def _validar_libro_campos(self):
        """
        Reglas:
        - TODOS obligatorios EXCEPTO 'ubicación'.
        - año: numérico.
        - cantidad: numérico > 0.
        """
        self._validar_libro_obligatorio(var_titulo.get(), "Título")
        self._validar_libro_obligatorio(var_autor.get(), "Autor")
        self._validar_libro_obligatorio(var_categoria.get(), "Categoría")
        self._validar_libro_obligatorio(var_editorial.get(), "Editorial")
        self._validar_libro_obligatorio(var_anio.get(), "Año")
        self._validar_libro_obligatorio(var_pais.get(), "País")
        self._validar_libro_obligatorio(var_precio.get(), "Precio")

        if not var_anio.get().isdigit():
            raise ValueError("El campo 'Año' debe ser numérico.")

        try:
            cant = int(var_cantidad.get())
            if cant <= 0:
                raise ValueError("La 'Cantidad' debe ser un número mayor que 0.")
        except Exception:
            raise ValueError("La 'Cantidad' debe ser numérica.")

        # Ubicación: opcional (puede quedar vacío)

    @with_transaction(db)
    def guardar_libro(self):
        """
        Crea libro (validando todos los campos salvo 'ubicación').
        """
        try:
            self._validar_libro_campos()
            self.model.libro_crear(
                titulo=var_titulo.get().strip(),
                autor=var_autor.get().strip(),
                categoria=var_categoria.get().strip(),
                editorial=var_editorial.get().strip(),
                anio=int(var_anio.get()),
                pais=var_pais.get().strip(),
                ubicacion=(var_ubicacion.get().strip() or None),
                cantidad=int(var_cantidad.get()),
                precio=var_precio.get().strip()
            )
            self.actualizar_libros()
            messagebox.showinfo("OK", "Libro agregado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def modificar_libro(self):
        """
        Modifica libro seleccionado (con mismas validaciones).
        """
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
                editorial=var_editorial.get().strip(),
                anio=int(var_anio.get()),
                pais=var_pais.get().strip(),
                ubicacion=(var_ubicacion.get().strip() or None),
                cantidad=int(var_cantidad.get()),
                precio=var_precio.get().strip()
            )
            self.actualizar_libros()
            messagebox.showinfo("OK", "Libro modificado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def eliminar_libro(self):
        """
        Elimina el libro seleccionado.
        """
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro.")
        self.model.libro_eliminar(id_libro)
        self.actualizar_libros()
        messagebox.showinfo("OK", "Libro eliminado.")

    # ======================================================================
    # SOCIOS – CRUD
    # ======================================================================
    def actualizar_socios(self):
        """
        Vuelca al TreeView la lista completa de socios.
        """
        tree_socios.delete(*tree_socios.get_children())
        for s in self.model.socios_todos():
            tree_socios.insert("", "end", text=s["id"],
                               values=(s["nombre"], s["dni"], s["telefono"], s["email"]))

    # -------- VALIDACIONES (SOCIOS) --------
    def _validar_socio_campos(self):
        """
        Reglas:
        - TODOS obligatorios: nombre, dni, teléfono, email.
        """
        if not var_socio_nombre.get().strip():
            raise ValueError("El campo 'Nombre' del socio es obligatorio.")
        if not var_socio_dni.get().strip():
            raise ValueError("El campo 'DNI' del socio es obligatorio.")
        if not var_socio_tel.get().strip():
            raise ValueError("El campo 'Teléfono' del socio es obligatorio.")
        if not var_socio_email.get().strip():
            raise ValueError("El campo 'Email' del socio es obligatorio.")

    @with_transaction(db)
    def guardar_socio(self):
        """
        Crea un socio con todos los campos obligatorios.
        """
        try:
            self._validar_socio_campos()
            self.model.socio_crear(
                nombre=var_socio_nombre.get().strip(),
                dni=var_socio_dni.get().strip(),
                telefono=var_socio_tel.get().strip(),
                email=var_socio_email.get().strip()
            )
            self.actualizar_socios()
            messagebox.showinfo("OK", "Socio agregado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def modificar_socio(self):
        """
        Modifica socio seleccionado con validaciones.
        """
        sel = tree_socios.focus()
        if not sel:
            return messagebox.showwarning("Seleccionar", "Seleccione un socio.")
        id_socio = tree_socios.item(sel, "text")
        try:
            self._validar_socio_campos()
            self.model.socio_modificar(
                id_socio,
                nombre=var_socio_nombre.get().strip(),
                dni=var_socio_dni.get().strip(),
                telefono=var_socio_tel.get().strip(),
                email=var_socio_email.get().strip()
            )
            self.actualizar_socios()
            messagebox.showinfo("OK", "Socio modificado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @with_transaction(db)
    def eliminar_socio(self):
        """
        Elimina socio seleccionado.
        """
        sel = tree_socios.focus()
        if not sel:
            return messagebox.showwarning("Seleccionar", "Seleccione un socio.")
        id_socio = tree_socios.item(sel, "text")
        self.model.socio_eliminar(id_socio)
        self.actualizar_socios()
        messagebox.showinfo("OK", "Socio eliminado.")

    # ======================================================================
    # UI PRÉSTAMO – sin cambiar de pestaña
    # ======================================================================
    def ui_prestar(self):
        """
        Abre una ventana modal para elegir socio (con buscador) y registrar el préstamo
        del libro actualmente seleccionado en el TreeView.
        """
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro para prestar.")

        win = Toplevel(ventana_principal)
        win.title("Seleccionar socio para préstamo")
        win.geometry("660x440")

        Label(win, text="Buscar socio (nombre / email / DNI):").pack(anchor="w", padx=10, pady=6)
        q = StringVar()
        ent = Entry(win, textvariable=q, width=44)
        ent.pack(anchor="w", padx=10)
        ent.focus_set()

        tree = ttk.Treeview(win, columns=("nombre","dni","tel","email"), show="headings", height=12)
        for col, txt, w in [("nombre","Nombre",240),("dni","DNI",110),("tel","Teléfono",120),("email","Email",160)]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="w")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def cargar(filtro=""):
            tree.delete(*tree.get_children())
            filtro = filtro.strip().lower()
            for s in self.model.socios_todos():
                if (filtro in (s["nombre"] or "").lower()
                    or filtro in (s["email"] or "").lower()
                    or filtro in (s["dni"] or "").lower()):
                    tree.insert("", "end", text=s["id"],
                                values=(s["nombre"], s["dni"], s["telefono"], s["email"]))

        def on_dbl(_):
            sel = tree.focus()
            if not sel:
                return
            id_socio = tree.item(sel, "text")
            try:
                self.model.prestar(id_libro, id_socio)
                self.actualizar_libros()
                messagebox.showinfo("OK", "Préstamo registrado.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Alta rápida (mínima) → nombre + email
        def alta_rapida():
            nombre = askstring("Alta rápida", "Nombre del socio:")
            email = askstring("Alta rápida", "Email del socio:")
            if not nombre or not email:
                messagebox.showwarning("Validación", "Nombre y Email son obligatorios para alta rápida.")
                return
            try:
                self.model.socio_crear(nombre=nombre.strip(), email=email.strip())
                self.actualizar_socios()
                cargar(q.get())
                messagebox.showinfo("OK", "Socio creado.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Bindings y botones
        q.trace("w", lambda *args: cargar(q.get()))
        tree.bind("<Double-1>", on_dbl)
        Button(win, text="Alta rápida de socio", command=alta_rapida).pack(pady=4)

        cargar()

    # ======================================================================
    # UI DEVOLUCIÓN – listar préstamos activos y elegir uno
    # ======================================================================
    def ui_devolver(self):
        """
        Abre ventana modal con los préstamos activos del libro seleccionado para
        elegir y devolver (sin ingresar ID).
        """
        id_libro = self._libro_seleccionado_id()
        if not id_libro:
            return messagebox.showwarning("Seleccionar", "Seleccione un libro con préstamos activos.")

        prestamos = self.model.prestamos_activos_por_libro(id_libro)
        if not prestamos:
            return messagebox.showinfo("Info", "No hay préstamos activos para ese libro.")

        win = Toplevel(ventana_principal)
        win.title("Devolver préstamo")
        win.geometry("600x380")

        tree = ttk.Treeview(win, columns=("prestamo_id","socio","fecha"), show="headings", height=12)
        for col, txt, w in [("prestamo_id","ID",90),("socio","Socio",290),("fecha","Fecha préstamo",180)]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="w")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for p in prestamos:
            tree.insert("", "end", text=p["id"], values=(p["id"], p["socio"], p["fecha_prestamo"]))

        def devolver_sel():
            sel = tree.focus()
            if not sel:
                return
            pid = tree.item(sel, "text")
            try:
                self.model.devolver(pid)
                self.actualizar_libros()
                messagebox.showinfo("OK", "Devolución registrada.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(win, text="Devolver seleccionado", command=devolver_sel).pack(pady=6)

    # ======================================================================
    # UI CONSULTAS – Libros y Socios
    # ======================================================================
    def ui_consultar_libros(self):
        """
        Ventana de consulta de libros con buscador (título/autor/categoría).
        """
        win = Toplevel(ventana_principal)
        win.title("Consultar Libros")
        win.geometry("780x500")

        Label(win, text="Buscar (Título / Autor / Categoría):").pack(anchor="w", padx=10, pady=6)
        q = StringVar()
        ent = Entry(win, textvariable=q, width=52)
        ent.pack(anchor="w", padx=10)
        ent.focus_set()

        tree = ttk.Treeview(win, columns=("titulo","autor","categoria","cant","precio"), show="headings", height=16)
        for col, txt, w in [
            ("titulo","Título",260),
            ("autor","Autor",220),
            ("categoria","Categoría",160),
            ("cant","Cant.",70),
            ("precio","Precio",90),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="w")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def cargar(f=""):
            tree.delete(*tree.get_children())
            f = f.lower()
            for l in self.model.libros_todos():
                if (f in l["titulo"].lower()
                    or f in l["autor"].lower()
                    or f in l["categoria"].lower()):
                    tree.insert("", "end", text=l["id"],
                                values=(l["titulo"], l["autor"], l["categoria"], l["cantidad"], l["precio"]))

        q.trace("w", lambda *args: cargar(q.get()))
        cargar()

    def ui_consultar_socios(self):
        """
        Ventana de consulta de socios con buscador (nombre/DNI/email).
        """
        win = Toplevel(ventana_principal)
        win.title("Consultar Socios")
        win.geometry("720x470")

        Label(win, text="Buscar (Nombre / DNI / Email):").pack(anchor="w", padx=10, pady=6)
        q = StringVar()
        ent = Entry(win, textvariable=q, width=44)
        ent.pack(anchor="w", padx=10)
        ent.focus_set()

        tree = ttk.Treeview(win, columns=("nombre","dni","tel","email"), show="headings", height=16)
        for col, txt, w in [
            ("nombre","Nombre",260),
            ("dni","DNI",120),
            ("tel","Teléfono",140),
            ("email","Email",200),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="w")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def cargar(f=""):
            tree.delete(*tree.get_children())
            f = f.lower()
            for s in self.model.socios_todos():
                if (f in s["nombre"].lower()
                    or f in (s["dni"] or "").lower()
                    or f in s["email"].lower()):
                    tree.insert("", "end", text=s["id"],
                                values=(s["nombre"], s["dni"], s["telefono"], s["email"]))

        q.trace("w", lambda *args: cargar(q.get()))
        cargar()

    # ======================================================================
    # EXPORT
    # ======================================================================
    def exportar_libros(self):
        """
        Genera export_libros.csv en la carpeta del proyecto.
        """
        path = self.model.exportar_libros_csv()
        messagebox.showinfo("Exportado", f"Se generó: {path}")

    def exportar_socios(self):
        """
        Genera export_socios.csv en la carpeta del proyecto.
        """
        path = self.model.exportar_socios_csv()
        messagebox.showinfo("Exportado", f"Se generó: {path}")











