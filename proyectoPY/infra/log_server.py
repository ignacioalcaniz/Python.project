"""
Servidor de Log
----------------
Este servidor recibe mensajes desde los clientes mediante sockets y los guarda
en un archivo de texto. Cumple con el requisito del punto 5 del módulo avanzado.

Para ejecutarlo:
    python -m proyectoPY.infra.log_server
"""

import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 5000
LOG_FILE = "eventos.log"


def manejar_cliente(conn, addr):
    """Recibe mensajes del cliente y los guarda en archivo."""
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            mensaje = data.decode("utf-8")
            print(f"[LOG] {mensaje}")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(mensaje + "\n")


def iniciar_servidor():
    """Inicia el servidor de logs."""
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVIDOR DE LOG] Escuchando en {HOST}:{PORT}...")
    print(f"Archivo de logs: {LOG_FILE}")

    while True:
        conn, addr = server.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr))
        hilo.start()


if __name__ == "__main__":
    iniciar_servidor()

