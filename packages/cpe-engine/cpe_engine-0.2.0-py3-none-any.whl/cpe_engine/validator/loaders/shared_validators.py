"""
Shared validation functions for common fields across loaders.

Eliminates code duplication between InvoiceLoader and NoteLoader.
"""

from typing import Dict, Any


class SharedValidators:
    """Reusable validation methods for common fields in document loaders."""
    
    @staticmethod
    def validate_company_data(v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate company data structure.
        
        Args:
            v: Company data dictionary
            
        Returns:
            Dict[str, Any]: Validated company data
            
        Raises:
            ValueError: If company data is invalid
        """
        if not isinstance(v, dict):
            raise ValueError('Company debe ser un diccionario')
        
        required_fields = ['ruc', 'razon_social']
        for field in required_fields:
            if field not in v or not v[field]:
                raise ValueError(f'Company.{field} es requerido')
        
        # Validar RUC básico
        ruc = str(v['ruc'])
        if not ruc.isdigit() or len(ruc) != 11:
            raise ValueError('Company.ruc debe tener 11 dígitos')
            
        return v
    
    @staticmethod
    def validate_client_data(v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate client data structure.
        
        Args:
            v: Client data dictionary
            
        Returns:
            Dict[str, Any]: Validated client data
            
        Raises:
            ValueError: If client data is invalid
        """
        if not isinstance(v, dict):
            raise ValueError('Client debe ser un diccionario')
            
        required_fields = ['tipo_doc', 'num_doc', 'razon_social']
        for field in required_fields:
            if field not in v or not v[field]:
                raise ValueError(f'Client.{field} es requerido')
                
        return v
    
    @staticmethod
    def validate_details_list(v: list) -> list:
        """
        Validate details list has at least one item.
        
        Args:
            v: Details list
            
        Returns:
            list: Validated details list
            
        Raises:
            ValueError: If details list is empty
        """
        if not v or len(v) == 0:
            raise ValueError('Debe tener al menos un detalle')
        return v