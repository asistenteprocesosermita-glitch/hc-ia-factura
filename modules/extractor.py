import re
from datetime import datetime
from modules.config import *
from modules.models import Paciente, Estancia, EventoFacturable
from modules.utils import parse_fecha, calcular_dias_estancia

class FacturableExtractor:
    def __init__(self, cleaned_text: str):
        self.text = cleaned_text
        self.paciente = None
        self.estancias = []
        self.eventos = []

    def extract_all(self) -> dict:
        self._extract_datos_paciente()
        self._extract_estancias()
        self._extract_procedimientos()
        self._extract_formulas_medicas()
        self._extract_administraciones()
        self._extract_laboratorios()
        self._extract_imagenes()
        self._extract_transfusiones()
        self._extract_cancelaciones()
        return self._to_dict()

    def _extract_datos_paciente(self):
        """Extrae datos demográficos del encabezado."""
        datos = {}
        for pattern, key in [
            (PAT_CC, 'cc'),
            (PAT_NOMBRE, 'nombre'),
            (PAT_FECHA_NAC, 'fecha_nacimiento'),
            (PAT_EDAD, 'edad'),
            (PAT_SEXO, 'sexo'),
            (PAT_EPS, 'eps'),
            (PAT_AFILIADO, 'afiliado'),
            (PAT_RESPONSABLE, 'responsable'),
            (PAT_TEL, 'telefono'),
        ]:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                datos[key] = match.group(1).strip()
        self.paciente = Paciente(**datos)

    def _extract_estancias(self):
        """
        Detecta ingresos y egresos por servicio.
        Se basa en palabras clave y fechas.
        """
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            if 'RECIBO PACIENTE' in line or 'INGRESA A' in line:
                servicio = self._buscar_servicio_en_contexto(line, lines, i)
                fecha = self._buscar_fecha_cercana(line, lines, i)
                if servicio and fecha:
                    self.estancias.append(Estancia(
                        servicio=servicio,
                        ingreso=fecha,
                        egreso=None,
                        dias=0
                    ))
            if 'ENTREGO PACIENTE' in line or 'TRASLADADO' in line or 'ALTA' in line:
                # Asignar fecha de egreso a la última estancia sin egreso
                if self.estancias and self.estancias[-1].egreso is None:
                    fecha = self._buscar_fecha_cercana(line, lines, i)
                    self.estancias[-1].egreso = fecha
                    self.estancias[-1].dias = calcular_dias_estancia(
                        self.estancias[-1].ingreso,
                        fecha
                    )

    def _buscar_servicio_en_contexto(self, line, lines, idx):
        # Buscar en línea actual o anterior
        for offset in [0, -1, -2]:
            target = lines[idx + offset] if 0 <= idx + offset < len(lines) else ""
            m = re.search(PAT_SERVICIO, target, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def _buscar_fecha_cercana(self, line, lines, idx):
        for offset in [0, -1, -2, 1, 2]:
            target = lines[idx + offset] if 0 <= idx + offset < len(lines) else ""
            m = re.search(PAT_FECHA_FOLIO, target, re.IGNORECASE)
            if m:
                return parse_fecha(m.group(1), m.group(2))
        return None

    def _extract_procedimientos(self):
        """Captura procedimientos quirúrgicos y no quirúrgicos."""
        for match in re.finditer(PAT_PROCEDIMIENTO, self.text, re.IGNORECASE):
            desc = match.group(0).strip()
            # Buscar fecha cercana
            fecha = self._buscar_fecha_cercana(desc, self.text.split('\n'), 0)
            self.eventos.append(EventoFacturable(
                tipo='procedimiento',
                fecha=fecha,
                servicio=None,  # se puede inferir por contexto
                descripcion=desc,
                codigo_cups=CUPS.get(desc.split(' ')[0], None),
                cantidad=1,
                estado='realizado',
                folio=None  # se puede extraer de la línea
            ))

    def _extract_formulas_medicas(self):
        """
        Extrae órdenes de la sección "FORMULA MEDICA ESTANDAR" o "ORDENES DE LABORATORIO".
        Usa las tablas presentes en el texto.
        """
        # Buscar tabla de fórmula médica
        fm_sections = re.findall(PAT_FM_TABLA, self.text, re.DOTALL)
        for section in fm_sections:
            lines = section.strip().split('\n')
            for line in lines:
                m = re.match(PAT_FM_CANT, line.strip())
                if m:
                    cantidad = float(m.group(1))
                    descripcion = m.group(2).strip()
                    dosis = m.group(3) if len(m.groups()) > 2 else None
                    via = m.group(4) if len(m.groups()) > 3 else None
                    # Buscar estado (NUEVO, CONTINUAR, SUSPENDIDO, etc.)
                    estado = 'realizado'
                    if 'SUSPENDIDO' in line or 'CANCELADO' in line:
                        estado = 'cancelado'
                    # Si es medicamento, lo registramos como orden (después confirmaremos administración)
                    self.eventos.append(EventoFacturable(
                        tipo='orden_medicamento',
                        fecha=None,  # se buscará en contexto
                        servicio=None,
                        descripcion=descripcion,
                        cantidad=cantidad,
                        dosis=dosis,
                        via=via,
                        estado=estado,
                        folio=None
                    ))

    def _extract_administraciones(self):
        """
        Busca en las notas de enfermería las administraciones confirmadas.
        Cada coincidencia genera un evento facturable de tipo 'medicamento'.
        """
        for match in re.finditer(PAT_ADMIN_MED, self.text, re.IGNORECASE):
            descripcion = match.group(1).strip()
            cantidad = float(match.group(2).replace(',', '.')) if match.group(2) else 1
            unidad = match.group(3) if len(match.groups()) > 2 else ''
            # Buscar fecha en contexto
            start = max(0, match.start() - 200)
            end = min(len(self.text), match.end() + 200)
            contexto = self.text[start:end]
            fecha = self._buscar_fecha_cercana(contexto, contexto.split('\n'), 0)
            self.eventos.append(EventoFacturable(
                tipo='medicamento',
                fecha=fecha,
                servicio='UCI' if 'UCI' in contexto else 'HOSPITALIZACION',
                descripcion=descripcion,
                cantidad=cantidad,
                unidad=unidad,
                estado='realizado',
                folio=None
            ))

    def _extract_transfusiones(self):
        """Identifica transfusiones y sus unidades."""
        for match in re.finditer(PAT_TRANSFUSION, self.text, re.IGNORECASE):
            bloque = match.group(0)
            # Extraer número de unidades
            m_uds = re.search(r'(\d+)\s*(?:UNIDAD(?:ES)?)', bloque, re.IGNORECASE)
            cantidad = int(m_uds.group(1)) if m_uds else 1
            # Tipo de producto
            tipo = 'GRE' if 'GLOBULOS ROJOS' in bloque.upper() else \
                   'PLAQUETAS AFERESIS' if 'AFERESIS' in bloque.upper() else \
                   'PLAQUETAS ESTANDAR' if 'PLAQUETAS' in bloque.upper() else 'OTROS'
            # Buscar fecha
            fecha = self._buscar_fecha_cercana(bloque, self.text.split('\n'), 0)
            self.eventos.append(EventoFacturable(
                tipo='transfusion',
                fecha=fecha,
                servicio=None,
                descripcion=tipo,
                cantidad=cantidad,
                estado='realizado',
                folio=None
            ))

    def _extract_laboratorios(self):
        """Extrae órdenes de laboratorio."""
        for match in re.finditer(PAT_LABORATORIO, self.text, re.IGNORECASE):
            desc = match.group(0)
            # Verificar si está en una línea de "Cantidad Descripción"
            # Buscar hacia atrás en la línea
            inicio_linea = self.text.rfind('\n', 0, match.start()) + 1
            fin_linea = self.text.find('\n', match.start())
            if fin_linea == -1:
                fin_linea = len(self.text)
            linea_completa = self.text[inicio_linea:fin_linea]
            cantidad = 1
            m_cant = re.match(r'^(\d+)\s+', linea_completa)
            if m_cant:
                cantidad = int(m_cant.group(1))
            # Determinar estado
            estado = 'realizado'
            if 'CANCELADO' in linea_completa or 'Cancelado' in linea_completa:
                estado = 'cancelado'
            self.eventos.append(EventoFacturable(
                tipo='laboratorio',
                fecha=self._buscar_fecha_cercana(linea_completa, self.text.split('\n'), 0),
                servicio=None,
                descripcion=desc,
                cantidad=cantidad,
                estado=estado,
                folio=None
            ))

    def _extract_imagenes(self):
        """Extrae órdenes de ayudas diagnósticas por imágenes."""
        for match in re.finditer(PAT_IMAGEN, self.text, re.IGNORECASE):
            desc = match.group(0)
            # Similar a laboratorios
            inicio_linea = self.text.rfind('\n', 0, match.start()) + 1
            fin_linea = self.text.find('\n', match.start())
            if fin_linea == -1:
                fin_linea = len(self.text)
            linea_completa = self.text[inicio_linea:fin_linea]
            cantidad = 1
            m_cant = re.match(r'^(\d+)\s+', linea_completa)
            if m_cant:
                cantidad = int(m_cant.group(1))
            estado = 'realizado'
            if 'CANCELADO' in linea_completa or 'Cancelado' in linea_completa:
                estado = 'cancelado'
            self.eventos.append(EventoFacturable(
                tipo='imagen',
                fecha=self._buscar_fecha_cercana(linea_completa, self.text.split('\n'), 0),
                servicio=None,
                descripcion=desc,
                cantidad=cantidad,
                estado=estado,
                folio=None
            ))

    def _extract_cancelaciones(self):
        """
        Marca como cancelados aquellos eventos que previamente se habían
        registrado como realizados pero luego aparecen cancelados.
        """
        # Este método es opcional si ya se capturó el estado al momento de la extracción.
        pass

    def _to_dict(self):
        return {
            "paciente": self.paciente.to_dict() if self.paciente else {},
            "estancias": [e.to_dict() for e in self.estancias],
            "eventos": [e.to_dict() for e in self.eventos]
        }
