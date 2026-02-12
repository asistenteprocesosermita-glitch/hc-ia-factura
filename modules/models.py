from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class Paciente:
    cc: Optional[str] = None
    nombre: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    edad: Optional[int] = None
    sexo: Optional[str] = None
    eps: Optional[str] = None
    plan: Optional[str] = None
    afiliado: Optional[str] = None
    responsable: Optional[str] = None
    parentesco: Optional[str] = None
    telefono: Optional[str] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Estancia:
    servicio: str
    ingreso: str
    egreso: Optional[str] = None
    dias: int = 0
    folio_ingreso: Optional[int] = None
    folio_egreso: Optional[int] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class EventoFacturable:
    tipo: str            # estancia, procedimiento, medicamento, laboratorio, imagen, transfusion, interconsulta
    fecha: Optional[str]
    hora: Optional[str] = None
    servicio: Optional[str] = None
    descripcion: str
    codigo_cups: Optional[str] = None
    cantidad: float = 1.0
    unidad: Optional[str] = None      # mg, ml, amp, etc.
    via: Optional[str] = None
    estado: str = "realizado"        # realizado, cancelado, suspendido, en_proceso
    folio: Optional[int] = None

    def to_dict(self):
        return asdict(self)
