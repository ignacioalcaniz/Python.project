"""
Módulo model
------------

Este módulo define la clase ProductoModel y el modelo ORM Producto 
para la aplicación "Vivero La Place Stock".

Responsabilidades del modelo:
- Manejar la conexión con la base de datos (SQLite).
- Definir la estructura de la tabla de productos mediante Peewee ORM.
- Proveer métodos CRUD (Crear, Leer, Actualizar, Eliminar) para los productos.
"""

from peewee import *

# Conexión a la base SQLite
db = SqliteDatabase("viverolaplace.db")


class BaseModel(Model):
    """Clase base para todos los modelos (permite compartir la DB)."""
    class Meta:
        database = db


class Producto(BaseModel):
    """
    Modelo ORM para la tabla 'productos'.

    Campos:
        id (int): Identificador único del producto.
        nombre (str): Nombre del producto.
        cantidad (int): Cantidad en stock.
        precio (str): Precio del producto.
    """
    id = AutoField()
    nombre = CharField(unique=True)
    cantidad = IntegerField(default=0)
    precio = CharField()


class ProductoModel:
    """
    Clase adaptadora entre el ORM (Peewee) y el controlador.

    Métodos:
        obtener_productos(): Devuelve todos los productos como lista de tuplas.
        insertar_producto(nombre, cantidad, precio): Inserta un nuevo producto.
        eliminar_producto(id_producto): Elimina un producto por su ID.
        modificar_producto(id_producto, nombre, cantidad, precio): Modifica un producto existente.
    """

    def __init__(self):
        """Inicializa la base de datos y crea la tabla si no existe."""
        db.connect()
        db.create_tables([Producto])

    def obtener_productos(self):
        """Obtiene todos los productos de la base de datos."""
        try:
            return [(p.id, p.nombre, p.cantidad, p.precio) for p in Producto.select()]
        except Exception as e:
            print(f"[ERROR] al obtener productos: {e}")
            return []

    def insertar_producto(self, nombre, cantidad, precio):
        """Inserta un nuevo producto en la base de datos."""
        try:
            Producto.create(nombre=nombre, cantidad=cantidad, precio=precio)
        except Exception as e:
            print(f"[ERROR] al insertar producto: {e}")

    def eliminar_producto(self, id_producto):
        """Elimina un producto por su ID."""
        try:
            prod = Producto.get_or_none(Producto.id == id_producto)
            if prod:
                prod.delete_instance()
        except Exception as e:
            print(f"[ERROR] al eliminar producto: {e}")

    def modificar_producto(self, id_producto, nombre, cantidad, precio):
        """Modifica un producto existente en la base de datos."""
        try:
            prod = Producto.get_or_none(Producto.id == id_producto)
            if prod:
                prod.nombre = nombre
                prod.cantidad = cantidad
                prod.precio = precio
                prod.save()
        except Exception as e:
            print(f"[ERROR] al modificar producto: {e}")


