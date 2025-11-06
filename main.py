"""
Punto de entrada de la aplicación
Biblioteca Popular Nelly Llorens
"""

from proyectoPY.controller.controller import BibliotecaController
from proyectoPY.view.view import ventana_principal

if __name__ == "__main__":
    app = BibliotecaController()
    ventana_principal.mainloop()

