"""
InvoiceLoader - Validaciones para Invoice basadas en greenter/validator InvoiceLoader.

Define validaciones usando catálogos oficiales SUNAT y pydantic.
"""

from datetime import datetime
from typing import Literal, List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .base_loader import BaseLoader
from .shared_validators import SharedValidators
from ...catalogs import (
    TIPOS_DOCUMENTO_CODES,
    MONEDAS_CODES, 
    TIPOS_OPERACION_CODES,
    validar_tipo_documento,
    validar_moneda,
    validar_tipo_operacion,
)


class InvoiceValidationModel(BaseModel):
    """
    Modelo pydantic para validación de Invoice.
    
    Equivalente a las validaciones en greenter/validator/Loader/v21/InvoiceLoader.php
    pero usando catálogos oficiales SUNAT.
    """
    
    # Campos básicos requeridos (equivalente a Assert\NotBlank, Assert\NotNull)
    tipo_doc: Literal['01', '03'] = Field(..., description="Solo facturas (01) y boletas (03)")
    serie: str = Field(..., min_length=1, max_length=4, description="Serie del documento")  
    correlativo: int = Field(..., ge=1, le=99999999, description="Correlativo 1-99999999")
    fecha_emision: datetime = Field(..., description="Fecha de emisión requerida")
    
    # Validación con catálogos oficiales 
    tipo_moneda: str = Field(..., description="Código de moneda del catálogo 02")
    tipo_operacion: str = Field(..., description="Tipo de operación del catálogo 17")
    
    # Totales requeridos (greenter es declarativo)
    mto_oper_gravadas: float = Field(..., ge=0, description="Monto operaciones gravadas")
    mto_oper_inafectas: float = Field(..., ge=0, description="Monto operaciones inafectas")  
    mto_oper_exoneradas: float = Field(..., ge=0, description="Monto operaciones exoneradas")
    mto_impventa: float = Field(..., ge=0, description="Monto total de la venta")
    
    # Objetos anidados (validación automática de pydantic)
    company: Dict[str, Any] = Field(..., description="Datos de empresa")
    client: Dict[str, Any] = Field(..., description="Datos de cliente")
    details: List[Dict[str, Any]] = Field(..., min_length=1, description="Al menos un detalle")
    
    # Campos opcionales
    legends: Optional[List[Dict[str, Any]]] = None
    forma_pago: Optional[Dict[str, Any]] = None
    cuotas: Optional[List[Dict[str, Any]]] = None
    anticipos: Optional[List[Dict[str, Any]]] = None
    detraccion: Optional[Dict[str, Any]] = None
    cargos: Optional[List[Dict[str, Any]]] = None
    descuentos: Optional[List[Dict[str, Any]]] = None
    
    @field_validator('tipo_moneda')
    @classmethod
    def validate_currency(cls, v):
        """Validar moneda contra catálogo oficial 02."""
        if not validar_moneda(v):
            available = ', '.join(list(MONEDAS_CODES)[:10]) + '...'
            raise ValueError(f'Código de moneda inválido: {v}. Disponibles: {available}')
        return v
    
    @field_validator('tipo_operacion')
    @classmethod
    def validate_operation_type(cls, v):
        """Validar tipo de operación contra catálogo oficial 17."""
        if not validar_tipo_operacion(v):
            available = ', '.join(list(TIPOS_OPERACION_CODES)[:10]) + '...'
            raise ValueError(f'Tipo de operación inválido: {v}. Disponibles: {available}')
        return v
    
    @field_validator('company')
    @classmethod
    def validate_company(cls, v):
        """Validar datos básicos de empresa."""
        return SharedValidators.validate_company_data(v)
    
    @field_validator('client')
    @classmethod
    def validate_client(cls, v):
        """Validar datos básicos de cliente."""
        return SharedValidators.validate_client_data(v)
    
    @field_validator('details')
    @classmethod
    def validate_details(cls, v):
        """Validar que hay al menos un detalle."""
        return SharedValidators.validate_details_list(v)

    model_config = ConfigDict(extra="allow")


class InvoiceLoader(BaseLoader):
    """
    Loader para validación de Invoice.
    
    Equivalente a greenter/validator/Loader/v21/InvoiceLoader.php
    """
    
    def get_validation_model(self):
        """Retorna modelo de validación para Invoice."""
        return InvoiceValidationModel