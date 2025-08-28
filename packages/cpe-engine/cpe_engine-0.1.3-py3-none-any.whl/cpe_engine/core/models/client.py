"""Modelo Client para datos del cliente receptor."""

from dataclasses import dataclass
from typing import Optional

from .address import Address


@dataclass
class Client:
    """Datos del cliente receptor del comprobante."""
    
    num_doc: str  # Número de documento (DNI, RUC, etc.)
    tipo_doc: str  # Tipo de documento (1=DNI, 6=RUC, etc.)
    razon_social: str  # Nombre o razón social
    codigo_pais: str = "PE"
    address: Optional[Address] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    
    def __init__(self, 
                 num_doc: str = None,
                 tipo_doc: str = None,
                 razon_social: str = None,
                 codigo_pais: str = "PE",
                 address: Optional[Address] = None,
                 email: Optional[str] = None,
                 telefono: Optional[str] = None):
        # Usar convención Greenter: numDoc -> num_doc
        self.num_doc = num_doc
        self.tipo_doc = tipo_doc
        self.razon_social = razon_social
        self.codigo_pais = codigo_pais
        self.address = address
        self.email = email
        self.telefono = telefono
        
        self.__post_init__()
    
    def __post_init__(self):
        """Validaciones básicas después de inicialización."""
        # Validar documento según tipo
        if self.tipo_doc == "1":  # DNI
            if not self.num_doc or len(self.num_doc) != 8:
                raise ValueError(f"DNI debe tener 8 dígitos, recibido: {self.num_doc}")
            if not self.num_doc.isdigit():
                raise ValueError(f"DNI debe ser numérico, recibido: {self.num_doc}")
                
        elif self.tipo_doc == "6":  # RUC
            if not self.num_doc or len(self.num_doc) != 11:
                raise ValueError(f"RUC debe tener 11 dígitos, recibido: {self.num_doc}")
            if not self.num_doc.isdigit():
                raise ValueError(f"RUC debe ser numérico, recibido: {self.num_doc}")
        
        # Validar que tenga razón social
        if not self.razon_social.strip():
            raise ValueError("Razón social del cliente es requerida")
            
        print(f"[Client] Cliente creado: {self.razon_social} - {self.get_tipo_doc_desc()}: {self.num_doc}")
    
    def get_tipo_doc_desc(self) -> str:
        """Obtiene descripción del tipo de documento."""
        tipos = {
            "1": "DNI",
            "6": "RUC",
            "4": "Carné de extranjería", 
            "7": "Pasaporte",
            "0": "Otros"
        }
        return tipos.get(self.tipo_doc, "Desconocido")
        
    def is_persona_juridica(self) -> bool:
        """Determina si es persona jurídica (RUC) o natural (DNI)."""
        return self.tipo_doc == "6"