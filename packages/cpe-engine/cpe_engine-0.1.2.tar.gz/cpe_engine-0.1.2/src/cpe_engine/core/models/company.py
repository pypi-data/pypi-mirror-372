"""Modelo Company para datos de la empresa emisora."""

from dataclasses import dataclass
from typing import Optional

from .address import Address


@dataclass
class Company:
    """Datos de la empresa emisora del comprobante."""
    
    ruc: str  # RUC de 11 dígitos
    tipo_doc: str = "6"  # Tipo de documento de identidad (6 = RUC)
    nombre_comercial: Optional[str] = None
    razon_social: str = ""
    codigo_pais: str = "PE"
    address: Optional[Address] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones básicas después de inicialización."""
        # Validar RUC
        if not self.ruc or len(self.ruc) != 11:
            raise ValueError(f"RUC debe tener 11 dígitos, recibido: {self.ruc}")
            
        if not self.ruc.isdigit():
            raise ValueError(f"RUC debe ser numérico, recibido: {self.ruc}")
            
        # Validar que tenga razón social
        if not self.razon_social.strip():
            raise ValueError("Razón social es requerida")
            
        print(f"[Company] Empresa creada: {self.razon_social} - RUC: {self.ruc}")