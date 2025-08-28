"""Builder base para generación de XML usando templates Jinja2."""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .filters import CUSTOM_FILTERS


class XmlBuilderError(Exception):
    """Error en la construcción de XML."""
    pass


class XmlBuilder(ABC):
    """Builder base para generar XMLs UBL 2.1."""
    
    def __init__(self):
        """Inicializa el builder con configuración Jinja2."""
        self.template_dir = self._get_template_directory()
        self.jinja_env = self._setup_jinja_environment()
        print(f"[XmlBuilder] Inicializado con templates en: {self.template_dir}")
    
    def _get_template_directory(self) -> str:
        """Obtiene el directorio de templates."""
        # Obtener directorio base del paquete
        current_file = Path(__file__)
        base_dir = current_file.parent.parent.parent  # src/cpe_engine/
        template_dir = base_dir / "templates"
        
        if not template_dir.exists():
            raise XmlBuilderError(f"Directorio de templates no encontrado: {template_dir}")
            
        return str(template_dir)
    
    def _setup_jinja_environment(self) -> Environment:
        """Configura el entorno Jinja2."""
        try:
            env = Environment(
                loader=FileSystemLoader(self.template_dir),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=False
            )
            
            # Registrar filtros personalizados
            env.filters.update(CUSTOM_FILTERS)
            
            print(f"[XmlBuilder] Jinja2 configurado con {len(CUSTOM_FILTERS)} filtros personalizados")
            return env
            
        except Exception as e:
            raise XmlBuilderError(f"Error configurando Jinja2: {e}")
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Obtiene el nombre del template a usar."""
        pass
    
    @abstractmethod
    def prepare_context(self, document) -> dict:
        """Prepara el contexto para el template."""
        pass
    
    def build(self, document) -> str:
        """
        Construye el XML para un documento.
        
        Args:
            document: Documento a procesar (Invoice, Note, etc.)
            
        Returns:
            XML generado como string
            
        Raises:
            XmlBuilderError: Si hay error en la generación
        """
        try:
            print(f"[XmlBuilder] Iniciando construcción XML para: {document.get_nombre()}")
            
            # Obtener template
            template_name = self.get_template_name()
            template = self.jinja_env.get_template(template_name)
            print(f"[XmlBuilder] Template cargado: {template_name}")
            
            # Preparar contexto
            context = self.prepare_context(document)
            print(f"[XmlBuilder] Contexto preparado con {len(context)} variables")
            
            # Generar XML
            xml_content = template.render(context)
            print(f"[XmlBuilder] XML generado: {len(xml_content)} caracteres")
            
            # Validar que se generó contenido
            if not xml_content.strip():
                raise XmlBuilderError("El template generó contenido vacío")
                
            return xml_content
            
        except Exception as e:
            error_msg = f"Error generando XML para {document.get_nombre()}: {e}"
            print(f"[XmlBuilder] ERROR: {error_msg}")
            raise XmlBuilderError(error_msg)
    
    def build_and_save(self, document, output_path: str) -> str:
        """
        Construye el XML y lo guarda en un archivo.
        
        Args:
            document: Documento a procesar
            output_path: Ruta donde guardar el XML
            
        Returns:
            XML generado como string
        """
        xml_content = self.build(document)
        
        try:
            # Crear directorio si no existe
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
                
            print(f"[XmlBuilder] XML guardado en: {output_path}")
            return xml_content
            
        except Exception as e:
            raise XmlBuilderError(f"Error guardando XML en {output_path}: {e}")
    
    def validate_document(self, document) -> bool:
        """
        Valida que el documento tenga los campos requeridos.
        
        Args:
            document: Documento a validar
            
        Returns:
            True si es válido
            
        Raises:
            XmlBuilderError: Si faltan campos requeridos
        """
        required_fields = ['serie', 'correlativo', 'company', 'client', 'details']
        
        for field in required_fields:
            if not hasattr(document, field):
                raise XmlBuilderError(f"Campo requerido faltante: {field}")
                
            value = getattr(document, field)
            if value is None or (isinstance(value, (list, str)) and len(value) == 0):
                raise XmlBuilderError(f"Campo requerido vacío: {field}")
        
        # Validar que tenga al menos un detalle
        if len(document.details) == 0:
            raise XmlBuilderError("Documento debe tener al menos un detalle")
            
        return True