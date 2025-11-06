"""
Patrón Observador (Publish/Subscribe)
------------------------------------

Este módulo implementa un bus de eventos simple.
Permite que distintas partes de la app reaccionen cuando ocurre algo importante
(libro creado, socio creado, préstamo realizado, etc).
"""


class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_name, callback):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name, payload):
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                callback(payload)


# ====== EVENTOS DEFINIDOS ======
EVT_LIBRO_CREADO = "libro_creado"
EVT_LIBRO_MODIFICADO = "libro_modificado"
EVT_LIBRO_ELIMINADO = "libro_eliminado"

EVT_SOCIO_CREADO = "socio_creado"   # 👈 ESTE ES EL QUE FALTABA

EVT_PRESTAMO_REALIZADO = "prestamo_realizado"
EVT_DEVOLUCION_REGISTRADA = "devolucion_registrada"


# Bus global
event_bus = EventBus()
