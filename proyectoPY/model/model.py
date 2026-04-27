"""
Modelo principal de la Biblioteca Popular Nelly Llorens.
Usa Peewee + MySQL.
"""

import os
import csv
from datetime import datetime, date, timedelta

from peewee import (
    Model,
    CharField,
    TextField,
    IntegerField,
    BooleanField,
    DateField,
    DateTimeField,
    ForeignKeyField,
    MySQLDatabase,
    fn
)

from proyectoPY.patterns.observer import (
    event_bus,
    EVT_LIBRO_CREADO, EVT_LIBRO_MODIFICADO, EVT_LIBRO_ELIMINADO,
    EVT_SOCIO_CREADO, EVT_PRESTAMO_REALIZADO, EVT_DEVOLUCION_REGISTRADA
)

DB_NAME = os.getenv("DB_NAME", "biblioteca_nelly_llorens")
DB_USER = os.getenv("DB_USER", "biblioteca_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "TuClaveSegura123!")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

db = MySQLDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


class BaseModel(Model):
    class Meta:
        database = db


class UsuarioSistema(BaseModel):
    usuario = CharField(unique=True, max_length=100)
    password = CharField(max_length=255)
    activo = BooleanField(default=True)
    fecha_alta = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "usuarios_sistema"


class LogSistema(BaseModel):
    fecha_hora = DateTimeField(default=datetime.now)
    nombre_persona = CharField(max_length=120)
    usuario_sistema = CharField(max_length=100)
    accion = CharField(max_length=120)
    detalle = TextField(null=True)

    class Meta:
        table_name = "logs_sistema"


class Libro(BaseModel):
    titulo = CharField(max_length=255)
    autor = CharField(max_length=255)
    categoria = CharField(max_length=120)
    subcategoria = CharField(max_length=120, null=True)
    es_infantil = BooleanField(default=False)
    editorial = CharField(max_length=150, null=True)
    anio = IntegerField(null=True)
    pais = CharField(max_length=120, null=True)
    idioma = CharField(max_length=120, null=True)
    isbn = CharField(max_length=80, null=True, unique=True)
    ubicacion = CharField(max_length=120, null=True)
    cantidad = IntegerField(default=1)
    cantidad_paginas = IntegerField(null=True)
    descripcion = TextField(null=True)
    imagen_path = TextField(null=True)
    fecha_alta = DateField(default=date.today)

    class Meta:
        table_name = "libros"


class Socio(BaseModel):
    nombre = CharField(max_length=120)
    apellido = CharField(max_length=120, null=True)
    dni = CharField(max_length=50, unique=True)
    telefono = CharField(max_length=80, null=True)
    email = CharField(max_length=150, null=True)
    direccion = CharField(max_length=255, null=True)
    activo = BooleanField(default=True)
    observaciones = TextField(null=True)
    imagen_path = TextField(null=True)
    fecha_alta = DateField(default=date.today)

    modalidad_cuota = CharField(max_length=30, default="Mensual")
    estado_cuota = CharField(max_length=30, default="Pendiente")
    ultimo_mes_pago = CharField(max_length=30, null=True)
    fecha_ultimo_pago = DateField(null=True)
    observacion_cuota = TextField(null=True)

    class Meta:
        table_name = "socios"


class Prestamo(BaseModel):
    libro = ForeignKeyField(Libro, backref="prestamos", on_delete="CASCADE")
    socio = ForeignKeyField(Socio, backref="prestamos", on_delete="CASCADE")
    fecha_prestamo = DateField(default=date.today)
    fecha_vencimiento = DateField(null=True)
    fecha_devolucion = DateField(null=True)

    class Meta:
        table_name = "prestamos"


def hoy():
    return date.today()


def fecha_a_str(valor):
    if not valor:
        return "-"
    if isinstance(valor, datetime):
        valor = valor.date()
    return valor.strftime("%d/%m/%Y")


def mes_texto(fecha_pago):
    if not fecha_pago:
        return None
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return f"{meses[fecha_pago.month - 1]} {fecha_pago.year}"


class BibliotecaModel:
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([
            UsuarioSistema,
            LogSistema,
            Libro,
            Socio,
            Prestamo
        ])
        self._crear_superusuario_inicial()

    # -----------------------------------------------------
    # LOGIN / LOGS
    # -----------------------------------------------------
    def _crear_superusuario_inicial(self):
        if UsuarioSistema.select().count() == 0:
            UsuarioSistema.create(
                usuario="admin",
                password="admin123",
                activo=True
            )

    def verificar_login(self, usuario, password):
        return UsuarioSistema.get_or_none(
            (UsuarioSistema.usuario == usuario.strip()) &
            (UsuarioSistema.password == password.strip()) &
            (UsuarioSistema.activo == True)
        )

    def usuarios_todos(self):
        return list(UsuarioSistema.select().dicts())

    def registrar_log(self, nombre_persona, usuario_sistema, accion, detalle=None):
        return LogSistema.create(
            nombre_persona=nombre_persona.strip(),
            usuario_sistema=usuario_sistema.strip(),
            accion=accion.strip(),
            detalle=detalle.strip() if detalle else None
        )

    def logs_todos(self, limite=300):
        query = (
            LogSistema
            .select()
            .order_by(LogSistema.fecha_hora.desc())
            .limit(limite)
        )

        salida = []
        for x in query:
            salida.append({
                "id": x.id,
                "fecha_hora": x.fecha_hora.strftime("%d/%m/%Y %H:%M:%S"),
                "nombre_persona": x.nombre_persona,
                "usuario_sistema": x.usuario_sistema,
                "accion": x.accion,
                "detalle": x.detalle or "-"
            })
        return salida

    def logs_filtrados(self, texto="", limite=300):
        texto = (texto or "").strip().lower()
        resultados = []

        for log in self.logs_todos(limite=limite):
            blob = " ".join([
                str(log["fecha_hora"]),
                str(log["nombre_persona"]),
                str(log["usuario_sistema"]),
                str(log["accion"]),
                str(log["detalle"])
            ]).lower()

            if texto and texto not in blob:
                continue

            resultados.append(log)

        return resultados

    # -----------------------------------------------------
    # LIBROS
    # -----------------------------------------------------
    def _libro_disponibles(self, libro_id):
        libro = Libro.get_by_id(libro_id)
        activos = Prestamo.select().where(
            (Prestamo.libro == libro) &
            (Prestamo.fecha_devolucion.is_null(True))
        ).count()
        return max(libro.cantidad - activos, 0)

    def _libro_estado(self, libro_id):
        disponibles = self._libro_disponibles(libro_id)
        return "Disponible" if disponibles > 0 else "Prestado"

    def libro_crear(self, **kwargs):
        isbn = kwargs.get("isbn")
        if isbn:
            existente = Libro.get_or_none(Libro.isbn == isbn)
            if existente:
                raise ValueError("Ya existe un libro con ese ISBN.")

        cantidad_paginas = kwargs.get("cantidad_paginas")
        if cantidad_paginas is not None and int(cantidad_paginas) < 0:
            raise ValueError("La cantidad de páginas no puede ser negativa.")

        libro = Libro.create(**kwargs)
        event_bus.publish(EVT_LIBRO_CREADO, {"id": libro.id, "titulo": libro.titulo})
        return libro

    def libro_modificar(self, id_libro, **kwargs):
        libro = Libro.get_or_none(Libro.id == id_libro)
        if not libro:
            raise ValueError("Libro no encontrado.")

        isbn = kwargs.get("isbn")
        if isbn:
            existente = Libro.get_or_none((Libro.isbn == isbn) & (Libro.id != id_libro))
            if existente:
                raise ValueError("Ya existe otro libro con ese ISBN.")

        cantidad_paginas = kwargs.get("cantidad_paginas")
        if cantidad_paginas is not None and int(cantidad_paginas) < 0:
            raise ValueError("La cantidad de páginas no puede ser negativa.")

        Libro.update(**kwargs).where(Libro.id == id_libro).execute()
        event_bus.publish(EVT_LIBRO_MODIFICADO, {"id": id_libro, "titulo": kwargs.get("titulo", libro.titulo)})
        return True

    def libro_eliminar(self, id_libro):
        libro = Libro.get_or_none(Libro.id == id_libro)
        if not libro:
            raise ValueError("Libro no encontrado.")

        prestamos_asociados = Prestamo.select().where(Prestamo.libro == libro).count()
        if prestamos_asociados > 0:
            raise ValueError("No se puede eliminar el libro porque tiene préstamos registrados.")

        titulo = libro.titulo
        libro.delete_instance()
        event_bus.publish(EVT_LIBRO_ELIMINADO, {"id": id_libro, "titulo": titulo})
        return True

    def libro_por_id(self, id_libro):
        libro = Libro.get_or_none(Libro.id == id_libro)
        if not libro:
            return None

        total_prestamos = Prestamo.select().where(Prestamo.libro == libro).count()

        return {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "categoria": libro.categoria,
            "subcategoria": libro.subcategoria or "",
            "es_infantil": libro.es_infantil,
            "editorial": libro.editorial or "",
            "anio": libro.anio if libro.anio else "",
            "pais": libro.pais or "",
            "idioma": libro.idioma or "",
            "isbn": libro.isbn or "",
            "ubicacion": libro.ubicacion or "",
            "cantidad": libro.cantidad,
            "cantidad_paginas": libro.cantidad_paginas if libro.cantidad_paginas else "",
            "descripcion": libro.descripcion or "",
            "imagen_path": libro.imagen_path or "",
            "fecha_alta": fecha_a_str(libro.fecha_alta),
            "estado": self._libro_estado(libro.id),
            "disponibles": self._libro_disponibles(libro.id),
            "total_prestamos_historicos": total_prestamos
        }

    def libros_todos(self):
        salida = []
        for libro in Libro.select().order_by(Libro.titulo.asc()):
            salida.append({
                "id": libro.id,
                "titulo": libro.titulo,
                "autor": libro.autor,
                "categoria": libro.categoria,
                "subcategoria": libro.subcategoria or "",
                "anio": libro.anio if libro.anio else "",
                "cantidad": libro.cantidad,
                "disponibles": self._libro_disponibles(libro.id),
                "estado": self._libro_estado(libro.id),
                "cantidad_paginas": libro.cantidad_paginas if libro.cantidad_paginas else ""
            })
        return salida

    def libros_filtrados(self, texto="", infantil=None, categoria="", subcategoria="", solo_disponibles=False):
        texto = (texto or "").strip().lower()
        categoria = (categoria or "").strip().lower()
        subcategoria = (subcategoria or "").strip().lower()

        resultados = []
        for libro in Libro.select().order_by(Libro.titulo.asc()):
            blob = " ".join([
                libro.titulo or "",
                libro.autor or "",
                libro.categoria or "",
                libro.subcategoria or "",
                libro.editorial or "",
                libro.pais or "",
                libro.idioma or "",
                libro.isbn or "",
                libro.ubicacion or "",
                str(libro.anio or ""),
                str(libro.cantidad_paginas or "")
            ]).lower()

            if texto and texto not in blob:
                continue

            if infantil is not None and libro.es_infantil != infantil:
                continue

            if categoria and categoria not in (libro.categoria or "").lower():
                continue

            if subcategoria and subcategoria not in (libro.subcategoria or "").lower():
                continue

            disponibles = self._libro_disponibles(libro.id)
            if solo_disponibles and disponibles <= 0:
                continue

            resultados.append({
                "id": libro.id,
                "titulo": libro.titulo,
                "autor": libro.autor,
                "categoria": libro.categoria,
                "subcategoria": libro.subcategoria or "",
                "anio": libro.anio if libro.anio else "",
                "cantidad": libro.cantidad,
                "disponibles": disponibles,
                "estado": self._libro_estado(libro.id),
                "cantidad_paginas": libro.cantidad_paginas if libro.cantidad_paginas else ""
            })

        return resultados

    def prestamos_activos_del_libro(self, id_libro):
        libro = Libro.get_or_none(Libro.id == id_libro)
        if not libro:
            return []

        salida = []
        query = (
            Prestamo
            .select()
            .where((Prestamo.libro == libro) & (Prestamo.fecha_devolucion.is_null(True)))
            .order_by(Prestamo.fecha_prestamo.desc())
        )

        for p in query:
            estado = "Vencido" if p.fecha_vencimiento and p.fecha_vencimiento < hoy() else "Activo"
            salida.append({
                "prestamo_id": p.id,
                "socio": f"{p.socio.nombre} {p.socio.apellido or ''}".strip(),
                "dni": p.socio.dni,
                "fecha_prestamo": fecha_a_str(p.fecha_prestamo),
                "fecha_vencimiento": fecha_a_str(p.fecha_vencimiento),
                "estado": estado
            })
        return salida

    def prestamos_activos_por_libro(self, id_libro):
        libro = Libro.get_or_none(Libro.id == id_libro)
        if not libro:
            return []

        salida = []
        query = (
            Prestamo
            .select()
            .where((Prestamo.libro == libro) & (Prestamo.fecha_devolucion.is_null(True)))
            .order_by(Prestamo.fecha_prestamo.desc())
        )

        for p in query:
            vencido = bool(p.fecha_vencimiento and p.fecha_vencimiento < hoy())
            salida.append({
                "id": p.id,
                "socio": f"{p.socio.nombre} {p.socio.apellido or ''}".strip(),
                "fecha_prestamo": fecha_a_str(p.fecha_prestamo),
                "fecha_vencimiento": fecha_a_str(p.fecha_vencimiento),
                "vencido": vencido
            })
        return salida

    def libro_estadisticas(self, id_libro):
        libro = Libro.get_or_none(Libro.id == id_libro)
        if not libro:
            return None

        total_prestamos = Prestamo.select().where(Prestamo.libro == libro).count()
        activos = Prestamo.select().where(
            (Prestamo.libro == libro) & (Prestamo.fecha_devolucion.is_null(True))
        ).count()
        devueltos = Prestamo.select().where(
            (Prestamo.libro == libro) & (Prestamo.fecha_devolucion.is_null(False))
        ).count()

        socios_frecuentes = []
        query = (
            Prestamo
            .select(
                Socio.nombre,
                Socio.apellido,
                fn.COUNT(Prestamo.id).alias("cantidad")
            )
            .join(Socio)
            .where(Prestamo.libro == libro)
            .group_by(Socio.id)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(10)
        )

        for x in query:
            socios_frecuentes.append({
                "socio": f"{x.socio.nombre} {x.socio.apellido or ''}".strip(),
                "cantidad": x.cantidad
            })

        return {
            "libro": libro.titulo,
            "total_prestamos": total_prestamos,
            "prestamos_activos": activos,
            "prestamos_devueltos": devueltos,
            "socios_frecuentes": socios_frecuentes
        }

    # -----------------------------------------------------
    # SOCIOS
    # -----------------------------------------------------
    def socio_crear(self, **kwargs):
        dni = kwargs.get("dni")
        if dni:
            existente = Socio.get_or_none(Socio.dni == dni)
            if existente:
                raise ValueError("Ya existe un socio con ese DNI.")

        socio = Socio.create(**kwargs)
        event_bus.publish(EVT_SOCIO_CREADO, {"id": socio.id, "nombre": socio.nombre})
        return socio

    def socio_modificar(self, id_socio, **kwargs):
        socio = Socio.get_or_none(Socio.id == id_socio)
        if not socio:
            raise ValueError("Socio no encontrado.")

        dni = kwargs.get("dni")
        if dni:
            existente = Socio.get_or_none((Socio.dni == dni) & (Socio.id != id_socio))
            if existente:
                raise ValueError("Ya existe otro socio con ese DNI.")

        Socio.update(**kwargs).where(Socio.id == id_socio).execute()
        return True

    def socio_eliminar(self, id_socio):
        socio = Socio.get_or_none(Socio.id == id_socio)
        if not socio:
            raise ValueError("Socio no encontrado.")

        prestamos_asociados = Prestamo.select().where(Prestamo.socio == socio).count()
        if prestamos_asociados > 0:
            raise ValueError("No se puede eliminar el socio porque tiene préstamos registrados.")

        socio.delete_instance()
        return True

    def socio_por_id(self, id_socio):
        socio = Socio.get_or_none(Socio.id == id_socio)
        if not socio:
            return None

        activos = Prestamo.select().where(
            (Prestamo.socio == socio) & (Prestamo.fecha_devolucion.is_null(True))
        ).count()

        historicos = Prestamo.select().where(Prestamo.socio == socio).count()

        return {
            "id": socio.id,
            "nombre": socio.nombre,
            "apellido": socio.apellido or "",
            "dni": socio.dni,
            "telefono": socio.telefono or "",
            "email": socio.email or "",
            "direccion": socio.direccion or "",
            "activo": socio.activo,
            "observaciones": socio.observaciones or "",
            "imagen_path": socio.imagen_path or "",
            "fecha_alta": fecha_a_str(socio.fecha_alta),
            "prestamos_activos": activos,
            "prestamos_historicos": historicos,
            "modalidad_cuota": socio.modalidad_cuota,
            "estado_cuota": socio.estado_cuota,
            "ultimo_mes_pago": socio.ultimo_mes_pago or "",
            "fecha_ultimo_pago": fecha_a_str(socio.fecha_ultimo_pago),
            "observacion_cuota": socio.observacion_cuota or ""
        }

    def socios_todos(self):
        salida = []
        for socio in Socio.select().order_by(Socio.nombre.asc()):
            activos = Prestamo.select().where(
                (Prestamo.socio == socio) & (Prestamo.fecha_devolucion.is_null(True))
            ).count()

            salida.append({
                "id": socio.id,
                "nombre": f"{socio.nombre} {socio.apellido or ''}".strip(),
                "dni": socio.dni,
                "telefono": socio.telefono or "",
                "email": socio.email or "",
                "direccion": socio.direccion or "",
                "activo": socio.activo,
                "prestamos_activos": activos,
                "estado_cuota": socio.estado_cuota,
                "ultimo_mes_pago": socio.ultimo_mes_pago or ""
            })
        return salida

    def socios_filtrados(self, texto=""):
        texto = (texto or "").strip().lower()
        salida = []

        for socio in Socio.select().order_by(Socio.nombre.asc()):
            blob = " ".join([
                socio.nombre or "",
                socio.apellido or "",
                socio.dni or "",
                socio.telefono or "",
                socio.email or "",
                socio.direccion or "",
                socio.estado_cuota or "",
                socio.ultimo_mes_pago or "",
                socio.modalidad_cuota or ""
            ]).lower()

            if texto and texto not in blob:
                continue

            activos = Prestamo.select().where(
                (Prestamo.socio == socio) & (Prestamo.fecha_devolucion.is_null(True))
            ).count()

            salida.append({
                "id": socio.id,
                "nombre": f"{socio.nombre} {socio.apellido or ''}".strip(),
                "dni": socio.dni,
                "telefono": socio.telefono or "",
                "email": socio.email or "",
                "direccion": socio.direccion or "",
                "activo": socio.activo,
                "prestamos_activos": activos,
                "estado_cuota": socio.estado_cuota,
                "ultimo_mes_pago": socio.ultimo_mes_pago or ""
            })

        return salida

    def historial_socio(self, id_socio):
        socio = Socio.get_or_none(Socio.id == id_socio)
        if not socio:
            return []

        salida = []
        query = (
            Prestamo
            .select()
            .where(Prestamo.socio == socio)
            .order_by(Prestamo.fecha_prestamo.desc())
        )

        for p in query:
            if p.fecha_devolucion:
                estado = "Devuelto"
            elif p.fecha_vencimiento and p.fecha_vencimiento < hoy():
                estado = "Vencido"
            else:
                estado = "Activo"

            salida.append({
                "prestamo_id": p.id,
                "libro": p.libro.titulo,
                "categoria": p.libro.categoria,
                "subcategoria": p.libro.subcategoria or "",
                "fecha_prestamo": fecha_a_str(p.fecha_prestamo),
                "fecha_vencimiento": fecha_a_str(p.fecha_vencimiento),
                "fecha_devolucion": fecha_a_str(p.fecha_devolucion),
                "estado": estado
            })
        return salida

    def socio_estadisticas(self, id_socio):
        socio = Socio.get_or_none(Socio.id == id_socio)
        if not socio:
            return None

        total_prestamos = Prestamo.select().where(Prestamo.socio == socio).count()
        activos = Prestamo.select().where(
            (Prestamo.socio == socio) & (Prestamo.fecha_devolucion.is_null(True))
        ).count()

        categoria_favorita = None
        cat_q = (
            Prestamo
            .select(Libro.categoria, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Libro)
            .where(Prestamo.socio == socio)
            .group_by(Libro.categoria)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(1)
        )
        for x in cat_q:
            categoria_favorita = x.libro.categoria

        subcategoria_favorita = None
        subcat_q = (
            Prestamo
            .select(Libro.subcategoria, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Libro)
            .where((Prestamo.socio == socio) & (Libro.subcategoria.is_null(False)))
            .group_by(Libro.subcategoria)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(1)
        )
        for x in subcat_q:
            subcategoria_favorita = x.libro.subcategoria

        preferencia_infantil = None
        infantil_q = (
            Prestamo
            .select(Libro.es_infantil, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Libro)
            .where(Prestamo.socio == socio)
            .group_by(Libro.es_infantil)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(1)
        )
        for x in infantil_q:
            preferencia_infantil = "Infantil" if x.libro.es_infantil else "General"

        libros = []
        libros_q = (
            Prestamo
            .select(Libro.titulo, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Libro)
            .where(Prestamo.socio == socio)
            .group_by(Libro.id)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(10)
        )
        for x in libros_q:
            libros.append({
                "titulo": x.libro.titulo,
                "cantidad": x.cantidad
            })

        return {
            "socio": f"{socio.nombre} {socio.apellido or ''}".strip(),
            "total_prestamos": total_prestamos,
            "prestamos_activos": activos,
            "categoria_favorita": categoria_favorita,
            "subcategoria_favorita": subcategoria_favorita,
            "preferencia_infantil": preferencia_infantil,
            "libros": libros
        }

    # -----------------------------------------------------
    # PRÉSTAMOS
    # -----------------------------------------------------
    def prestar(self, id_libro, id_socio, fecha_vencimiento=None):
        libro = Libro.get_or_none(Libro.id == id_libro)
        socio = Socio.get_or_none(Socio.id == id_socio)

        if not libro:
            raise ValueError("Libro no encontrado.")
        if not socio:
            raise ValueError("Socio no encontrado.")
        if not socio.activo:
            raise ValueError("El socio está inactivo.")
        if self._libro_disponibles(id_libro) <= 0:
            raise ValueError("No hay ejemplares disponibles para prestar.")

        prestamo = Prestamo.create(
            libro=libro,
            socio=socio,
            fecha_prestamo=hoy(),
            fecha_vencimiento=fecha_vencimiento
        )

        event_bus.publish(EVT_PRESTAMO_REALIZADO, {
            "id": prestamo.id,
            "libro": libro.titulo,
            "socio": socio.nombre
        })
        return prestamo

    def devolver(self, id_prestamo):
        prestamo = Prestamo.get_or_none(Prestamo.id == id_prestamo)
        if not prestamo:
            raise ValueError("Préstamo no encontrado.")

        if prestamo.fecha_devolucion:
            raise ValueError("Ese préstamo ya fue devuelto.")

        prestamo.fecha_devolucion = hoy()
        prestamo.save()

        event_bus.publish(EVT_DEVOLUCION_REGISTRADA, {
            "id": prestamo.id,
            "libro": prestamo.libro.titulo,
            "socio": prestamo.socio.nombre
        })
        return prestamo

    def renovar_prestamo(self, id_prestamo, dias=7):
        prestamo = Prestamo.get_or_none(Prestamo.id == id_prestamo)
        if not prestamo:
            raise ValueError("Préstamo no encontrado.")

        if prestamo.fecha_devolucion:
            raise ValueError("No se puede renovar un préstamo ya devuelto.")

        base = prestamo.fecha_vencimiento or hoy()
        if base < hoy():
            base = hoy()

        prestamo.fecha_vencimiento = base + timedelta(days=int(dias))
        prestamo.save()
        return prestamo

    def prestamos_filtrados(self, texto="", solo_activos=False):
        texto = (texto or "").strip().lower()
        salida = []

        query = Prestamo.select().order_by(Prestamo.fecha_prestamo.desc())

        for p in query:
            if p.fecha_devolucion:
                estado = "Devuelto"
            elif p.fecha_vencimiento and p.fecha_vencimiento < hoy():
                estado = "Vencido"
            else:
                estado = "Activo"

            if solo_activos and estado == "Devuelto":
                continue

            blob = " ".join([
                p.libro.titulo or "",
                p.libro.categoria or "",
                p.libro.subcategoria or "",
                p.socio.nombre or "",
                p.socio.apellido or "",
                p.socio.dni or "",
                estado
            ]).lower()

            if texto and texto not in blob:
                continue

            salida.append({
                "id": p.id,
                "libro": p.libro.titulo,
                "categoria": p.libro.categoria,
                "subcategoria": p.libro.subcategoria or "",
                "socio": f"{p.socio.nombre} {p.socio.apellido or ''}".strip(),
                "dni": p.socio.dni,
                "fecha_prestamo": fecha_a_str(p.fecha_prestamo),
                "fecha_vencimiento": fecha_a_str(p.fecha_vencimiento),
                "fecha_devolucion": fecha_a_str(p.fecha_devolucion),
                "estado": estado
            })

        return salida

    # -----------------------------------------------------
    # ESTADÍSTICAS
    # -----------------------------------------------------
    def resumen_dashboard(self):
        total_libros = Libro.select().count()
        total_socios = Socio.select().count()

        prestamos_activos = Prestamo.select().where(Prestamo.fecha_devolucion.is_null(True)).count()
        prestamos_vencidos = Prestamo.select().where(
            (Prestamo.fecha_devolucion.is_null(True)) &
            (Prestamo.fecha_vencimiento.is_null(False)) &
            (Prestamo.fecha_vencimiento < hoy())
        ).count()
        prestamos_historicos = Prestamo.select().count()

        return {
            "total_libros": total_libros,
            "total_socios": total_socios,
            "prestamos_activos": prestamos_activos,
            "prestamos_vencidos": prestamos_vencidos,
            "prestamos_historicos": prestamos_historicos
        }

    def top_socios(self, limite=10):
        salida = []
        query = (
            Prestamo
            .select(Socio.nombre, Socio.apellido, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Socio)
            .group_by(Socio.id)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(limite)
        )
        for x in query:
            salida.append({
                "nombre": f"{x.socio.nombre} {x.socio.apellido or ''}".strip(),
                "cantidad": x.cantidad
            })
        return salida

    def top_categorias(self, limite=10):
        salida = []
        query = (
            Prestamo
            .select(Libro.categoria, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Libro)
            .group_by(Libro.categoria)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(limite)
        )
        for x in query:
            salida.append({
                "categoria": x.libro.categoria,
                "cantidad": x.cantidad
            })
        return salida

    def top_subcategorias(self, limite=10):
        salida = []
        query = (
            Prestamo
            .select(Libro.subcategoria, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Libro)
            .where(Libro.subcategoria.is_null(False))
            .group_by(Libro.subcategoria)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(limite)
        )
        for x in query:
            salida.append({
                "subcategoria": x.libro.subcategoria,
                "cantidad": x.cantidad
            })
        return salida

    def top_libros(self, limite=10):
        salida = []
        query = (
            Prestamo
            .select(Libro.titulo, fn.COUNT(Prestamo.id).alias("cantidad"))
            .join(Libro)
            .group_by(Libro.id)
            .order_by(fn.COUNT(Prestamo.id).desc())
            .limit(limite)
        )
        for x in query:
            salida.append({
                "titulo": x.libro.titulo,
                "cantidad": x.cantidad
            })
        return salida

    # -----------------------------------------------------
    # EXPORT / BACKUPS
    # -----------------------------------------------------
    def _asegurar_backups_dir(self):
        carpeta = os.path.join(os.getcwd(), "backups")
        os.makedirs(carpeta, exist_ok=True)
        return carpeta

    def exportar_libros_csv(self):
        carpeta = self._asegurar_backups_dir()
        path = os.path.join(carpeta, "libros_export.csv")

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "titulo", "autor", "categoria", "subcategoria", "infantil",
                "editorial", "anio", "pais", "idioma", "isbn", "ubicacion",
                "cantidad", "cantidad_paginas", "descripcion", "imagen_path",
                "fecha_alta", "estado", "disponibles"
            ])

            for l in self.libros_todos():
                libro = self.libro_por_id(l["id"])
                writer.writerow([
                    libro["id"], libro["titulo"], libro["autor"], libro["categoria"],
                    libro["subcategoria"], "Sí" if libro["es_infantil"] else "No",
                    libro["editorial"], libro["anio"], libro["pais"], libro["idioma"],
                    libro["isbn"], libro["ubicacion"], libro["cantidad"],
                    libro["cantidad_paginas"], libro["descripcion"], libro["imagen_path"],
                    libro["fecha_alta"], libro["estado"], libro["disponibles"]
                ])
        return path

    def exportar_socios_csv(self):
        carpeta = self._asegurar_backups_dir()
        path = os.path.join(carpeta, "socios_export.csv")

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "nombre", "apellido", "dni", "telefono", "email",
                "direccion", "activo", "observaciones", "imagen_path",
                "fecha_alta", "prestamos_activos", "prestamos_historicos",
                "modalidad_cuota", "estado_cuota", "ultimo_mes_pago",
                "fecha_ultimo_pago", "observacion_cuota"
            ])

            for s in self.socios_todos():
                socio = self.socio_por_id(s["id"])
                writer.writerow([
                    socio["id"], socio["nombre"], socio["apellido"], socio["dni"],
                    socio["telefono"], socio["email"], socio["direccion"],
                    "Sí" if socio["activo"] else "No", socio["observaciones"],
                    socio["imagen_path"], socio["fecha_alta"], socio["prestamos_activos"],
                    socio["prestamos_historicos"], socio["modalidad_cuota"],
                    socio["estado_cuota"], socio["ultimo_mes_pago"],
                    socio["fecha_ultimo_pago"], socio["observacion_cuota"]
                ])
        return path

    def exportar_prestamos_csv(self):
        carpeta = self._asegurar_backups_dir()
        path = os.path.join(carpeta, "prestamos_export.csv")

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "libro", "categoria", "subcategoria", "socio", "dni",
                "fecha_prestamo", "fecha_vencimiento", "fecha_devolucion", "estado"
            ])

            for p in self.prestamos_filtrados():
                writer.writerow([
                    p["id"], p["libro"], p["categoria"], p["subcategoria"],
                    p["socio"], p["dni"], p["fecha_prestamo"], p["fecha_vencimiento"],
                    p["fecha_devolucion"], p["estado"]
                ])
        return path

    def backup_total_csv(self):
        return {
            "libros": self.exportar_libros_csv(),
            "socios": self.exportar_socios_csv(),
            "prestamos": self.exportar_prestamos_csv()
        }








