"""
Sistema de loaders para validación - Equivalente a greenter/validator loaders.

Cada loader define las reglas de validación para un tipo de documento específico
usando pydantic models.
"""

from typing import Optional
from .base_loader import BaseLoader
from .invoice_loader import InvoiceLoader
from .note_loader import NoteLoader  
from .sale_detail_loader import SaleDetailLoader


# Registry de loaders disponibles
LOADERS = {
    'Invoice': InvoiceLoader,
    'Note': NoteLoader,
    'SaleDetail': SaleDetailLoader,
}


def get_loader_for_document(document_type: str, version: str = "2.1") -> Optional[BaseLoader]:
    """
    Obtiene loader para un tipo de documento específico.
    
    Args:
        document_type: Nombre de la clase del documento (Invoice, Note, etc.)
        version: Versión UBL (actualmente solo 2.1)
        
    Returns:
        Instancia del loader apropiado o None si no hay validaciones
    """
    loader_class = LOADERS.get(document_type)
    
    if not loader_class:
        return None
        
    return loader_class()


__all__ = [
    'BaseLoader',
    'InvoiceLoader', 
    'NoteLoader',
    'SaleDetailLoader',
    'get_loader_for_document',
]