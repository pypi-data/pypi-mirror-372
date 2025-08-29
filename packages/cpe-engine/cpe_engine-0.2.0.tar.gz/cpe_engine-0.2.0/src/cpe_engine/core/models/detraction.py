"""Modelo Detraction para detracciones."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Detraction:
    """Detracción aplicada al documento."""
    
    # Campos principales - siguiendo convenciones Greenter (todos opcionales)
    percent: Optional[float] = None        # Porcentaje de la detracción
    mount: Optional[float] = None          # Monto de la detracción
    cta_banco: Optional[str] = None        # Cuenta bancaria
    cod_medio_pago: Optional[str] = None   # Código de medio de pago
    cod_bien_detraccion: Optional[str] = None  # Código del bien sujeto a detracción (Catálogo 54)
    value_ref: Optional[float] = None      # Valor referencial (para transporte terrestre)
    
    def __post_init__(self):
        """Validaciones básicas."""
        # Si se proporciona porcentaje, debe ser válido
        if self.percent is not None and (self.percent <= 0 or self.percent > 100):
            raise ValueError(f"Porcentaje de detracción debe estar entre 0 y 100, recibido: {self.percent}")
            
        # Si se proporciona monto, debe ser positivo
        if self.mount is not None and self.mount < 0:
            raise ValueError(f"Monto de detracción debe ser mayor o igual a 0, recibido: {self.mount}")