"""Modelo BaseSale - clase base para todos los comprobantes de venta."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .client import Client
from .company import Company
from .payment_terms import PaymentTerms, Cuota
# Imports de catálogos removidos - validaciones están en capa separada (validator/)


@dataclass
class Legend:
    """Leyenda del comprobante."""
    code: str
    value: str


class SaleDetail:
    """Detalle de línea de venta con soporte para alias de compatibilidad."""
    
    def __init__(self,
                 cod_producto: str = None, cod_item: str = None,  # Alias
                 descripcion: str = None, des_item: str = None,   # Alias
                 unidad: str = "NIU",
                 cantidad: float = 0.0,
                 mto_valor_unitario: float = 0.0,
                 mto_precio_unitario: float = 0.0,
                 mto_valor_venta: float = 0.0,
                 igv: float = 0.0,
                 total_impuestos: float = 0.0,
                 tip_afe_igv: int = 10,
                 porcentaje_igv: float = 18.0,
                 mto_precio_unitario_final: float = 0.0,
                 cod_tipo_tributo: str = "1000",
                 # Nuevos campos para compatibilidad con greenter
                 mto_valor_gratuito: float = 0.0,  # Valor referencial para operaciones gratuitas
                 cargos: list = None,              # Lista de Charge (cargos a nivel detalle)
                 descuentos: list = None):         # Lista de Charge (descuentos a nivel detalle)
        
        # Usar alias si se proporciona
        self.cod_producto = cod_producto or cod_item
        self.descripcion = descripcion or des_item
        
        # Soportar ambos nombres para compatibilidad
        self.cod_item = self.cod_producto
        self.des_item = self.descripcion
        self.unidad = unidad
        self.cantidad = cantidad
        self.mto_valor_unitario = mto_valor_unitario
        self.mto_precio_unitario = mto_precio_unitario
        self.mto_valor_venta = mto_valor_venta
        self.igv = igv
        self.total_impuestos = total_impuestos
        self.tip_afe_igv = str(tip_afe_igv)  # Convertir a string
        self.porcentaje_igv = porcentaje_igv
        self.mto_precio_unitario_final = mto_precio_unitario_final
        self.cod_tipo_tributo = cod_tipo_tributo
        
        # Nuevos campos para compatibilidad con greenter
        self.mto_valor_gratuito = mto_valor_gratuito
        self.cargos = cargos or []
        self.descuentos = descuentos or []
        
        # Solo validaciones básicas de negocio
        self._validar_campos_requeridos()
    
    def _validar_campos_requeridos(self):
        """Validar solo campos básicos requeridos (sin cálculos automáticos)."""
        # Validaciones básicas de negocio
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("Descripción del producto es requerida")
            
        if self.cantidad < 0:
            raise ValueError(f"Cantidad no puede ser negativa, recibido: {self.cantidad}")
    
    # Validaciones SUNAT están en validator/ - core es declarativo como greenter
    # def _validar_codigos_sunat(self): -> MoveToDifferentLayer


@dataclass
class BaseSale(ABC):
    """Clase base para todos los comprobantes de venta."""
    
    # Campos obligatorios primero
    serie: str
    correlativo: int
    fecha_emision: datetime
    tipo_doc: str  # "01"=Factura, "03"=Boleta, "07"=Nota Crédito, "08"=Nota Débito
    company: Optional[Company] = None
    client: Optional[Client] = None
    
    # Campos opcionales con default - usando convención Python
    tipo_moneda: str = "PEN"  # Usando snake_case consistente
    details: List[SaleDetail] = field(default_factory=list)
    legends: List[Legend] = field(default_factory=list)
    
    # Totales - DECLARATIVOS como greenter (usuario los proporciona)
    mto_oper_gravadas: float = 0.0  # Operaciones gravadas
    mto_oper_inafectas: float = 0.0  # Operaciones inafectas
    mto_oper_exoneradas: float = 0.0  # Operaciones exoneradas
    mto_oper_exportacion: float = 0.0  # Operaciones exportación
    mto_oper_gratuitas: float = 0.0  # Operaciones gratuitas (NUEVO)
    mto_igv_gratuitas: float = 0.0   # IGV de operaciones gratuitas (NUEVO)
    mto_igv: float = 0.0  # Total IGV
    mto_isc: float = 0.0  # Total ISC
    mto_otros_tributos: float = 0.0  # Otros tributos
    mto_total_tributos: float = 0.0  # Total impuestos
    mto_base_isc: float = 0.0  # Base ISC
    mto_base_otros_tributos: float = 0.0  # Base otros tributos
    mto_impventa: float = 0.0  # Importe total de la venta
    
    # Nuevos campos para compatibilidad con greenter
    forma_pago: Optional[PaymentTerms] = None  # Forma de pago (Contado/Credito)
    cuotas: List[Cuota] = field(default_factory=list)  # Cuotas de pago
    
    def __post_init__(self):
        """Validaciones automáticas después de crear el objeto."""
        # Validar campos obligatorios
        if not self.company:
            raise ValueError("Company es requerido")
        if not self.client:
            raise ValueError("Client es requerido")
            
        print(f"[{self.__class__.__name__}] Comprobante creado: {self.get_nombre()}")
        
        # Validaciones SUNAT están en validator/ - core es declarativo
        # self._validar_documento_sunat() -> MoveToDifferentLayer
        
        # Campos ya están en snake_case - no necesita sincronización
        
        # Greenter es declarativo - NO recalcula totales automáticamente
        # Los totales deben ser proporcionados por el usuario
        # Las series son libres según SUNAT - no hay restricciones específicas
    
    # Validaciones están en validator/ - core es declarativo como greenter
    # def _validar_documento_sunat(self): -> MoveToDifferentLayer

    def get_nombre(self) -> str:
        """Obtiene el nombre completo del comprobante."""
        return f"{self.company.ruc}-{self.tipo_doc}-{self.serie}-{self.correlativo:03d}"
    
    # Greenter es 100% declarativo - NO calcula totales ni crea leyendas automáticamente
    # Usuario debe proporcionar todos los valores y leyendas manualmente
    
    def agregar_detalle(self, detalle: SaleDetail):
        """Agregar un detalle (sin recalcular totales automáticamente)."""
        self.details.append(detalle)
        print(f"[{self.__class__.__name__}] Detalle agregado: {detalle.descripcion} - Cantidad: {detalle.cantidad}")
        # Greenter es declarativo - usuario debe proporcionar totales manualmente
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Debe ser implementado por las clases hijas."""
        pass