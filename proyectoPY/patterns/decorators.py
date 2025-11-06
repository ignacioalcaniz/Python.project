"""
Módulo decorators
=================

Contiene decoradores reutilizables dentro del proyecto.

Funciones:
- validate_non_empty: Verifica que ciertos campos no estén vacíos antes de ejecutar la acción.
- with_transaction: Garantiza que una operación de base de datos sea atómica.
"""

from functools import wraps
from tkinter import messagebox


def validate_non_empty(*field_names):
    """
    Decorador para verificar que ciertos campos no estén vacíos.

    Ejemplo:
        @validate_non_empty("nombre", "precio")
        def guardar(self):
            ...

    Si algún campo está vacío se muestra una advertencia y no se ejecuta la función.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for field in field_names:
                valor = getattr(self, f"var_{field}", lambda: None)()
                if valor is None or str(valor).strip() == "":
                    messagebox.showwarning(
                        "Campo vacío",
                        f"El campo '{field}' no puede estar vacío."
                    )
                    return
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def with_transaction(db):
    """
    Decorador que garantiza que la operación sobre la base de datos sea atómica.

    Si ocurre un error durante la ejecución, la transacción se revierte
    y se muestra un mensaje de error al usuario.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                with db.atomic():
                    return func(self, *args, **kwargs)
            except Exception as e:
                messagebox.showerror("Error en la operación", str(e))
        return wrapper
    return decorator


