"""Modelo Charge para cargos y descuentos."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Charge:
    """Cargo o descuento aplicado a un documento o línea."""
    
    # Campos principales - siguiendo convenciones Greenter
    cod_tipo: str  # Código del tipo de cargo/descuento
    factor: Optional[float] = None  # Factor multiplicador
    monto: Optional[float] = None  # Monto del cargo/descuento
    monto_base: Optional[float] = None  # Base sobre la cual se calcula
    
    def __post_init__(self):
        """Validaciones básicas."""
        if not self.cod_tipo or not self.cod_tipo.strip():
            raise ValueError("Código de tipo es requerido")
            
        # Si no se proporciona monto pero sí factor y base, calcular
        if self.monto is None and self.factor is not None and self.monto_base is not None:
            self.monto = round(self.monto_base * self.factor, 2)