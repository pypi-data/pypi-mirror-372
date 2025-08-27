"""Modelo Invoice para facturas y boletas."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from .base_sale import BaseSale
from .charge import Charge
from .prepayment import Prepayment
from .detraction import Detraction


@dataclass
class Invoice(BaseSale):
    """Factura o Boleta (Invoice 2.1 UBL)."""
    
    # Usando convenciones de Greenter
    ubl_version: str = "2.1"
    tipo_operacion: str = "0101"  # Venta interna por defecto
    tipo_doc: str = "01"  # Se setea en __post_init__
    
    # Fecha de vencimiento
    fec_vencimiento: Optional[datetime] = None
    
    # Descuentos globales
    sum_dscto_global: float = 0.0
    mto_descuentos: float = 0.0
    sum_otros_descuentos: float = 0.0
    sum_otros_cargos: float = 0.0
    
    # Anticipos y total de anticipos
    total_anticipos: float = 0.0
    
    # Valores adicionales
    valor_venta: float = 0.0  # Valor de venta sin impuestos
    sub_total: float = 0.0    # Subtotal
    
    # Observaciones
    observacion: Optional[str] = None
    
    # Nuevos campos para compatibilidad con greenter
    descuentos: List[Charge] = field(default_factory=list)  # Descuentos a nivel documento
    cargos: List[Charge] = field(default_factory=list)      # Cargos a nivel documento
    mto_cargos: float = 0.0                                 # Total de cargos (declarativo)
    anticipos: List[Prepayment] = field(default_factory=list)  # Anticipos/prepagos
    total_anticipos: float = 0.0                            # Total de anticipos (declarativo)
    detraccion: Optional[Detraction] = None                 # Detracción (si aplica)
    
    def __post_init__(self):
        """Inicialización específica de Invoice."""
        # Si no se especifica tipo_doc, determinar por tipo de cliente
        if not self.tipo_doc:
            if self.client and self.client.is_persona_juridica():
                self.tipo_doc = "01"  # Factura
            else:
                self.tipo_doc = "03"  # Boleta
        
        super().__post_init__()
        
        # Las series son libres según SUNAT: F001, F002, F003, etc. para facturas
        # B001, B002, B003, etc. para boletas - no hay restricción específica
    
    def get_tipo_comprobante_desc(self) -> str:
        """Obtiene descripción del tipo de comprobante."""
        tipos = {
            "01": "Factura",
            "03": "Boleta"
        }
        return tipos.get(self.tipo_doc, "Desconocido")
    
    def is_factura(self) -> bool:
        """Determina si es una factura."""
        return self.tipo_doc == "01"
    
    def is_boleta(self) -> bool:
        """Determina si es una boleta."""
        return self.tipo_doc == "03"
    
    def set_factura(self) -> None:
        """Configura como factura."""
        self.tipo_doc = "01"
        if not self.serie.startswith("F"):
            print("[Invoice] Cambiando a factura - considere usar serie que comience con F")
            
    def set_boleta(self) -> None:
        """Configura como boleta."""
        self.tipo_doc = "03"
        if not self.serie.startswith("B"):
            print("[Invoice] Cambiando a boleta - considere usar serie que comience con B")
    
    def get_template_name(self) -> str:
        """Retorna el nombre del template para facturas/boletas."""
        return "invoice.xml"