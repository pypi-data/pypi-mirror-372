"""
Validador de documentos separado del core (como greenter/validator).

El DocumentValidator es OPCIONAL y separado del core, exactamente como greenter.
Los builders y modelos NO usan validacion automatica.

Uso:
    from cpe_engine.validator import DocumentValidator
    
    validator = DocumentValidator()
    errors = validator.validate(mi_factura)
    
    if errors:
        print("Errores encontrados:", errors)
    else:
        # Proceder con XML, firma, envio...
        result = send_invoice(...)
"""

from .document_validator import DocumentValidator, ValidationError

__all__ = ['DocumentValidator', 'ValidationError']