"""
NoteLoader - Validaciones para Note basadas en greenter/validator NoteLoader.

Define validaciones para notas de crédito y débito usando catálogos oficiales.
"""

from datetime import datetime
from typing import Literal, List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .base_loader import BaseLoader
from .shared_validators import SharedValidators
from ...catalogs import (
    MONEDAS_CODES,
    TIPOS_OPERACION_CODES,  
    validar_moneda,
    validar_tipo_operacion,
    validar_nota_credito,
    validar_nota_debito,
)


class NoteValidationModel(BaseModel):
    """
    Modelo pydantic para validación de Note.
    
    Equivalente a las validaciones en greenter/validator/Loader/NoteLoader.php
    pero usando catálogos oficiales SUNAT.
    """
    
    # Campos básicos requeridos
    tipo_doc: Literal['07', '08'] = Field(..., description="Solo notas de crédito (07) y débito (08)")
    serie: str = Field(..., min_length=1, max_length=4, description="Serie del documento")
    correlativo: int = Field(..., ge=1, le=99999999, description="Correlativo 1-99999999")
    fecha_emision: datetime = Field(..., description="Fecha de emisión requerida")
    
    # Validación con catálogos oficiales
    tipo_moneda: str = Field(..., description="Código de moneda del catálogo 02")
    tipo_operacion: Optional[str] = Field(None, description="Tipo de operación del catálogo 17")
    
    # Campos específicos de notas (requeridos)
    tip_doc_afectado: str = Field(..., min_length=1, description="Tipo de documento afectado")
    num_doc_afectado: str = Field(..., min_length=1, description="Número de documento afectado")
    cod_motivo: str = Field(..., min_length=1, description="Código de motivo")
    des_motivo: str = Field(..., min_length=1, description="Descripción del motivo")
    
    # Totales requeridos (greenter es declarativo)
    mto_oper_gravadas: float = Field(..., ge=0, description="Monto operaciones gravadas")
    mto_oper_inafectas: float = Field(..., ge=0, description="Monto operaciones inafectas")
    mto_oper_exoneradas: float = Field(..., ge=0, description="Monto operaciones exoneradas")
    mto_total_tributos: float = Field(..., ge=0, description="Total de tributos/impuestos")
    mto_impventa: float = Field(..., ge=0, description="Monto total")
    
    # Objetos anidados (validación automática)
    company: Dict[str, Any] = Field(..., description="Datos de empresa")
    client: Dict[str, Any] = Field(..., description="Datos de cliente")
    details: List[Dict[str, Any]] = Field(..., min_length=1, description="Al menos un detalle")
    
    # Campos opcionales
    legends: Optional[List[Dict[str, Any]]] = None
    
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
        if v and not validar_tipo_operacion(v):
            available = ', '.join(list(TIPOS_OPERACION_CODES)[:10]) + '...'
            raise ValueError(f'Tipo de operación inválido: {v}. Disponibles: {available}')
        return v
    
    @field_validator('num_doc_afectado')
    @classmethod
    def validate_affected_document(cls, v):
        """Validar formato del documento afectado."""
        if not v or not v.strip():
            raise ValueError('Número de documento afectado es requerido')
        
        # Validar formato Serie-Correlativo
        if '-' not in v:
            raise ValueError('Formato inválido para documento afectado (debe ser Serie-Correlativo)')
        
        parts = v.split('-')
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            raise ValueError('Formato inválido para documento afectado (debe ser Serie-Correlativo)')
            
        return v.strip()
    
    @field_validator('cod_motivo')
    @classmethod
    def validate_motive_code(cls, v, info):
        """Validar código de motivo según catálogos oficiales 09 y 10."""
        if not v or not v.strip():
            raise ValueError('Código de motivo es requerido')
        
        # Obtener tipo de documento para validar motivo apropiado
        documento_tipo = info.data.get('tipo_doc') if info.data else None
        
        if documento_tipo == '07':  # Nota de crédito
            if not validar_nota_credito(v):
                raise ValueError(f'Código de motivo inválido para nota de crédito: {v}')
        elif documento_tipo == '08':  # Nota de débito
            if not validar_nota_debito(v):
                raise ValueError(f'Código de motivo inválido para nota de débito: {v}')
        
        return v.strip()
    
    @field_validator('des_motivo')
    @classmethod
    def validate_motive_description(cls, v):
        """Validar descripción del motivo."""
        if not v or not v.strip():
            raise ValueError('Descripción del motivo es requerida')
        return v.strip()
    
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
    
    @field_validator('mto_impventa')
    @classmethod
    def validate_total_amount(cls, v):
        """Validar que el total sea mayor a 0."""
        if v <= 0:
            raise ValueError('Total de nota debe ser mayor a 0')
        return v
    
    model_config = ConfigDict(extra="allow")


class NoteLoader(BaseLoader):
    """
    Loader para validación de Note.
    
    Equivalente a greenter/validator/Loader/NoteLoader.php
    """
    
    def get_validation_model(self):
        """Retorna modelo de validación para Note."""
        return NoteValidationModel