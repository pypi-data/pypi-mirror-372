"""Modelo Address para direcciones de empresa y cliente."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Address:
    """Dirección de empresa o cliente."""
    
    ubigeo: Optional[str] = None  # Código de ubigeo (6 dígitos)
    codigo_pais: Optional[str] = None  # Código de país (PE)
    departamento: Optional[str] = None
    provincia: Optional[str] = None
    distrito: Optional[str] = None
    urbanizacion: Optional[str] = None
    direccion: Optional[str] = None  # Dirección completa
    codigo_local: Optional[str] = None  # Código de local anexo
    
    def __post_init__(self):
        """Validaciones básicas después de inicialización."""
        if self.codigo_pais is None:
            self.codigo_pais = "PE"
            
        # Validar ubigeo si está presente
        if self.ubigeo and len(self.ubigeo) != 6:
            raise ValueError(f"Ubigeo debe tener 6 dígitos, recibido: {self.ubigeo}")
            
        if self.ubigeo and not self.ubigeo.isdigit():
            raise ValueError(f"Ubigeo debe ser numérico, recibido: {self.ubigeo}")