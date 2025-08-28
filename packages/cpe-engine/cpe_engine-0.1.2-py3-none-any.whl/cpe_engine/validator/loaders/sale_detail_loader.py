"""
SaleDetailLoader - Validaciones para SaleDetail basadas en greenter/validator SaleDetailLoader.

Define validaciones para los detalles/líneas de documentos usando catálogos oficiales.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .base_loader import BaseLoader
from ...catalogs import (
    UNIDADES_MEDIDA_CODES,
    CODIGOS_AFECTACION_IGV_CODES,
    validar_unidad_medida,
    validar_afectacion_igv,
)


class SaleDetailValidationModel(BaseModel):
    """
    Modelo pydantic para validación de SaleDetail.
    
    Equivalente a las validaciones en greenter/validator/Loader/SaleDetailLoader.php
    pero usando catálogos oficiales SUNAT.
    """
    
    # Campos básicos requeridos
    unidad: str = Field(..., description="Unidad de medida del catálogo 03")
    des_item: str = Field(..., min_length=1, max_length=250, description="Descripción del producto")
    cantidad: float = Field(..., gt=0, description="Cantidad debe ser mayor a 0")
    
    # Códigos de productos (opcionales pero con límites)
    cod_item: Optional[str] = Field(None, max_length=30, description="Código interno del producto")
    
    # Valores monetarios requeridos
    mto_valor_unitario: float = Field(..., ge=0, description="Valor unitario sin impuestos")
    mto_precio_unitario: float = Field(..., ge=0, description="Precio unitario con impuestos")
    mto_valor_venta: float = Field(..., ge=0, description="Valor total de la línea")
    
    # IGV y afectación (requeridos)
    tip_afe_igv: str = Field(..., description="Código de afectación IGV del catálogo 07")
    porcentaje_igv: float = Field(..., ge=0, le=100, description="Porcentaje de IGV")
    igv: float = Field(..., ge=0, description="Monto de IGV")
    total_impuestos: float = Field(..., ge=0, description="Total de impuestos de la línea")
    
    @field_validator('unidad')
    @classmethod
    def validate_unit(cls, v):
        """Validar unidad de medida contra catálogo oficial 03."""
        if not validar_unidad_medida(v):
            available = ', '.join(list(UNIDADES_MEDIDA_CODES)[:10]) + '...'
            raise ValueError(f'Unidad de medida inválida: {v}. Disponibles: {available}')
        return v
    
    @field_validator('tip_afe_igv')
    @classmethod
    def validate_igv_affection(cls, v):
        """Validar afectación IGV contra catálogo oficial 07."""
        if not validar_afectacion_igv(v):
            available = ', '.join(list(CODIGOS_AFECTACION_IGV_CODES)[:10]) + '...'
            raise ValueError(f'Código de afectación IGV inválido: {v}. Disponibles: {available}')
        return v
    
    @field_validator('des_item')
    @classmethod
    def validate_description(cls, v):
        """Validar descripción no vacía."""
        if not v or not v.strip():
            raise ValueError('Descripción no puede estar vacía')
        return v.strip()
    
    model_config = ConfigDict(extra="allow")


class SaleDetailLoader(BaseLoader):
    """
    Loader para validación de SaleDetail.
    
    Equivalente a greenter/validator/Loader/SaleDetailLoader.php
    """
    
    def get_validation_model(self):
        """Retorna modelo de validación para SaleDetail."""
        return SaleDetailValidationModel