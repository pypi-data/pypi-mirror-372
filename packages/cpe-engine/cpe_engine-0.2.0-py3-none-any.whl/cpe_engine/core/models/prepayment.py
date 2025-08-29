"""Modelo Prepayment para anticipos."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Prepayment:
    """Anticipo o prepago aplicado al documento."""
    
    # Campos principales - siguiendo convenciones Greenter
    tipo_doc_rel: str  # Tipo de documento del anticipo (ej: "01" factura)
    nro_doc_rel: str   # Número del documento (ej: "F001-123")
    total: float       # Monto total del anticipo
    
    def __post_init__(self):
        """Validaciones básicas."""
        if not self.tipo_doc_rel or not self.tipo_doc_rel.strip():
            raise ValueError("Tipo de documento relacionado es requerido")
            
        if not self.nro_doc_rel or not self.nro_doc_rel.strip():
            raise ValueError("Número de documento relacionado es requerido")
            
        if self.total <= 0:
            raise ValueError(f"Total del anticipo debe ser mayor a 0, recibido: {self.total}")