"""
Módulo model
------------

Define los modelos ORM y la clase `BibliotecaModel` responsable de la lógica
de base de datos para la Biblioteca Popular Nelly Llorens.

Responsabilidades:
- Conexión a MySQL.
- Definición de tablas ORM (Libro, Socio, Prestamo).
- CRUD de Libros y Socios.
- Registro de Préstamos y Devoluciones.
- Publicación de eventos (Observer).
"""

import pymysql
pymysql.install_as_MySQLdb()

from peewee import *
from datetime import datetime

# ----------------- CONEXIÓN MYSQL -----------------
db = MySQLDatabase(
    'biblioteca_db',
    user='root',
    password='Secu2015$',
    host='localhost',
    port=3306
)

class BaseModel(Model):
    class Meta:
        database = db

# ----------------- TABLAS -----------------
class Libro(BaseModel):
    id = AutoField()
    titulo = CharField(unique=True)
    autor = CharField()
    categoria = CharField()
    editorial = CharField(null=True)
    anio = IntegerField(null=True)
    pais = CharField(null=True)
    ubicacion = CharField(null=True)
    cantidad = IntegerField(default=0)
    precio = CharField(null=True)

class Socio(BaseModel):
    id = AutoField()
    nombre = CharField()
    dni = CharField(null=True)
    telefono = CharField(null=True)
    email = CharField(unique=True)

class Prestamo(BaseModel):
    id = AutoField()
    libro = ForeignKeyField(Libro, backref="prestamos")
    socio = ForeignKeyField(Socio, backref="prestamos")
    fecha_prestamo = DateTimeField(default=datetime.now)
    fecha_devolucion = DateTimeField(null=True)


# ----------------- OBSERVER (EVENTOS) -----------------
from proyectoPY.patterns.observer import (
    event_bus,
    EVT_LIBRO_CREADO, EVT_LIBRO_MODIFICADO, EVT_LIBRO_ELIMINADO,
    EVT_SOCIO_CREADO,
    EVT_PRESTAMO_REALIZADO, EVT_DEVOLUCION_REGISTRADA
)

# ----------------- LÓGICA -----------------
class BibliotecaModel:
    """
    Maneja toda la lógica de datos de Biblioteca.
    """
    def __init__(self):
        db.connect(reuse_if_open=True)
        db.create_tables([Libro, Socio, Prestamo])

    # ================= LIBROS =================
    def libros_todos(self):
        libros = []
        for l in Libro.select():
            libros.append({
                "id": l.id,
                "titulo": l.titulo,
                "autor": l.autor,
                "categoria": l.categoria,
                "editorial": l.editorial,
                "anio": l.anio,
                "pais": l.pais,
                "ubicacion": l.ubicacion,
                "cantidad": l.cantidad,
                "precio": l.precio
            })
        return libros

    def libro_crear(self, **datos):
        l = Libro.create(**datos)
        event_bus.publish(EVT_LIBRO_CREADO, {"id": l.id, "titulo": l.titulo})
        return l

    def libro_modificar(self, id_libro, **datos):
        l = Libro.get_or_none(Libro.id == id_libro)
        if l:
            for campo, valor in datos.items():
                setattr(l, campo, valor)
            l.save()
            event_bus.publish(EVT_LIBRO_MODIFICADO, {"id": l.id, "titulo": l.titulo})

    def libro_eliminar(self, id_libro):
        l = Libro.get_or_none(Libro.id == id_libro)
        if l:
            titulo = l.titulo
            l.delete_instance()
            event_bus.publish(EVT_LIBRO_ELIMINADO, {"id": id_libro, "titulo": titulo})

    # ================= SOCIOS =================
    def socios_todos(self):
        socios = []
        for s in Socio.select():
            socios.append({
                "id": s.id,
                "nombre": s.nombre,
                "dni": s.dni,
                "telefono": s.telefono,
                "email": s.email
            })
        return socios

    def socio_crear(self, **datos):
        s = Socio.create(**datos)
        event_bus.publish(EVT_SOCIO_CREADO, {"id": s.id, "nombre": s.nombre})
        return s

    def socio_modificar(self, id_socio, **datos):
        s = Socio.get_or_none(Socio.id == id_socio)
        if s:
            for campo, valor in datos.items():
                setattr(s, campo, valor)
            s.save()

    def socio_eliminar(self, id_socio):
        s = Socio.get_or_none(Socio.id == id_socio)
        if s:
            s.delete_instance()

    # ================= PRÉSTAMOS =================
    def prestar(self, id_libro, id_socio):
        l = Libro.get_or_none(Libro.id == id_libro)
        s = Socio.get_or_none(Socio.id == id_socio)

        if not l or not s:
            raise ValueError("Libro o socio inexistente.")
        if l.cantidad <= 0:
            raise ValueError("No hay ejemplares disponibles.")

        l.cantidad -= 1
        l.save()

        p = Prestamo.create(libro=l, socio=s)
        event_bus.publish(EVT_PRESTAMO_REALIZADO, {"libro": l.titulo, "socio": s.nombre, "prestamo_id": p.id})
        return p.id

    def devolver(self, id_prestamo):
        p = Prestamo.get_or_none(Prestamo.id == id_prestamo)
        if not p:
            raise ValueError("Préstamo inexistente.")
        if p.fecha_devolucion:
            raise ValueError("Este préstamo ya fue devuelto.")

        p.fecha_devolucion = datetime.now()
        p.save()

        l = p.libro
        l.cantidad += 1
        l.save()

        event_bus.publish(EVT_DEVOLUCION_REGISTRADA, {"libro": l.titulo, "prestamo_id": p.id})









