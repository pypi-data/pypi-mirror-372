"""
BaseLoader - Equivalente a LoaderMetadataInterface de greenter.

Define la interfaz base para todos los loaders de validación.
"""

from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel


class BaseLoader(ABC):
    """
    Loader base para validación de documentos.
    
    Equivalente a LoaderMetadataInterface de greenter, pero usando pydantic
    en lugar de Symfony constraints.
    """
    
    @abstractmethod
    def get_validation_model(self) -> Type[BaseModel]:
        """
        Retorna el modelo pydantic que define las validaciones.
        
        Returns:
            Clase BaseModel con las validaciones definidas
        """
        pass