import re
from datetime import datetime

def parse_fecha(fecha_str: str, hora_str: str = None) -> str:
    """Convierte DD/MM/AAAA a AAAA-MM-DD HH:MM:SS si es posible."""
    try:
        dt = datetime.strptime(fecha_str, "%d/%m/%Y")
        if hora_str:
            dt = dt.replace(hour=int(hora_str[:2]), minute=int(hora_str[3:5]), second=int(hora_str[6:8]))
        return dt.isoformat(sep=' ', timespec='seconds')
    except:
        return fecha_str

def calcular_dias_estancia(ingreso: str, egreso: str = None) -> int:
    """Calcula días completos entre dos fechas (ignora horas)."""
    fmt = "%Y-%m-%d"
    try:
        if ' ' in ingreso:
            ingreso = ingreso.split()[0]
        if egreso and ' ' in egreso:
            egreso = egreso.split()[0]
        delta = datetime.strptime(egreso, fmt) - datetime.strptime(ingreso, fmt)
        return delta.days if delta.days > 0 else 1
    except:
        return 0
