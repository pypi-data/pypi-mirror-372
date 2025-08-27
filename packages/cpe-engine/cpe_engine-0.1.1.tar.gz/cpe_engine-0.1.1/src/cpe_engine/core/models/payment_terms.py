"""Modelos para formas de pago y cuotas."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PaymentTerms:
    """Forma de pago del documento."""
    
    # Campos principales - siguiendo convenciones Greenter
    tipo: str  # "Contado" o "Credito"
    monto: Optional[float] = None  # Monto de la forma de pago
    moneda: Optional[str] = None   # Moneda (opcional, usa la del documento)
    
    def __post_init__(self):
        """Validaciones básicas."""
        if not self.tipo or not self.tipo.strip():
            raise ValueError("Tipo de forma de pago es requerido")
            
        # Validar que sea Contado o Credito
        if self.tipo not in ["Contado", "Credito"]:
            raise ValueError(f"Tipo debe ser 'Contado' o 'Credito', recibido: {self.tipo}")
            
        if self.monto is not None and self.monto < 0:
            raise ValueError(f"Monto debe ser mayor o igual a 0, recibido: {self.monto}")


@dataclass
class Cuota:
    """Cuota de pago."""
    
    # Campos principales - siguiendo convenciones Greenter
    monto: float
    fecha_pago: datetime
    moneda: str = "PEN"
    
    def __post_init__(self):
        """Validaciones básicas."""
        if self.monto <= 0:
            raise ValueError(f"Monto de cuota debe ser mayor a 0, recibido: {self.monto}")
            
        if not self.moneda or not self.moneda.strip():
            raise ValueError("Moneda es requerida")