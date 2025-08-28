"""
DocumentValidator principal - Equivalente a greenter/validator SymfonyValidator.

Validador OPCIONAL y separado del core. Los documentos se pueden crear sin validar,
exactamente como greenter.
"""

from dataclasses import asdict
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, ValidationError as PydanticValidationError

from .loaders import get_loader_for_document


class ValidationError:
    """Error de validación individual."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
    
    def __str__(self) -> str:
        return f"{self.field}: {self.message}"
    
    def __repr__(self) -> str:
        return f"ValidationError(field='{self.field}', message='{self.message}')"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'field': self.field,
            'message': self.message,
            'value': self.value
        }


class DocumentValidator:
    """
    Validador principal de documentos - Equivalente a SymfonyValidator de greenter.
    
    Es completamente OPCIONAL y separado del core. Los documentos pueden crearse
    sin validación, exactamente como en greenter.
    """
    
    def __init__(self, version: str = "2.1"):
        """
        Inicializa el validador.
        
        Args:
            version: Versión UBL (por defecto "2.1")
        """
        self.version = version
        print(f"[DocumentValidator] Inicializado para UBL {version}")
    
    def validate(self, document) -> List[ValidationError]:
        """
        Valida un documento usando catálogos oficiales SUNAT.
        
        Args:
            document: Documento a validar (Invoice, Note, etc.)
            
        Returns:
            Lista de errores de validación (vacía si es válido)
        """
        if document is None:
            return [ValidationError("document", "Documento es requerido")]
        
        document_type = document.__class__.__name__
        
        # Solo mostrar nombre si el documento lo tiene
        doc_name = ""
        if hasattr(document, 'get_nombre'):
            doc_name = f": {document.get_nombre()}"
            
        print(f"[DocumentValidator] Validando {document_type}{doc_name}")
        
        # Buscar loader para el tipo de documento
        loader = get_loader_for_document(document_type, self.version)
        
        if not loader:
            print(f"[DocumentValidator] Sin validaciones para {document_type}")
            return []  # Sin validaciones disponibles
        
        # Ejecutar validación con pydantic
        errors = self._validate_with_loader(document, loader)
        
        # Validar detalles anidados si existen
        if hasattr(document, 'details') and document.details:
            detail_errors = self._validate_details(document.details)
            errors.extend(detail_errors)
        
        if errors:
            print(f"[DocumentValidator] ❌ {len(errors)} errores encontrados")
        else:
            print(f"[DocumentValidator] ✅ Documento válido")
            
        return errors
    
    def _validate_with_loader(self, document, loader) -> List[ValidationError]:
        """Valida documento con un loader específico."""
        try:
            # Obtener modelo pydantic del loader
            validation_model = loader.get_validation_model()
            
            # Convertir dataclass a dict
            if hasattr(document, '__dataclass_fields__'):
                data = asdict(document)
            else:
                data = document.__dict__.copy()
            
            # Limpiar campos especiales que pueden causar problemas
            data = self._clean_data_for_validation(data)
            
            # Validar con pydantic
            validation_model(**data)
            return []  # Sin errores
            
        except PydanticValidationError as e:
            return [
                ValidationError(
                    field='.'.join(str(loc) for loc in error['loc']),
                    message=error['msg'],
                    value=error.get('input')
                )
                for error in e.errors()
            ]
        except Exception as e:
            return [ValidationError("validation", f"Error interno: {str(e)}")]
    
    def _clean_data_for_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia datos para validación pydantic."""
        # Remover campos que pueden ser objetos complejos
        cleaned = data.copy()
        
        # Convertir objetos anidados a dict si es necesario
        for key, value in data.items():
            if hasattr(value, '__dict__'):
                if hasattr(value, '__dataclass_fields__'):
                    cleaned[key] = asdict(value)
                else:
                    cleaned[key] = value.__dict__
            elif isinstance(value, list):
                # Limpiar listas de objetos
                cleaned[key] = [
                    asdict(item) if hasattr(item, '__dataclass_fields__') 
                    else item.__dict__ if hasattr(item, '__dict__') 
                    else item
                    for item in value
                ]
        
        return cleaned
    
    def _validate_details(self, details: List) -> List[ValidationError]:
        """Valida detalles/líneas de documento."""
        errors = []
        
        for i, detail in enumerate(details):
            detail_errors = self.validate(detail)
            # Prefijo para identificar el detalle
            for error in detail_errors:
                error.field = f"details[{i}].{error.field}"
            errors.extend(detail_errors)
        
        return errors
    
    def is_valid(self, document) -> bool:
        """
        Verifica si un documento es válido.
        
        Args:
            document: Documento a validar
            
        Returns:
            True si es válido (sin errores)
        """
        return len(self.validate(document)) == 0
    
    def get_errors_summary(self, errors: List[ValidationError]) -> str:
        """
        Genera resumen legible de errores.
        
        Args:
            errors: Lista de errores
            
        Returns:
            String con resumen de errores
        """
        if not errors:
            return "Sin errores"
        
        summary = f"Se encontraron {len(errors)} errores:\n"
        for error in errors:
            summary += f"  - {error}\n"
        
        return summary.strip()