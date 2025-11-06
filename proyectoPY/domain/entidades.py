from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LibroDTO:
    id: Optional[int]
    titulo: str
    cantidad: int
    precio: str  

@dataclass
class SocioDTO:
    id: Optional[int]
    nombre: str
    email: str

@dataclass
class PrestamoDTO:
    id: Optional[int]
    libro_id: int
    socio_id: int
    fecha_prestamo: datetime
    fecha_devolucion: Optional[datetime] = None
