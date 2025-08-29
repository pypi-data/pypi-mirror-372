"""Modelo Note para notas de crédito y débito."""

from dataclasses import dataclass, field
from typing import Optional, List

from .base_sale import BaseSale
from .charge import Charge
from .prepayment import Prepayment


@dataclass
class Note(BaseSale):
    """Nota de Crédito o Débito."""
    
    # Código y descripción del motivo - convención snake_case estándar
    cod_motivo: str = ""  # Código del catálogo 09 (crédito) o 10 (débito)
    des_motivo: str = ""  # Descripción del motivo
    
    # Documento afectado - convención snake_case estándar  
    tip_doc_afectado: str = ""  # Tipo de documento afectado (01=Factura, 03=Boleta)
    num_doc_afectado: str = ""  # Número del documento afectado (Serie-Correlativo)
    
    # Valores específicos de nota - convenciones Greenter
    ubl_version: str = "2.1"
    tipo_doc: str = "07"  # Se setea en __post_init__
    
    # Campos adicionales para compatibilidad con templates
    sum_otros_cargos: float = 0.0
    sum_dscto_global: float = 0.0
    mto_descuentos: float = 0.0
    sum_otros_descuentos: float = 0.0
    total_anticipos: float = 0.0
    valor_venta: float = 0.0  # Valor de venta sin impuestos
    sub_total: float = 0.0    # Subtotal
    
    # Campos adicionales para compatibilidad con greenter
    descuentos: List[Charge] = field(default_factory=list)     # Descuentos a nivel documento
    cargos: List[Charge] = field(default_factory=list)         # Cargos a nivel documento
    mto_cargos: float = 0.0                                    # Total de cargos (declarativo)
    anticipos: List[Prepayment] = field(default_factory=list)  # Anticipos (si aplica en notas)
    
    def __post_init__(self):
        """Inicialización específica de Note."""
        
        # Si no se especifica tipo_doc, es nota de crédito por defecto
        if not self.tipo_doc:
            self.tipo_doc = "07"  # Nota de crédito
        
        # Syncronizar tipo_doc con tipo_doc para compatibilidad con templates
        self.tipo_doc = self.tipo_doc
        
        super().__post_init__()
        
        # Validaciones específicas de nota
        self._validar_nota()
        
    def _validar_nota(self) -> None:
        """Validaciones específicas para notas."""
        if not self.cod_motivo.strip():
            raise ValueError("Código de motivo es requerido")
            
        if not self.des_motivo.strip():
            raise ValueError("Descripción de motivo es requerida")
            
        if not self.tip_doc_afectado.strip():
            raise ValueError("Tipo de documento afectado es requerido")
            
        if not self.num_doc_afectado.strip():
            raise ValueError("Número de documento afectado es requerido")
            
        # Las series son libres según SUNAT: F001, F002, B001, B002, etc. para notas de crédito y 
        # para notas de débito - no hay restricción específica,
        # comienza con F si modifica factura, B si modifica boleta
        # Los motivos vienen de catálogos oficiales 09 y 10 - validación en DocumentValidator
    
    def get_tipo_comprobante_desc(self) -> str:
        """Obtiene descripción del tipo de comprobante."""
        tipos = {
            "07": "Nota de Crédito",
            "08": "Nota de Débito"
        }
        return tipos.get(self.tipo_doc, "Desconocido")
    
    def is_nota_credito(self) -> bool:
        """Determina si es una nota de crédito."""
        return self.tipo_doc == "07"
    
    def is_nota_debito(self) -> bool:
        """Determina si es una nota de débito."""
        return self.tipo_doc == "08"
        
    def set_nota_credito(self) -> None:
        """Configura como nota de crédito."""
        self.tipo_doc = "07"
        
    def set_nota_debito(self) -> None:
        """Configura como nota de débito."""
        self.tipo_doc = "08"
        
    def get_motivo_desc(self) -> str:
        """Obtiene descripción del motivo según el catálogo."""
        if self.is_nota_credito():
            motivos = {
                "01": "Anulación de la operación",
                "02": "Anulación por error en el RUC", 
                "03": "Corrección por error en la descripción",
                "04": "Descuento global",
                "05": "Descuento por ítem",
                "06": "Devolución total",
                "07": "Devolución por ítem",
                "08": "Bonificación",
                "09": "Disminución en el valor",
                "10": "Otros conceptos"
            }
        else:  # Nota de débito
            motivos = {
                "01": "Intereses por mora",
                "02": "Aumento en el valor", 
                "03": "Penalidades/ otros conceptos",
                "10": "Otros conceptos"
            }
        
        return motivos.get(self.cod_motivo, self.des_motivo)
    
    def get_template_name(self) -> str:
        """Retorna el nombre del template para notas."""
        if self.is_nota_credito():
            return "credit_note.xml"
        else:
            return "debit_note.xml"