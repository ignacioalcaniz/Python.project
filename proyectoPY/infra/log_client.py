"""
Cliente de Log
--------------
Envía mensajes al servidor de log mediante sockets.

Se usa desde el patrón observador, en el controlador, para registrar eventos.
"""

import socket

HOST = "127.0.0.1"
PORT = 5000


def send_log(message: str):
    """Envía un mensaje al servidor de logs."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            sock.sendall(message.encode("utf-8"))
    except ConnectionRefusedError:
        # Si el servidor no está corriendo, no rompe el programa.
        pass
